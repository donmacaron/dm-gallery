from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.config import get_settings
from app.database import get_db
from app.models.album import Album
from app.models.media import Media

router = APIRouter(tags=["admin-media"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


@router.get("/media", response_class=HTMLResponse)
async def media_list(
    request:    Request,
    media_type: str     = "",
    unassigned: str     = "",
    db:         Session = Depends(get_db),
):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)

    q = db.query(Media)
    if media_type:
        q = q.filter(Media.media_type == media_type)
    if unassigned == "1":
        q = q.filter(Media.album_id.is_(None))

    media_items = q.order_by(Media.created_at.desc()).all()
    albums = db.query(Album).order_by(Album.title).all()

    return templates.TemplateResponse(request, "admin/media/list.html", {
        "admin":       admin,
        "site_title":  settings.site_title,
        "active":      "media",
        "media_items": media_items,
        "filter_type": media_type,
        "unassigned":  unassigned,
        "albums":      albums,
    })


@router.post("/api/media/{media_id}/assign", response_class=HTMLResponse)
async def media_assign(
    media_id: int,
    request:  Request,
    album_id: Optional[str] = Form(None),
    db:       Session       = Depends(get_db),
):
    admin = require_admin(request)
    if not admin:
        return HTMLResponse("", status_code=401)

    media = db.query(Media).filter(Media.id == media_id).first()
    if media:
        media.album_id = int(album_id) if album_id and album_id.isdigit() else None
        db.commit()

    album_name = ""
    if media and media.album_id:
        album = db.query(Album).filter(Album.id == media.album_id).first()
        album_name = album.title if album else ""

    label = ("\u2713 " + album_name) if album_name else "(unassigned)"
    return HTMLResponse(
        f'<span style="font-size:0.75rem; color:var(--accent);">{label}</span>'
    )


@router.post("/api/media/{media_id}/delete")
async def media_delete(
    media_id: int,
    request:  Request,
    db:       Session = Depends(get_db),
):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)

    media = db.query(Media).filter(Media.id == media_id).first()
    if media:
        db.delete(media)
        db.commit()

    return RedirectResponse("/admin/media", status_code=302)
