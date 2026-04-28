from __future__ import annotations
import uuid
from pathlib import Path
from typing import List, Optional

import aiofiles
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
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


@router.post("/api/upload", response_class=HTMLResponse)
async def api_upload(
    request:  Request,
    files:    List[UploadFile] = File(...),
    album_id: Optional[str]   = Form(None),
    db:       Session          = Depends(get_db),
):
    admin = require_admin(request)
    if not admin:
        return HTMLResponse("<div class='form-error'>Unauthorized</div>", status_code=401)

    album_id_int = int(album_id) if album_id and album_id.strip().isdigit() else None
    orig_dir = Path(settings.originals_path)
    orig_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for uf in files:
        if not uf.filename:
            continue
        media_type = get_media_type(uf.filename)
        ext        = Path(uf.filename).suffix.lower()
        unique     = uuid.uuid4().hex
        orig_path  = orig_dir / f"{unique}{ext}"

        content = await uf.read()
        async with aiofiles.open(str(orig_path), "wb") as fh:
            await fh.write(content)

        media = Media(
            original_filename  = uf.filename,
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
        results.append({"filename": uf.filename, "media_id": media.id, "job_id": job_id})

    return templates.TemplateResponse(request, "admin/_upload_results.html", {
        "results": results,
    })
