from __future__ import annotations
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from slugify import slugify
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.config import get_settings
from app.database import get_db
from app.models.album import Album
from app.models.job import Job
from app.models.media import Media

router = APIRouter(tags=["admin-albums"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


def _guard(request: Request):
    admin = require_admin(request)
    if not admin:
        return None, RedirectResponse("/admin/login", status_code=302)
    return admin, None


def _album_media(db: Session, album_id: int) -> list:
    """All media linked to an album via junction table."""
    rows = db.execute(
        text("SELECT media_id FROM album_media WHERE album_id = :aid ORDER BY sort_order, added_at"),
        {"aid": album_id},
    ).fetchall()
    media_ids = [r[0] for r in rows]
    if not media_ids:
        return []
    objs = db.query(Media).filter(Media.id.in_(media_ids)).all()
    order_map = {mid: i for i, mid in enumerate(media_ids)}
    return sorted(objs, key=lambda m: order_map.get(m.id, 9999))


# ── LIST ──
@router.get("/albums", response_class=HTMLResponse)
async def albums_list(request: Request, db: Session = Depends(get_db)):
    admin, redir = _guard(request)
    if redir: return redir
    albums = db.query(Album).order_by(Album.parent_id.nullsfirst(), Album.sort_order, Album.title).all()
    return templates.TemplateResponse(request, "admin/albums/list.html", {
        "admin": admin, "site_title": settings.site_title, "active": "albums", "albums": albums,
    })


@router.get("/albums/new", response_class=HTMLResponse)
async def album_new(request: Request, db: Session = Depends(get_db)):
    admin, redir = _guard(request)
    if redir: return redir
    all_albums = db.query(Album).order_by(Album.title).all()
    return templates.TemplateResponse(request, "admin/albums/new.html", {
        "admin": admin, "site_title": settings.site_title, "active": "albums", "all_albums": all_albums,
    })


@router.post("/albums/create")
async def album_create(
    request: Request,
    title: str = Form(...), description: str = Form(""),
    parent_id: Optional[str] = Form(None),
    is_public: Optional[str] = Form(None), auto_zip: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    admin, redir = _guard(request)
    if redir: return redir
    base_slug = slugify(title) or "album"
    slug, counter = base_slug, 1
    while db.query(Album).filter(Album.slug == slug).first():
        slug = f"{base_slug}-{counter}"; counter += 1
    album = Album(
        slug=slug, title=title.strip(), description=description.strip() or None,
        parent_id=int(parent_id) if parent_id and parent_id.isdigit() else None,
        is_public=is_public == "on", auto_zip=auto_zip == "on",
    )
    db.add(album); db.commit(); db.refresh(album)
    return RedirectResponse(f"/admin/albums/{album.id}", status_code=302)


@router.get("/albums/{album_id}", response_class=HTMLResponse)
async def album_detail(album_id: int, request: Request, db: Session = Depends(get_db)):
    admin, redir = _guard(request)
    if redir: return redir
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album: return RedirectResponse("/admin/albums", status_code=302)

    media_items = _album_media(db, album_id)
    sub_albums  = db.query(Album).filter(Album.parent_id == album_id).order_by(Album.sort_order).all()
    all_albums  = db.query(Album).filter(Album.id != album_id).order_by(Album.title).all()
    zip_job = (
        db.query(Job).filter(Job.job_type == "zip", Job.target_id == album_id)
        .order_by(Job.created_at.desc()).first()
    )
    # Media NOT in this album (for "add from library" panel)
    linked_ids = [m.id for m in media_items]
    library_media = (
        db.query(Media)
        .filter(Media.conversion_status == "done")
        .filter(~Media.id.in_(linked_ids) if linked_ids else True)
        .order_by(Media.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(request, "admin/albums/edit.html", {
        "admin": admin, "site_title": settings.site_title, "active": "albums",
        "album": album, "media_items": media_items,
        "sub_albums": sub_albums, "all_albums": all_albums,
        "zip_job": zip_job, "library_media": library_media,
    })


@router.post("/albums/{album_id}/update")
async def album_update(
    album_id: int, request: Request,
    title: str = Form(...), description: str = Form(""),
    parent_id: Optional[str] = Form(None),
    is_public: Optional[str] = Form(None), auto_zip: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    admin, redir = _guard(request)
    if redir: return redir
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album: return RedirectResponse("/admin/albums", status_code=302)
    album.title = title.strip(); album.description = description.strip() or None
    album.parent_id = int(parent_id) if parent_id and parent_id.isdigit() else None
    album.is_public = is_public == "on"; album.auto_zip = auto_zip == "on"
    db.commit()
    return RedirectResponse(f"/admin/albums/{album_id}", status_code=302)


@router.post("/albums/{album_id}/delete")
async def album_delete(album_id: int, request: Request, db: Session = Depends(get_db)):
    admin, redir = _guard(request)
    if redir: return redir
    album = db.query(Album).filter(Album.id == album_id).first()
    if album:
        # Junction rows deleted via CASCADE
        db.query(Album).filter(Album.parent_id == album_id).update({"parent_id": None})
        db.delete(album); db.commit()
    return RedirectResponse("/admin/albums", status_code=302)


@router.post("/albums/{album_id}/toggle-public", response_class=HTMLResponse)
async def album_toggle_public(album_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_admin(request): return HTMLResponse("", status_code=401)
    album = db.query(Album).filter(Album.id == album_id).first()
    if album: album.is_public = not album.is_public; db.commit()
    cls  = "badge-public" if album.is_public else "badge-private"
    text_label = "PUBLIC" if album.is_public else "PRIVATE"
    return HTMLResponse(
        f'<span class="badge {cls}" id="visibility-{album_id}" '
        f'hx-post="/admin/albums/{album_id}/toggle-public" '
        f'hx-trigger="click" hx-swap="outerHTML" style="cursor:pointer;">{text_label}</span>'
    )


@router.post("/albums/{album_id}/regen-token", response_class=HTMLResponse)
async def album_regen_token(album_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_admin(request): return HTMLResponse("", status_code=401)
    album = db.query(Album).filter(Album.id == album_id).first()
    if album: album.share_token = secrets.token_hex(16); db.commit()
    share_url = f"/s/{album.share_token}" if album and album.share_token else ""
    return HTMLResponse(
        f'<code id="share-token-{album_id}" style="font-size:0.75rem;color:var(--accent);word-break:break-all;">'
        f'{share_url}</code>'
    )


# ── MANY-TO-MANY: add/remove media via junction ──
@router.post("/albums/{album_id}/add-media/{media_id}", response_class=HTMLResponse)
async def album_add_media(album_id: int, media_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_admin(request): return HTMLResponse("", status_code=401)
    # Check not already linked
    existing = db.execute(
        text("SELECT 1 FROM album_media WHERE album_id=:a AND media_id=:m"),
        {"a": album_id, "m": media_id}
    ).fetchone()
    if not existing:
        db.execute(
            text("INSERT INTO album_media (album_id, media_id, sort_order) VALUES (:a, :m, 0)"),
            {"a": album_id, "m": media_id}
        )
        db.commit()
    return HTMLResponse("")


@router.post("/albums/{album_id}/add-media-bulk", response_class=HTMLResponse)
async def album_add_media_bulk(
    album_id: int, request: Request,
    media_ids: str = Form(""),
    db: Session = Depends(get_db),
):
    """Add multiple media to album at once. media_ids = comma-separated IDs."""
    if not require_admin(request): return HTMLResponse("", status_code=401)
    ids = [int(x) for x in media_ids.split(",") if x.strip().isdigit()]
    for mid in ids:
        existing = db.execute(
            text("SELECT 1 FROM album_media WHERE album_id=:a AND media_id=:m"),
            {"a": album_id, "m": mid}
        ).fetchone()
        if not existing:
            db.execute(
                text("INSERT INTO album_media (album_id, media_id, sort_order) VALUES (:a, :m, 0)"),
                {"a": album_id, "m": mid}
            )
    db.commit()
    return RedirectResponse(f"/admin/albums/{album_id}", status_code=302)


@router.post("/albums/{album_id}/remove-media/{media_id}", response_class=HTMLResponse)
async def album_remove_media(album_id: int, media_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_admin(request): return HTMLResponse("", status_code=401)
    db.execute(
        text("DELETE FROM album_media WHERE album_id=:a AND media_id=:m"),
        {"a": album_id, "m": media_id}
    )
    db.commit()
    return HTMLResponse("")


@router.post("/albums/{album_id}/set-cover/{media_id}", response_class=HTMLResponse)
async def album_set_cover(album_id: int, media_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_admin(request): return HTMLResponse("", status_code=401)
    album = db.query(Album).filter(Album.id == album_id).first()
    media = db.query(Media).filter(Media.id == media_id).first()
    if album and media and media.thumb_path:
        album.cover_thumb_path = media.thumb_path; db.commit()
    return HTMLResponse('<span style="color:var(--fg);font-size:0.75rem;">✓ Cover set</span>')


# ── ZIP ──
@router.post("/albums/{album_id}/build-zip", response_class=HTMLResponse)
async def album_build_zip(album_id: int, request: Request, db: Session = Depends(get_db)):
    import uuid as _uuid
    from app.services import job_runner
    from app.services.zip_service import build_album_zip
    if not require_admin(request): return HTMLResponse("", status_code=401)
    job_id = _uuid.uuid4().hex
    job = Job(id=job_id, job_type="zip", status="pending",
              target_id=album_id, target_type="album",
              total_items=0, done_items=0, progress=0)
    db.add(job); db.commit()
    job_runner.submit(build_album_zip, album_id, job_id, settings.zips_path)
    return templates.TemplateResponse(request, "admin/_zip_status.html", {
        "job": job, "album_id": album_id,
    })


@router.get("/api/albums/{album_id}/zip-status", response_class=HTMLResponse)
async def album_zip_status(album_id: int, request: Request, job_id: str = "", db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first() if job_id else None
    if not job:
        job = (db.query(Job).filter(Job.job_type == "zip", Job.target_id == album_id)
               .order_by(Job.created_at.desc()).first())
    return templates.TemplateResponse(request, "admin/_zip_status.html", {
        "job": job, "album_id": album_id,
    })
