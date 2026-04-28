from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models.job import Job
from app.models.media import Media

router = APIRouter(tags=["admin-jobs"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/api/jobs/{job_id}/fragment", response_class=HTMLResponse)
async def job_fragment(job_id: str, request: Request, db: Session = Depends(get_db)):
    job   = db.query(Job).filter(Job.id == job_id).first()
    media = None
    if job and job.target_type == "media" and job.target_id:
        media = db.query(Media).filter(Media.id == job.target_id).first()

    return templates.TemplateResponse(request, "admin/_job_fragment.html", {
        "job":   job,
        "media": media,
    })


@router.get("/api/media/{media_id}/status")
async def media_status(media_id: int, db: Session = Depends(get_db)):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        return JSONResponse({"status": "not_found"}, status_code=404)
    return {
        "id":                media.id,
        "conversion_status": media.conversion_status,
        "thumb_path":        media.thumb_path,
        "web_path":          media.web_path,
        "error":             media.conversion_error,
    }


@router.get("/api/jobs/active", response_class=HTMLResponse)
async def active_jobs_fragment(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request)
    if not admin:
        return HTMLResponse("")

    jobs = (
        db.query(Job)
        .filter(Job.status.in_(["pending", "running"]))
        .order_by(Job.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(request, "admin/_active_jobs.html", {
        "jobs": jobs,
    })
