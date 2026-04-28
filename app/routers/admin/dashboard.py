from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.config import get_settings
from app.database import get_db
from app.models.album import Album
from app.models.job import Job
from app.models.media import Media

router = APIRouter(tags=["admin-dashboard"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    total_albums  = db.query(Album).count()
    total_media   = db.query(Media).count()
    pending       = db.query(Media).filter(Media.conversion_status == "pending").count()
    processing    = db.query(Media).filter(Media.conversion_status == "processing").count()
    error_count   = db.query(Media).filter(Media.conversion_status == "error").count()
    recent_media  = db.query(Media).order_by(Media.created_at.desc()).limit(16).all()
    active_jobs   = (
        db.query(Job)
        .filter(Job.status.in_(["pending", "running"]))
        .order_by(Job.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(request, "admin/dashboard.html", {
        "admin":        admin,
        "site_title":   settings.site_title,
        "active":       "dashboard",
        "total_albums": total_albums,
        "total_media":  total_media,
        "pending":      pending,
        "processing":   processing,
        "error_count":  error_count,
        "recent_media": recent_media,
        "active_jobs":  active_jobs,
    })
