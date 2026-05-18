from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from slugify import slugify
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.config import get_settings
from app.database import get_db
from app.models.album import Album
from app.models.media import Media
from app.models.page import Page

router = APIRouter(tags=["admin-pages"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


def _guard(request):
    admin = require_admin(request)
    if not admin:
        return None, RedirectResponse("/admin/login", status_code=302)
    return admin, None


def _editor_ctx(db: Session) -> dict:
    """Photos and albums for the editor pickers."""
    photos = db.query(Media).filter(
        Media.media_type == "photo",
        Media.conversion_status == "done",
        Media.thumb_path.isnot(None),
    ).order_by(Media.created_at.desc()).all()
    albums = db.query(Album).filter(
        Album.is_public == True
    ).order_by(Album.sort_order, Album.title).all()
    return {"editor_photos": photos, "editor_albums": albums}


@router.get("/pages", response_class=HTMLResponse)
async def pages_list(request: Request, db: Session = Depends(get_db)):
    admin, redir = _guard(request)
    if redir: return redir
    pages = db.query(Page).order_by(Page.sort_order, Page.title).all()
    return templates.TemplateResponse(request, "admin/pages/list.html", {
        "admin": admin, "site_title": settings.site_title, "active": "pages", "pages": pages,
    })


@router.get("/pages/new", response_class=HTMLResponse)
async def page_new(request: Request, db: Session = Depends(get_db)):
    admin, redir = _guard(request)
    if redir: return redir
    photos = db.query(Media).filter(
        Media.media_type == "photo", Media.conversion_status == "done"
    ).order_by(Media.created_at.desc()).all()
    return templates.TemplateResponse(request, "admin/pages/edit.html", {
        "admin": admin, "site_title": settings.site_title,
        "active": "pages", "page": None, "is_new": True, "photos": photos,
        **_editor_ctx(db),
    })


@router.post("/pages/create")
async def page_create(
    request: Request,
    title:         str           = Form(...),
    content_html:  str           = Form(""),
    content_delta: str           = Form(""),
    cover_url:     str           = Form(""),
    is_published:  Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    admin, redir = _guard(request)
    if redir: return redir
    base_slug = slugify(title) or "page"
    slug, counter = base_slug, 1
    while db.query(Page).filter(Page.slug == slug).first():
        slug = f"{base_slug}-{counter}"; counter += 1
    page = Page(
        slug=slug, title=title.strip(),
        content_html=content_html or None,
        content_delta=content_delta or None,
        cover_url=cover_url.strip() or None,
        is_published=is_published == "on",
    )
    db.add(page); db.commit(); db.refresh(page)
    return RedirectResponse(f"/admin/pages/{page.id}", status_code=302)


@router.get("/pages/{page_id}", response_class=HTMLResponse)
async def page_edit(page_id: int, request: Request, db: Session = Depends(get_db)):
    admin, redir = _guard(request)
    if redir: return redir
    page = db.query(Page).filter(Page.id == page_id).first()
    if not page: return RedirectResponse("/admin/pages", status_code=302)
    photos = db.query(Media).filter(
        Media.media_type == "photo", Media.conversion_status == "done"
    ).order_by(Media.created_at.desc()).all()
    return templates.TemplateResponse(request, "admin/pages/edit.html", {
        "admin": admin, "site_title": settings.site_title,
        "active": "pages", "page": page, "is_new": False, "photos": photos,
        **_editor_ctx(db),
    })


@router.post("/pages/{page_id}/update")
async def page_update(
    page_id: int, request: Request,
    title:         str           = Form(...),
    content_html:  str           = Form(""),
    content_delta: str           = Form(""),
    cover_url:     str           = Form(""),
    is_published:  Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    admin, redir = _guard(request)
    if redir: return redir
    page = db.query(Page).filter(Page.id == page_id).first()
    if not page: return RedirectResponse("/admin/pages", status_code=302)
    page.title        = title.strip()
    page.content_html = content_html or None
    page.content_delta= content_delta or None
    page.cover_url    = cover_url.strip() or None
    page.is_published = is_published == "on"
    db.commit()
    return RedirectResponse(f"/admin/pages/{page_id}", status_code=302)


@router.post("/pages/{page_id}/delete")
async def page_delete(page_id: int, request: Request, db: Session = Depends(get_db)):
    admin, redir = _guard(request)
    if redir: return redir
    page = db.query(Page).filter(Page.id == page_id).first()
    if page: db.delete(page); db.commit()
    return RedirectResponse("/admin/pages", status_code=302)


@router.post("/pages/{page_id}/toggle-publish", response_class=HTMLResponse)
async def page_toggle_publish(page_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_admin(request): return HTMLResponse("", status_code=401)
    page = db.query(Page).filter(Page.id == page_id).first()
    if page: page.is_published = not page.is_published; db.commit()
    cls  = "badge-public" if page.is_published else "badge-private"
    text = "PUBLISHED" if page.is_published else "DRAFT"
    return HTMLResponse(
        f'<span class="badge {cls}" id="pub-{page_id}" '
        f'hx-post="/admin/pages/{page_id}/toggle-publish" '
        f'hx-trigger="click" hx-swap="outerHTML" style="cursor:pointer;">{text}</span>'
    )


# ── API: media list for editor pickers ──
@router.get("/api/editor/photos", response_class=JSONResponse)
async def api_editor_photos(request: Request, db: Session = Depends(get_db)):
    if not require_admin(request): return JSONResponse([], status_code=401)
    photos = db.query(Media).filter(
        Media.media_type == "photo",
        Media.conversion_status == "done",
        Media.thumb_path.isnot(None),
    ).order_by(Media.created_at.desc()).all()
    return JSONResponse([{
        "id":         p.id,
        "thumb_path": p.thumb_path,
        "web_path":   p.web_path,
        "filename":   p.original_filename,
        "width":      p.width,
        "height":     p.height,
    } for p in photos])


@router.get("/api/editor/albums", response_class=JSONResponse)
async def api_editor_albums(request: Request, db: Session = Depends(get_db)):
    if not require_admin(request): return JSONResponse([], status_code=401)
    albums = db.query(Album).filter(Album.is_public == True).order_by(Album.sort_order, Album.title).all()
    return JSONResponse([{
        "id":    a.id,
        "title": a.title,
        "slug":  a.slug,
        "cover": a.cover_thumb_path,
    } for a in albums])
