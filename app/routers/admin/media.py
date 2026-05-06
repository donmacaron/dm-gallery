from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
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
        linked_ids = [r[0] for r in db.execute(
            text("SELECT DISTINCT media_id FROM album_media")
        ).fetchall()]
        if linked_ids:
            q = q.filter(~Media.id.in_(linked_ids))

    media_items = q.order_by(Media.created_at.desc()).all()
    albums      = db.query(Album).order_by(Album.title).all()

    # Build album membership map using Python-side iteration (avoids SQLite IN ? syntax issue)
    media_album_map: dict = {}
    if media_items:
        # Load ALL album_media rows once, then filter in Python
        all_links = db.execute(
            text("""
                SELECT am.media_id, a.id, a.title
                FROM album_media am
                JOIN albums a ON a.id = am.album_id
            """)
        ).fetchall()
        mids = {m.id for m in media_items}
        for mid, aid, atitle in all_links:
            if mid in mids:
                media_album_map.setdefault(mid, []).append({"id": aid, "title": atitle})

    return templates.TemplateResponse(request, "admin/media/list.html", {
        "admin":           admin,
        "site_title":      settings.site_title,
        "active":          "media",
        "media_items":     media_items,
        "filter_type":     media_type,
        "unassigned":      unassigned,
        "albums":          albums,
        "media_album_map": media_album_map,
    })


@router.post("/api/media/bulk-action", response_class=HTMLResponse)
async def media_bulk_action(
    request:   Request,
    action:    str           = Form(""),
    media_ids: str           = Form(""),
    album_id:  Optional[str] = Form(None),
    db:        Session       = Depends(get_db),
):
    admin = require_admin(request)
    if not admin:
        return HTMLResponse("", status_code=401)

    ids = [int(x) for x in media_ids.split(",") if x.strip().isdigit()]
    if not ids:
        return RedirectResponse("/admin/media", status_code=302)

    if action == "delete":
        for mid in ids:
            db.execute(text("DELETE FROM album_media WHERE media_id=:m"), {"m": mid})
            media = db.query(Media).filter(Media.id == mid).first()
            if media:
                db.delete(media)
        db.commit()

    elif action == "add_to_album" and album_id and album_id.isdigit():
        aid = int(album_id)
        for mid in ids:
            existing = db.execute(
                text("SELECT 1 FROM album_media WHERE album_id=:a AND media_id=:m"),
                {"a": aid, "m": mid}
            ).fetchone()
            if not existing:
                db.execute(
                    text("INSERT INTO album_media (album_id, media_id, sort_order) VALUES (:a, :m, 0)"),
                    {"a": aid, "m": mid}
                )
        db.commit()

    return RedirectResponse("/admin/media", status_code=302)


@router.post("/api/media/{media_id}/delete")
async def media_delete(media_id: int, request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    db.execute(text("DELETE FROM album_media WHERE media_id=:m"), {"m": media_id})
    media = db.query(Media).filter(Media.id == media_id).first()
    if media:
        db.delete(media)
    db.commit()
    return RedirectResponse("/admin/media", status_code=302)
