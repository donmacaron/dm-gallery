from __future__ import annotations
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import authenticate_admin, create_access_token, hash_password, require_admin
from app.config import get_settings
from app.database import get_db
from app.models.setting import Setting

router = APIRouter(tags=["admin-settings"])
templates = Jinja2Templates(directory="app/templates")
settings_obj = get_settings()

SETTINGS_GROUPS = [
    ("Site", [
        ("site_title",   "text", "Site Title"),
        ("site_tagline", "text", "Tagline (meta description)"),
    ]),
    ("Header", [
        ("header_logo_text",    "text",     "Logo Text (empty = use Site Title)"),
        ("header_show_tagline", "checkbox", "Show tagline under logo"),
        ("header_bg_color",     "color",    "Header Background Color"),
        ("header_border_color", "color",    "Header Border / Divider Color"),
        ("header_text_color",   "color",    "Header Text / Logo Color"),
    ]),
    ("Social Links", [
        ("social_telegram_url",  "url", "Telegram URL (empty = hide icon)"),
        ("social_instagram_url", "url", "Instagram URL (empty = hide icon)"),
    ]),
    ("Theme Colors", [
        ("theme_bg_color",         "color", "Page Background Color"),
        ("theme_fg_color",         "color", "Text / Phosphor Color"),
        ("theme_accent_color",     "color", "Accent Color"),
        ("theme_scanline_opacity", "text",  "Scanline Opacity (0.0 \u2013 0.3)"),
        ("theme_font",             "text",  "Primary Font (Google Fonts name)"),
    ]),
    ("Homepage", [
        ("homepage_album_id", "text", "Featured Album ID (empty = list all)"),
    ]),
]


def _current_username(db: Session) -> str:
    row = db.query(Setting).filter(Setting.key == "admin_username").first()
    return row.value if row and row.value else settings_obj.admin_username


def _upsert(db: Session, key: str, value: str):
    row = db.query(Setting).filter(Setting.key == key).first()
    if row:
        row.value = value
    else:
        db.add(Setting(key=key, value=value))


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    rows    = db.query(Setting).all()
    current = {s.key: s.value for s in rows}
    return templates.TemplateResponse(request, "admin/settings/index.html", {
        "admin": admin, "site_title": settings_obj.site_title,
        "active": "settings", "groups": SETTINGS_GROUPS,
        "current": current, "saved": False,
        "current_username": _current_username(db),
        "account_error": None, "account_saved": False,
    })


@router.post("/settings/update", response_class=HTMLResponse)
async def settings_update(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    form = await request.form()
    for _, fields in SETTINGS_GROUPS:
        for key, ftype, _ in fields:
            value = "1" if (ftype == "checkbox" and form.get(key)) else str(form.get(key, "") or "")
            _upsert(db, key, value)
    db.commit()
    rows    = db.query(Setting).all()
    current = {s.key: s.value for s in rows}
    return templates.TemplateResponse(request, "admin/settings/index.html", {
        "admin": admin, "site_title": settings_obj.site_title,
        "active": "settings", "groups": SETTINGS_GROUPS,
        "current": current, "saved": True,
        "current_username": _current_username(db),
        "account_error": None, "account_saved": False,
    })


@router.post("/settings/update-account", response_class=HTMLResponse)
async def settings_update_account(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)

    form         = await request.form()
    new_username = str(form.get("new_username", "")).strip()
    current_pw   = str(form.get("current_password", ""))
    new_pw       = str(form.get("new_password", ""))
    confirm_pw   = str(form.get("confirm_password", ""))

    rows    = db.query(Setting).all()
    current = {s.key: s.value for s in rows}
    cur_username = _current_username(db)

    def _render(error=None, saved=False):
        return templates.TemplateResponse(request, "admin/settings/index.html", {
            "admin": admin, "site_title": settings_obj.site_title,
            "active": "settings", "groups": SETTINGS_GROUPS,
            "current": current, "saved": False,
            "current_username": cur_username,
            "account_error": error, "account_saved": saved,
        })

    # Must verify current password first
    if not authenticate_admin(cur_username, current_pw):
        return _render(error="Current password is incorrect.")

    if new_pw:
        if new_pw != confirm_pw:
            return _render(error="New passwords do not match.")
        if len(new_pw) < 6:
            return _render(error="New password must be at least 6 characters.")

    if new_username and len(new_username) < 2:
        return _render(error="Username must be at least 2 characters.")

    if new_username:
        _upsert(db, "admin_username", new_username)
        cur_username = new_username

    if new_pw:
        _upsert(db, "admin_password_hash", hash_password(new_pw))

    db.commit()

    from datetime import timedelta
    token = create_access_token(
        data={"sub": cur_username},
        expires_delta=timedelta(minutes=settings_obj.access_token_expire_minutes),
    )
    rows    = db.query(Setting).all()
    current = {s.key: s.value for s in rows}
    resp = templates.TemplateResponse(request, "admin/settings/index.html", {
        "admin": cur_username, "site_title": settings_obj.site_title,
        "active": "settings", "groups": SETTINGS_GROUPS,
        "current": current, "saved": False,
        "current_username": cur_username,
        "account_error": None, "account_saved": True,
    })
    resp.set_cookie(
        key="admin_token", value=token,
        httponly=True, max_age=60 * 60 * 24 * 7, samesite="lax",
    )
    return resp
