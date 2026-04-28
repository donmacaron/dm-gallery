"""
Folder Import Router — Phase 3
Scan a local folder and import it as a new album.
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

router = APIRouter(tags=["admin-folder-import"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


@router.get("/folder-import", response_class=HTMLResponse)
async def folder_import_page(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    albums = db.query(Album).order_by(Album.title).all()
    return templates.TemplateResponse(request, "admin/folder_import.html", {
        "admin": admin, "site_title": settings.site_title,
        "active": "media", "albums": albums,
        "scan_result": None, "error": None,
    })


@router.post("/folder-import/scan", response_class=HTMLResponse)
async def folder_scan(
    request:     Request,
    folder_path: str           = Form(...),
    db:          Session       = Depends(get_db),
):
    """HTMX: scan folder, return preview fragment."""
    admin = require_admin(request)
    if not admin:
        return HTMLResponse("", status_code=401)

    error  = None
    result = None
    try:
        from app.services.folder_scanner import scan_folder
        result = scan_folder(folder_path)
    except Exception as exc:
        error = str(exc)

    return templates.TemplateResponse(request, "admin/_folder_scan_result.html", {
        "folder_path": folder_path,
        "result":      result,
        "error":       error,
    })


@router.post("/folder-import/import")
async def folder_import(
    request:     Request,
    folder_path: str           = Form(...),
    album_title: str           = Form(...),
    parent_id:   Optional[str] = Form(None),
    db:          Session       = Depends(get_db),
):
    """Import folder as new album, queue all conversions."""
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)

    parent = int(parent_id) if parent_id and parent_id.isdigit() else None

    try:
        from app.services.folder_scanner import import_folder
        result = import_folder(
            folder_path    = folder_path,
            album_title    = album_title or folder_path.split("\\")[-1].split("/")[-1],
            originals_path = settings.originals_path,
            parent_id      = parent,
        )
        return RedirectResponse(f"/admin/albums/{result['album_id']}", status_code=302)
    except Exception as exc:
        albums = db.query(Album).order_by(Album.title).all()
        return templates.TemplateResponse(request, "admin/folder_import.html", {
            "admin": admin, "site_title": settings.site_title,
            "active": "media", "albums": albums,
            "scan_result": None, "error": str(exc),
        }, status_code=400)
