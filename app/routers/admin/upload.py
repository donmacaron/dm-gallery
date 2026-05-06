"""Upload Router - single-file endpoint for sequential JS upload queue."""
from __future__ import annotations
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
    from app.models.album import Album
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
    """
    admin = require_admin(request)
    if not admin:
        return JSONResponse({"status": "error", "message": "Unauthorized"}, status_code=401)

    if not file.filename:
        return JSONResponse({"status": "error", "message": "No file"})

    album_id_int = int(album_id) if album_id and album_id.strip().isdigit() else None
    orig_dir = Path(settings.originals_path)
    orig_dir.mkdir(parents=True, exist_ok=True)

    media_type = get_media_type(file.filename)
    ext        = Path(file.filename).suffix.lower()
    unique     = uuid.uuid4().hex
    orig_path  = orig_dir / f"{unique}{ext}"

    content = await file.read()
    async with aiofiles.open(str(orig_path), "wb") as fh:
        await fh.write(content)

    media = Media(
        original_filename  = file.filename,
        slug               = uuid.uuid4().hex[:16],
        media_type         = media_type,
        album_id           = album_id_int,
        original_path      = str(orig_path),
        file_size_original = len(content),
        conversion_status  = "pending",
        sort_order         = 0,
    )
    db.add(media)
    db.flush()

    # Insert into junction table if album assigned
    if album_id_int:
        db.execute(
            text("INSERT INTO album_media (album_id, media_id, sort_order) VALUES (:a, :m, 0)"),
            {"a": album_id_int, "m": media.id},
        )

    job_id = uuid.uuid4().hex
    job = Job(
        id=job_id, job_type="conversion", status="pending",
        target_id=media.id, target_type="media",
        total_items=1, done_items=0, progress=0,
    )
    db.add(job)
    db.commit()
    db.refresh(media)

    job_runner.submit(convert_media_bg, media.id, job_id)

    return JSONResponse({
        "status":     "queued",
        "filename":   file.filename,
        "media_id":   media.id,
        "job_id":     job_id,
        "media_type": media_type,
    })
