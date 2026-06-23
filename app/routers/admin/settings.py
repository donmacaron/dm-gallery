from __future__ import annotations
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import authenticate_admin, create_access_token, hash_password, require_admin
from app.config import get_settings
from app.database import get_db
from app.models.album import Album
from app.models.media import Media
from app.models.page import Page
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
    ("Gallery Display", [
        ("album_names_always", "checkbox", "Always show album names (unchecked = hover only)"),
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
    ("Footer", [
        ("footer_bg_color",     "color", "Footer Background Color"),
        ("footer_fg_color",     "color", "Footer Text Color"),
        ("footer_border_color", "color", "Footer Border / Divider Color"),
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


def _get_settings_map(db: Session) -> dict:
    return {s.key: s.value for s in db.query(Setting).all()}


def _template_ctx(request, admin, db, current, saved=False,
                  homepage_saved=False, account_error=None, account_saved=False):
    albums       = db.query(Album).order_by(Album.sort_order, Album.title).all()
    pages        = db.query(Page).filter(Page.is_published == True).order_by(Page.title).all()
    # Load ALL converted photos (no limit) for the specific_photo picker
    photos       = db.query(Media).filter(
        Media.media_type == "photo", Media.conversion_status == "done"
    ).order_by(Media.created_at.desc()).all()
    selected_ids = [
        int(x) for x in current.get("homepage_selected_albums", "").split(",")
        if x.strip().isdigit()
    ]
    return templates.TemplateResponse(request, "admin/settings/index.html", {
        "admin": admin, "site_title": settings_obj.site_title,
        "active": "settings", "groups": SETTINGS_GROUPS,
        "current": current, "saved": saved,
        "current_username": _current_username(db),
        "account_error": account_error, "account_saved": account_saved,
        "homepage_saved": homepage_saved,
        "albums": albums, "pages": pages, "photos": photos,
        "selected_ids": selected_ids,
    })


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    current = _get_settings_map(db)
    return _template_ctx(request, admin, db, current)


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
    current = _get_settings_map(db)
    return _template_ctx(request, admin, db, current, saved=True)


@router.post("/settings/update-homepage", response_class=HTMLResponse)
async def settings_update_homepage(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    form = await request.form()
    _upsert(db, "homepage_mode",            str(form.get("homepage_mode",            "all_albums") or "all_albums"))
    _upsert(db, "homepage_album_id",        str(form.get("homepage_album_id",        "") or ""))
    _upsert(db, "homepage_page_id",         str(form.get("homepage_page_id",         "") or ""))
    _upsert(db, "homepage_photo_id",        str(form.get("homepage_photo_id",        "") or ""))
    _upsert(db, "homepage_rotation",        str(form.get("homepage_rotation",        "reload") or "reload"))
    _upsert(db, "homepage_selected_albums", str(form.get("homepage_selected_albums", "") or ""))
    db.commit()
    current = _get_settings_map(db)
    return _template_ctx(request, admin, db, current, homepage_saved=True)


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
    current      = _get_settings_map(db)
    cur_username = _current_username(db)

    if not authenticate_admin(cur_username, current_pw):
        return _template_ctx(request, admin, db, current, account_error="Current password is incorrect.")
    if new_pw:
        if new_pw != confirm_pw:
            return _template_ctx(request, admin, db, current, account_error="New passwords do not match.")
        if len(new_pw) < 6:
            return _template_ctx(request, admin, db, current, account_error="New password must be at least 6 characters.")
    if new_username and len(new_username) < 2:
        return _template_ctx(request, admin, db, current, account_error="Username must be at least 2 characters.")
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
    current = _get_settings_map(db)
    resp = _template_ctx(request, cur_username, db, current, account_saved=True)
    resp.set_cookie(
        key="admin_token", value=token,
        httponly=True, max_age=60 * 60 * 24 * 7, samesite="lax",
    )
    return resp
