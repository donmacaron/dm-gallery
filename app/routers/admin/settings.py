from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.config import get_settings
from app.database import get_db
from app.models.setting import Setting

router = APIRouter(tags=["admin-settings"])
templates = Jinja2Templates(directory="app/templates")
settings_obj = get_settings()

SETTINGS_GROUPS = [
    ("Site", [
        ("site_title",   "text",  "Site Title"),
        ("site_tagline", "text",  "Tagline (meta description)"),
    ]),
    ("Header", [
        ("header_logo_text",    "text",     "Logo Text (empty = use Site Title)"),
        ("header_show_tagline", "checkbox", "Show tagline under logo in header"),
    ]),
    ("Social Links", [
        ("social_telegram_url",  "url", "Telegram URL (leave empty to hide icon)"),
        ("social_instagram_url", "url", "Instagram URL (leave empty to hide icon)"),
    ]),
    ("Theme Colors", [
        ("theme_bg_color",         "color", "Background Color"),
        ("theme_fg_color",         "color", "Text / Phosphor Color"),
        ("theme_accent_color",     "color", "Accent Color"),
        ("theme_scanline_opacity", "text",  "Scanline Opacity (0.0 \u2013 0.3)"),
        ("theme_font",             "text",  "Primary Font (Google Fonts name, e.g. VT323)"),
    ]),
    ("Homepage", [
        ("homepage_album_id", "text", "Featured Album ID (empty = list all public albums)"),
    ]),
]


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    rows    = db.query(Setting).all()
    current = {s.key: s.value for s in rows}
    return templates.TemplateResponse(request, "admin/settings/index.html", {
        "admin":      admin,
        "site_title": settings_obj.site_title,
        "active":     "settings",
        "groups":     SETTINGS_GROUPS,
        "current":    current,
        "saved":      False,
    })


@router.post("/settings/update", response_class=HTMLResponse)
async def settings_update(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)

    form = await request.form()

    for group_name, fields in SETTINGS_GROUPS:
        for key, ftype, label in fields:
            if ftype == "checkbox":
                # Checkbox: present in form = "1", absent = "0"
                value = "1" if form.get(key) else "0"
            else:
                value = str(form.get(key, "") or "")

            row = db.query(Setting).filter(Setting.key == key).first()
            if row:
                row.value = value
            else:
                db.add(Setting(key=key, value=value))

    db.commit()

    rows    = db.query(Setting).all()
    current = {s.key: s.value for s in rows}
    return templates.TemplateResponse(request, "admin/settings/index.html", {
        "admin":      admin,
        "site_title": settings_obj.site_title,
        "active":     "settings",
        "groups":     SETTINGS_GROUPS,
        "current":    current,
        "saved":      True,
    })
