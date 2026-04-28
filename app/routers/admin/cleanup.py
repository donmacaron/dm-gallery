"""
Cleanup Router — Phase 6
Scan for orphaned media files on disk (no DB record) and optionally delete them.
"""
from __future__ import annotations
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.config import get_settings
from app.database import get_db
from app.models.media import Media

router = APIRouter(tags=["admin-cleanup"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


def _find_orphans(db: Session) -> dict:
    """Find files on disk with no corresponding DB record."""
    all_originals = {m.original_path for m in db.query(Media).all() if m.original_path}
    all_web       = {m.web_path   for m in db.query(Media).all() if m.web_path}
    all_thumbs    = {m.thumb_path for m in db.query(Media).all() if m.thumb_path}

    orphan_originals = []
    orig_dir = Path(settings.originals_path)
    if orig_dir.exists():
        for f in orig_dir.iterdir():
            if f.is_file() and str(f) not in all_originals:
                orphan_originals.append({"path": str(f), "size_mb": round(f.stat().st_size / 1048576, 2)})

    orphan_media = []
    media_dir = Path(settings.media_path)
    if media_dir.exists():
        for f in media_dir.rglob("*"):
            if not f.is_file():
                continue
            rel = str(f.relative_to(media_dir))
            if rel not in all_web and rel not in all_thumbs:
                orphan_media.append({"path": str(f), "size_mb": round(f.stat().st_size / 1048576, 2)})

    return {
        "orphan_originals": orphan_originals,
        "orphan_media":     orphan_media,
        "total_originals":  len(orphan_originals),
        "total_media":      len(orphan_media),
        "size_originals_mb":round(sum(o["size_mb"] for o in orphan_originals), 1),
        "size_media_mb":    round(sum(o["size_mb"] for o in orphan_media), 1),
    }


@router.get("/cleanup", response_class=HTMLResponse)
async def cleanup_page(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    stats = _find_orphans(db)
    return templates.TemplateResponse(request, "admin/cleanup.html", {
        "admin": admin, "site_title": settings.site_title,
        "active": "cleanup", "stats": stats, "done": False,
    })


@router.post("/cleanup/run", response_class=HTMLResponse)
async def cleanup_run(
    request: Request,
    what:    str     = "media",  # 'originals' | 'media' | 'all'
    db:      Session = Depends(get_db),
):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)

    stats   = _find_orphans(db)
    deleted = 0

    targets: list = []
    if what in ("originals", "all"):
        targets += [o["path"] for o in stats["orphan_originals"]]
    if what in ("media", "all"):
        targets += [o["path"] for o in stats["orphan_media"]]

    for path_str in targets:
        try:
            Path(path_str).unlink(missing_ok=True)
            deleted += 1
        except Exception:
            pass

    stats_after = _find_orphans(db)
    return templates.TemplateResponse(request, "admin/cleanup.html", {
        "admin": admin, "site_title": settings.site_title,
        "active": "cleanup", "stats": stats_after,
        "done": True, "deleted": deleted,
    })
