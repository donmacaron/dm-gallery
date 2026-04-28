"""
Menu Admin Router — Phase 4
Manage site navigation menu items.
"""
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
from app.models.menu import MenuItem
from app.models.page import Page

router = APIRouter(tags=["admin-menu"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


def _guard(request: Request):
    admin = require_admin(request)
    if not admin:
        return None, RedirectResponse("/admin/login", status_code=302)
    return admin, None


@router.get("/menu", response_class=HTMLResponse)
async def menu_index(request: Request, db: Session = Depends(get_db)):
    admin, redir = _guard(request)
    if redir: return redir
    items  = db.query(MenuItem).filter(MenuItem.parent_id == None).order_by(MenuItem.sort_order).all()
    pages  = db.query(Page).filter(Page.is_published == True).order_by(Page.title).all()
    albums = db.query(Album).filter(Album.is_public == True).order_by(Album.title).all()
    return templates.TemplateResponse(request, "admin/menu/index.html", {
        "admin": admin, "site_title": settings.site_title, "active": "menu",
        "items": items, "pages": pages, "albums": albums,
    })


@router.post("/menu/create")
async def menu_create(
    request:   Request,
    label:     str           = Form(...),
    item_type: str           = Form("external"),
    page_id:   Optional[str] = Form(None),
    album_id:  Optional[str] = Form(None),
    ext_url:   str           = Form(""),
    db:        Session       = Depends(get_db),
):
    admin, redir = _guard(request)
    if redir: return redir

    # Find max sort_order
    max_order = db.query(MenuItem).filter(MenuItem.parent_id == None).count()
    item = MenuItem(
        label     = label.strip(),
        item_type = item_type,
        page_id   = int(page_id)  if page_id  and page_id.isdigit()  else None,
        album_id  = int(album_id) if album_id and album_id.isdigit() else None,
        ext_url   = ext_url.strip() or None,
        sort_order= max_order,
        is_visible= True,
    )
    db.add(item); db.commit()
    return RedirectResponse("/admin/menu", status_code=302)


@router.post("/menu/{item_id}/update")
async def menu_update(
    item_id: int, request: Request,
    label:     str           = Form(...),
    item_type: str           = Form("external"),
    page_id:   Optional[str] = Form(None),
    album_id:  Optional[str] = Form(None),
    ext_url:   str           = Form(""),
    is_visible:Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    admin, redir = _guard(request)
    if redir: return redir
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if item:
        item.label     = label.strip()
        item.item_type = item_type
        item.page_id   = int(page_id)  if page_id  and page_id.isdigit()  else None
        item.album_id  = int(album_id) if album_id and album_id.isdigit() else None
        item.ext_url   = ext_url.strip() or None
        item.is_visible= is_visible == "on"
        db.commit()
    return RedirectResponse("/admin/menu", status_code=302)


@router.post("/menu/{item_id}/delete")
async def menu_delete(item_id: int, request: Request, db: Session = Depends(get_db)):
    admin, redir = _guard(request)
    if redir: return redir
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if item: db.delete(item); db.commit()
    return RedirectResponse("/admin/menu", status_code=302)


@router.post("/menu/{item_id}/move", response_class=HTMLResponse)
async def menu_move(
    item_id: int, request: Request,
    direction: str = Form("up"),
    db: Session = Depends(get_db),
):
    """HTMX: swap sort_order with neighbour."""
    if not require_admin(request): return HTMLResponse("", status_code=401)
    items = db.query(MenuItem).filter(MenuItem.parent_id == None).order_by(MenuItem.sort_order).all()
    ids   = [i.id for i in items]
    try:
        idx = ids.index(item_id)
    except ValueError:
        return RedirectResponse("/admin/menu", status_code=302)

    swap_idx = idx - 1 if direction == "up" else idx + 1
    if 0 <= swap_idx < len(items):
        a, b = items[idx], items[swap_idx]
        a.sort_order, b.sort_order = swap_idx, idx
        db.commit()

    # Return updated list fragment
    items = db.query(MenuItem).filter(MenuItem.parent_id == None).order_by(MenuItem.sort_order).all()
    pages  = db.query(Page).filter(Page.is_published == True).order_by(Page.title).all()
    albums = db.query(Album).filter(Album.is_public == True).order_by(Album.title).all()
    return templates.TemplateResponse(request, "admin/menu/_items_list.html", {
        "items": items, "pages": pages, "albums": albums,
    })
