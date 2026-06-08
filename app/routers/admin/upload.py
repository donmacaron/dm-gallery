"""Upload Router - single-file endpoint for sequential JS upload queue."""
from __future__ import annotations
import shutil
import uuid
from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.config import get_settings
from app.database import get_db
from app.models.album import Album
from app.models.job import Job
from app.models.media import Media
from app.services import job_runner
from app.services.conversion_pipeline import convert_media_bg
from app.services.image_processor import get_media_type

router = APIRouter(tags=["admin-upload"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(
    request:  Request,
    album_id: Optional[int] = None,
    db:       Session       = Depends(get_db),
):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    albums = db.query(Album).order_by(Album.title).all()
    return templates.TemplateResponse(request, "admin/media/upload.html", {
        "admin":             admin,
        "site_title":        settings.site_title,
        "active":            "media",
        "albums":            albums,
        "preselected_album": album_id,
    })


@router.post("/api/upload/single", response_class=JSONResponse)
async def api_upload_single(
    request:  Request,
    file:     UploadFile      = File(...),
    album_id: Optional[str]   = Form(None),
    db:       Session          = Depends(get_db),
):
    """
    Upload ONE file at a time.
    The frontend queues files and calls this endpoint sequentially.
    Returns JSON so the JS progress handler can update the UI.
    Includes comprehensive error handling with structured error codes.
    """
    try:
        # ── Authentication ──────────────────────────────────────
        admin = require_admin(request)
        if not admin:
            return JSONResponse(
                {"status": "error", "code": "UNAUTHORIZED", "message": "Session expired. Please login again."},
                status_code=401,
            )

        if not file.filename:
            return JSONResponse(
                {"status": "error", "code": "NO_FILE", "message": "No file selected."},
                status_code=400,
            )

        # ── Validate file type ──────────────────────────────────
        media_type = get_media_type(file.filename)
        if not media_type:
            return JSONResponse(
                {
                    "status": "error",
                    "code": "INVALID_FILE_TYPE",
                    "message": f"File type not supported. Use JPG, PNG, WEBP, HEIC, GIF, MP4, MOV, MP3, or FLAC.",
                    "filename": file.filename,
                },
                status_code=400,
            )

        # ── Validate album if provided ──────────────────────────
        album_id_int = None
        if album_id and album_id.strip().isdigit():
            album_id_int = int(album_id)
            album = db.query(Album).filter(Album.id == album_id_int).first()
            if not album:
                return JSONResponse(
                    {
                        "status": "error",
                        "code": "ALBUM_NOT_FOUND",
                        "message": f"Album ID {album_id_int} does not exist.",
                    },
                    status_code=404,
                )

        # ── Setup directories ──────────────────────────────────
        orig_dir = Path(settings.originals_path)
        try:
            orig_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return JSONResponse(
                {
                    "status": "error",
                    "code": "CANNOT_CREATE_DIRECTORY",
                    "message": "Server storage error. Contact administrator.",
                },
                status_code=507,
            )

        # ── Check available disk space ──────────────────────────
        stat = shutil.disk_usage(str(orig_dir))
        if stat.free < 100 * 1024 * 1024:  # Less than 100MB free
            return JSONResponse(
                {
                    "status": "error",
                    "code": "DISK_FULL",
                    "message": "Server storage is almost full. Please try again later.",
                },
                status_code=507,
            )

        # ── Write file with error handling ──────────────────────
        ext = Path(file.filename).suffix.lower()
        unique = uuid.uuid4().hex
        orig_path = orig_dir / f"{unique}{ext}"

        file_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        max_size = 5 * 1024 * 1024 * 1024  # 5GB per file

        try:
            async with aiofiles.open(str(orig_path), "wb") as fh:
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    file_size += len(chunk)

                    # Check if file exceeds max size
                    if file_size > max_size:
                        await fh.flush()
                        try:
                            orig_path.unlink()
                        except:
                            pass
                        return JSONResponse(
                            {
                                "status": "error",
                                "code": "FILE_TOO_LARGE",
                                "message": f"File exceeds 5GB limit. Size: {file_size / (1024**3):.1f}GB",
                                "filename": file.filename,
                            },
                            status_code=413,
                        )

                    await fh.write(chunk)

        except OSError as e:
            try:
                orig_path.unlink()
            except:
                pass
            return JSONResponse(
                {
                    "status": "error",
                    "code": "FILE_WRITE_ERROR",
                    "message": "Failed to save file. Check disk permissions.",
                },
                status_code=507,
            )

        # ── Create media record ──────────────────────────────────
        try:
            media = Media(
                original_filename=file.filename,
                slug=uuid.uuid4().hex[:16],
                media_type=media_type,
                album_id=album_id_int,
                original_path=str(orig_path),
                file_size_original=file_size,
                conversion_status="pending",
                sort_order=0,
            )
            db.add(media)
            db.flush()

            # Insert into junction table if album assigned
            if album_id_int:
                db.execute(
                    text("INSERT INTO album_media (album_id, media_id, sort_order) VALUES (:a, :m, 0)"),
                    {"a": album_id_int, "m": media.id},
                )

            # Create conversion job
            job_id = uuid.uuid4().hex
            job = Job(
                id=job_id,
                job_type="conversion",
                status="pending",
                target_id=media.id,
                target_type="media",
                total_items=1,
                done_items=0,
                progress=0,
            )
            db.add(job)
            db.commit()
            db.refresh(media)

            job_runner.submit(convert_media_bg, media.id, job_id)

        except Exception as e:
            try:
                orig_path.unlink()
            except:
                pass
            db.rollback()
            return JSONResponse(
                {
                    "status": "error",
                    "code": "DATABASE_ERROR",
                    "message": "Failed to record file. Please try again.",
                },
                status_code=500,
            )

        return JSONResponse(
            {
                "status": "queued",
                "filename": file.filename,
                "media_id": media.id,
                "job_id": job_id,
                "media_type": media_type,
            }
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            {
                "status": "error",
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again.",
            },
            status_code=500,
        )
