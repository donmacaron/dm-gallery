import hashlib
from datetime import date
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.album import Album
from app.models.media import Media
from app.models.menu import MenuItem
from app.models.page import Page
from app.models.setting import Setting

router = APIRouter(tags=["public"])
templates = Jinja2Templates(directory="app/templates")
settings_obj = get_settings()


def get_site_ctx(db: Session) -> dict:
    rows = db.query(Setting).all()
    ctx  = {s.key: s.value for s in rows}
    ctx.setdefault("site_title",               settings_obj.site_title)
    ctx.setdefault("site_tagline",             settings_obj.site_tagline)
    ctx.setdefault("header_logo_text",         "")
    ctx.setdefault("header_show_tagline",      "0")
    ctx.setdefault("header_bg_color",          "")
    ctx.setdefault("header_border_color",      "")
    ctx.setdefault("header_text_color",        "")
    ctx.setdefault("album_names_always",       "0")
    ctx.setdefault("theme_bg_color",           "#0a0a0a")
    ctx.setdefault("theme_fg_color",           "#33ff33")
    ctx.setdefault("theme_accent_color",       "#ff6600")
    ctx.setdefault("theme_scanline_opacity",   "0.05")
    ctx.setdefault("theme_font",               "VT323")
    ctx.setdefault("social_telegram_url",      "")
    ctx.setdefault("social_instagram_url",     "")
    ctx.setdefault("homepage_mode",            "all_albums")
    ctx.setdefault("homepage_album_id",        "")
    ctx.setdefault("homepage_selected_albums", "")
    ctx.setdefault("homepage_page_id",         "")
    ctx.setdefault("homepage_photo_id",        "")
    ctx.setdefault("homepage_rotation",        "reload")
    ctx.setdefault("footer_bg_color",          "")
    ctx.setdefault("footer_fg_color",          "")
    ctx.setdefault("footer_border_color",      "")
    return ctx


def get_menu(db: Session) -> list:
    items = (
        db.query(MenuItem)
        .filter(MenuItem.is_visible == True, MenuItem.parent_id == None)
        .order_by(MenuItem.sort_order)
        .all()
    )
    result = []
    for item in items:
        if item.item_type == "album" and item.album_id:
            album = db.query(Album).filter(
                Album.id == item.album_id, Album.is_public == True
            ).first()
            if album:
                result.append({"label": item.label, "url": f"/a/{album.slug}", "external": False})
        elif item.item_type == "page" and item.page_id:
            page = db.query(Page).filter(
                Page.id == item.page_id, Page.is_published == True
            ).first()
            if page:
                result.append({"label": item.label, "url": f"/p/{page.slug}", "external": False})
        elif item.item_type == "external" and item.ext_url:
            result.append({"label": item.label, "url": item.ext_url, "external": True})
        elif item.item_type == "all_albums":
            result.append({"label": item.label, "url": "/albums", "external": False})
    return result


def get_album_media(db: Session, album_id: int) -> list:
    rows = db.execute(
        text("""
            SELECT m.* FROM media m
            JOIN album_media am ON am.media_id = m.id
            WHERE am.album_id = :album_id
              AND m.conversion_status = 'done'
            ORDER BY am.sort_order, am.added_at
        """),
        {"album_id": album_id},
    ).mappings().all()
    media_ids = [r["id"] for r in rows]
    if not media_ids:
        return []
    objs = db.query(Media).filter(Media.id.in_(media_ids)).all()
    order_map = {mid: i for i, mid in enumerate(media_ids)}
    return sorted(objs, key=lambda m: order_map.get(m.id, 9999))


def _pick_rotation_photo(media_items: list, rotation: str) -> "Media | None":
    """Pick one photo deterministically based on rotation setting."""
    if not media_items:
        return None
    if rotation == "reload":
        import random
        return random.choice(media_items)
    # Date-based seed: everyone sees the same photo on the same day/week/month
    today = date.today()
    if rotation == "daily":
        seed_str = today.isoformat()
    elif rotation == "weekly":
        # Use ISO week
        seed_str = f"{today.isocalendar()[0]}-W{today.isocalendar()[1]:02d}"
    elif rotation == "monthly":
        seed_str = f"{today.year}-{today.month:02d}"
    else:
        seed_str = today.isoformat()
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    return media_items[seed % len(media_items)]


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    site = get_site_ctx(db)
    menu = get_menu(db)
    mode = site.get("homepage_mode", "all_albums")

    # ── MODE: all_albums ──
    if mode == "all_albums":
        albums = (
            db.query(Album)
            .filter(Album.is_public == True, Album.parent_id == None)
            .order_by(Album.sort_order, Album.created_at.desc())
            .all()
        )
        return templates.TemplateResponse(request, "public/home.html", {
            "site": site, "site_title": site["site_title"], "menu": menu,
            "mode": "all_albums", "albums": albums,
        })

    # ── MODE: selected_albums ──
    elif mode == "selected_albums":
        ids_str = site.get("homepage_selected_albums", "")
        ids = [int(x) for x in ids_str.split(",") if x.strip().isdigit()]
        if ids:
            all_albums = db.query(Album).filter(
                Album.id.in_(ids), Album.is_public == True
            ).all()
            # Sort by the order they were saved in settings
            order_map = {aid: i for i, aid in enumerate(ids)}
            albums = sorted(all_albums, key=lambda a: order_map.get(a.id, 999))
        else:
            albums = []
        return templates.TemplateResponse(request, "public/home.html", {
            "site": site, "site_title": site["site_title"], "menu": menu,
            "mode": "selected_albums", "albums": albums,
        })

    # ── MODE: page ──
    elif mode == "page":
        page_id = site.get("homepage_page_id", "")
        page = None
        if page_id and str(page_id).isdigit():
            page = db.query(Page).filter(
                Page.id == int(page_id), Page.is_published == True
            ).first()
        return templates.TemplateResponse(request, "public/home.html", {
            "site": site, "site_title": site["site_title"], "menu": menu,
            "mode": "page", "page": page,
        })

    # ── MODE: random_photo ──
    elif mode == "random_photo":
        album_id = site.get("homepage_album_id", "")
        photo = None
        if album_id and str(album_id).isdigit():
            media_items = get_album_media(db, int(album_id))
            rotation    = site.get("homepage_rotation", "reload")
            photo       = _pick_rotation_photo(media_items, rotation)
        return templates.TemplateResponse(request, "public/home.html", {
            "site": site, "site_title": site["site_title"], "menu": menu,
            "mode": "random_photo", "photo": photo,
        })

    # ── MODE: specific_photo ──
    elif mode == "specific_photo":
        photo_id = site.get("homepage_photo_id", "")
        photo = None
        if photo_id and str(photo_id).isdigit():
            photo = db.query(Media).filter(
                Media.id == int(photo_id),
                Media.conversion_status == "done"
            ).first()
        return templates.TemplateResponse(request, "public/home.html", {
            "site": site, "site_title": site["site_title"], "menu": menu,
            "mode": "specific_photo", "photo": photo,
        })

    # Fallback
    albums = (
        db.query(Album)
        .filter(Album.is_public == True, Album.parent_id == None)
        .order_by(Album.sort_order, Album.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(request, "public/home.html", {
        "site": site, "site_title": site["site_title"], "menu": menu,
        "mode": "all_albums", "albums": albums,
    })


@router.get("/albums", response_class=HTMLResponse)
async def all_albums_view(request: Request, db: Session = Depends(get_db)):
    site   = get_site_ctx(db)
    menu   = get_menu(db)
    albums = (
        db.query(Album)
        .filter(Album.is_public == True, Album.parent_id == None)
        .order_by(Album.sort_order, Album.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(request, "public/home.html", {
        "site": site, "site_title": site["site_title"], "menu": menu,
        "mode": "all_albums", "albums": albums,
    })


@router.get("/a/{slug}", response_class=HTMLResponse)
async def album_view(slug: str, request: Request, db: Session = Depends(get_db)):
    site = get_site_ctx(db)
    menu = get_menu(db)
    album = db.query(Album).filter(Album.slug == slug, Album.is_public == True).first()
    if not album:
        return templates.TemplateResponse(request, "public/404.html", {
            "site": site, "site_title": site["site_title"], "menu": menu,
        }, status_code=404)
    media_items = get_album_media(db, album.id)
    sub_albums  = (
        db.query(Album)
        .filter(Album.parent_id == album.id, Album.is_public == True)
        .order_by(Album.sort_order).all()
    )
    breadcrumb = []
    if album.parent_id:
        parent = db.query(Album).filter(Album.id == album.parent_id).first()
        if parent:
            breadcrumb.append({"title": parent.title, "slug": parent.slug})
    return templates.TemplateResponse(request, "public/album.html", {
        "site": site, "site_title": site["site_title"],
        "menu": menu, "album": album,
        "media_items": media_items, "sub_albums": sub_albums, "breadcrumb": breadcrumb,
    })


@router.get("/s/{token}", response_class=HTMLResponse)
async def shared_album(token: str, request: Request, db: Session = Depends(get_db)):
    site  = get_site_ctx(db)
    menu  = get_menu(db)
    album = db.query(Album).filter(Album.share_token == token).first()
    if not album:
        return templates.TemplateResponse(request, "public/404.html", {
            "site": site, "site_title": site["site_title"], "menu": menu,
        }, status_code=404)
    media_items = get_album_media(db, album.id)
    return templates.TemplateResponse(request, "public/album.html", {
        "site": site, "site_title": site["site_title"],
        "menu": menu, "album": album,
        "media_items": media_items, "sub_albums": [], "breadcrumb": [],
        "is_shared": True,
    })