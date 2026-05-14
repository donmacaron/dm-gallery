from __future__ import annotations
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
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


def _get_sub_album_ids(db: Session, album_id: int) -> list:
    result = []
    queue = [album_id]
    while queue:
        current = queue.pop()
        children = db.execute(
            text("SELECT id FROM albums WHERE parent_id = :pid"),
            {"pid": current}
        ).fetchall()
        for row in children:
            result.append(row[0])
            queue.append(row[0])
    return result


def _sub_album_media(db: Session, album_id: int) -> list:
    sub_ids = _get_sub_album_ids(db, album_id)
    if not sub_ids:
        return []
    sub_albums     = db.query(Album).filter(Album.id.in_(sub_ids)).all()
    album_name_map = {a.id: a.title for a in sub_albums}
    result = []
    for sub_id in sub_ids:
        rows = db.execute(
            text("SELECT media_id FROM album_media WHERE album_id = :aid ORDER BY sort_order, added_at"),
            {"aid": sub_id},
        ).fetchall()
        media_ids = [r[0] for r in rows]
        if not media_ids:
            continue
        objs = db.query(Media).filter(
            Media.id.in_(media_ids),
            Media.conversion_status == "done",
            Media.thumb_path.isnot(None),
        ).all()
        for m in objs:
            result.append({"media": m, "album_id": sub_id, "album_name": album_name_map.get(sub_id, "")})
    return result


def _try_auto_cover(db: Session, album_id: int) -> None:
    """Set first available thumb as cover if album has none. Also extracts dominant color."""
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album or album.cover_thumb_path:
        return
    row = db.execute(
        text("""
            SELECT m.thumb_path FROM media m
            JOIN album_media am ON am.media_id = m.id
            WHERE am.album_id = :aid
              AND m.thumb_path IS NOT NULL
              AND m.conversion_status = 'done'
            ORDER BY am.sort_order, am.added_at
            LIMIT 1
        """),
        {"aid": album_id},
    ).fetchone()
    if row and row[0]:
        album.cover_thumb_path = row[0]
        _update_dominant_color(album, row[0])
        db.commit()


def _update_dominant_color(album: Album, thumb_path: str) -> None:
    """Extract dominant color from thumbnail and store on album (no commit)."""
    try:
        from app.services.color_extractor import extract_dominant_color
        color = extract_dominant_color(thumb_path, settings.media_path)
        if color:
            album.dominant_color = color
    except Exception:
        pass


# ── LIST ──
@router.get("/albums", response_class=HTMLResponse)
async def albums_list(request: Request, db: Session = Depends(get_db)):
    admin, redir = _guard(request)
    if redir: return redir
    top_albums = (
        db.query(Album).filter(Album.parent_id == None)
        .order_by(Album.sort_order, Album.title).all()
    )
    child_albums = (
        db.query(Album).filter(Album.parent_id != None)
        .order_by(Album.parent_id, Album.sort_order, Album.title).all()
    )
    return templates.TemplateResponse(request, "admin/albums/list.html", {
        "admin": admin, "site_title": settings.site_title, "active": "albums",
        "top_albums": top_albums, "child_albums": child_albums,
    })


@router.post("/albums/reorder-top", response_class=JSONResponse)
async def albums_reorder_top(request: Request, db: Session = Depends(get_db)):
    if not require_admin(request): return JSONResponse({"status": "error"}, status_code=401)
    try:
        body  = await request.json()
        order = body.get("order", [])
    except Exception:
        return JSONResponse({"status": "error"}, status_code=400)
    for idx, album_id in enumerate(order):
        db.execute(text("UPDATE albums SET sort_order = :s WHERE id = :id"), {"s": idx, "id": int(album_id)})
    db.commit()
    return JSONResponse({"status": "ok", "updated": len(order)})


@router.post("/albums/{album_id}/reorder-subs", response_class=JSONResponse)
async def album_reorder_subs(album_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_admin(request): return JSONResponse({"status": "error"}, status_code=401)
    try:
        body  = await request.json()
        order = body.get("order", [])
    except Exception:
        return JSONResponse({"status": "error"}, status_code=400)
    for idx, aid in enumerate(order):
        db.execute(
            text("UPDATE albums SET sort_order = :s WHERE id = :id AND parent_id = :pid"),
            {"s": idx, "id": int(aid), "pid": album_id}
        )
    db.commit()
    return JSONResponse({"status": "ok", "updated": len(order)})


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
    media_items   = _album_media(db, album_id)
    sub_albums    = db.query(Album).filter(Album.parent_id == album_id).order_by(Album.sort_order).all()
    all_albums    = db.query(Album).filter(Album.id != album_id).order_by(Album.title).all()
    zip_job       = (
        db.query(Job).filter(Job.job_type == "zip", Job.target_id == album_id)
        .order_by(Job.created_at.desc()).first()
    )
    linked_ids    = [m.id for m in media_items]
    library_media = (
        db.query(Media).filter(Media.conversion_status == "done")
        .filter(~Media.id.in_(linked_ids) if linked_ids else True)
        .order_by(Media.created_at.desc()).all()
    )
    sub_media = _sub_album_media(db, album_id)
    return templates.TemplateResponse(request, "admin/albums/edit.html", {
        "admin": admin, "site_title": settings.site_title, "active": "albums",
        "album": album, "media_items": media_items,
        "sub_albums": sub_albums, "all_albums": all_albums,
        "zip_job": zip_job, "library_media": library_media, "sub_media": sub_media,
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
        db.query(Album).filter(Album.parent_id == album_id).update({"parent_id": None})
        db.delete(album); db.commit()
    return RedirectResponse("/admin/albums", status_code=302)


@router.post("/albums/{album_id}/toggle-public", response_class=HTMLResponse)
async def album_toggle_public(album_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_admin(request): return HTMLResponse("", status_code=401)
    album = db.query(Album).filter(Album.id == album_id).first()
    if album: album.is_public = not album.is_public; db.commit()
    cls   = "badge-public" if album.is_public else "badge-private"
    label = "PUBLIC" if album.is_public else "PRIVATE"
    return HTMLResponse(
        f'<span class="badge {cls}" id="visibility-{album_id}" '
        f'hx-post="/admin/albums/{album_id}/toggle-public" '
        f'hx-trigger="click" hx-swap="outerHTML" style="cursor:pointer;">{label}</span>'
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


# ── MANY-TO-MANY ──
@router.post("/albums/{album_id}/add-media/{media_id}", response_class=HTMLResponse)
async def album_add_media(album_id: int, media_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_admin(request): return HTMLResponse("", status_code=401)
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
        _try_auto_cover(db, album_id)
    return HTMLResponse("")


@router.post("/albums/{album_id}/add-media-bulk", response_class=HTMLResponse)
async def album_add_media_bulk(
    album_id: int, request: Request,
    media_ids: str = Form(""),
    db: Session = Depends(get_db),
):
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
    _try_auto_cover(db, album_id)
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
    """Set cover + extract dominant color."""
    if not require_admin(request): return HTMLResponse("", status_code=401)
    album = db.query(Album).filter(Album.id == album_id).first()
    media = db.query(Media).filter(Media.id == media_id).first()
    if album and media and media.thumb_path:
        album.cover_thumb_path = media.thumb_path
        _update_dominant_color(album, media.thumb_path)
        db.commit()
    return HTMLResponse('<span style="color:var(--fg);font-size:0.75rem;">✓ Cover set</span>')


@router.post("/albums/{album_id}/reorder", response_class=JSONResponse)
async def album_reorder(album_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_admin(request): return JSONResponse({"status": "error"}, status_code=401)
    try:
        body  = await request.json()
        order = body.get("order", [])
    except Exception:
        return JSONResponse({"status": "error"}, status_code=400)
    for idx, media_id in enumerate(order):
        db.execute(
            text("UPDATE album_media SET sort_order = :s WHERE album_id = :a AND media_id = :m"),
            {"s": idx, "a": album_id, "m": int(media_id)},
        )
    db.commit()
    return JSONResponse({"status": "ok", "updated": len(order)})


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
