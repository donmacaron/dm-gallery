"""
Reconvert Router
Queues all existing media for re-conversion.
Useful when changing output format (e.g. WebP → original format).
"""
from __future__ import annotations
import uuid

from fastapi import APIRouter, Depends, Request
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

router = APIRouter(tags=["admin-reconvert"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


@router.post("/reconvert-all", response_class=HTMLResponse)
async def reconvert_all(
    request:    Request,
    media_type: str     = "photo",   # photo | all
    db:         Session = Depends(get_db),
):
    """
    Reset and re-queue all photos (or all media) for conversion.
    Old web/thumb files are deleted by the pipeline before creating new ones.
    """
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)

    q = db.query(Media)
    if media_type == "photo":
        q = q.filter(Media.media_type.in_(["photo", "gif"]))

    items = q.all()
    queued = 0

    for media in items:
        if not media.original_path:
            continue   # skip items without an original on disk

        # Reset DB state
        media.conversion_status = "pending"
        media.conversion_error  = None
        # web_path and thumb_path will be updated by the pipeline after it
        # deletes the old files and creates new ones

        # Create a job record
        job_id = uuid.uuid4().hex
        job = Job(
            id          = job_id,
            job_type    = "conversion",
            status      = "pending",
            target_id   = media.id,
            target_type = "media",
            total_items = 1,
            done_items  = 0,
            progress    = 0,
        )
        db.add(job)
        job_runner.submit(convert_media_bg, media.id, job_id)
        queued += 1

    db.commit()

    return templates.TemplateResponse(request, "admin/reconvert_result.html", {
        "admin":  admin,
        "site_title": settings.site_title,
        "active": "cleanup",
        "queued": queued,
        "media_type": media_type,
    })
