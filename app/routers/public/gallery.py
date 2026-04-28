from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.album import Album
from app.models.media import Media
from app.models.menu import MenuItem
from app.models.setting import Setting

router = APIRouter(tags=["public"])
templates = Jinja2Templates(directory="app/templates")
settings_obj = get_settings()


def get_site_ctx(db: Session) -> dict:
    rows = db.query(Setting).all()
    ctx = {s.key: s.value for s in rows}
    ctx.setdefault("site_title",             settings_obj.site_title)
    ctx.setdefault("site_tagline",           settings_obj.site_tagline)
    ctx.setdefault("theme_bg_color",         "#0a0a0a")
    ctx.setdefault("theme_fg_color",         "#33ff33")
    ctx.setdefault("theme_accent_color",     "#ff6600")
    ctx.setdefault("theme_scanline_opacity", "0.05")
    ctx.setdefault("theme_font",             "VT323")
    ctx.setdefault("social_telegram_url",    "")
    ctx.setdefault("social_instagram_url",   "")
    return ctx


def get_menu(db: Session) -> list:
    return (
        db.query(MenuItem)
        .filter(MenuItem.is_visible == True, MenuItem.parent_id == None)
        .order_by(MenuItem.sort_order)
        .all()
    )


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    site = get_site_ctx(db)
    menu = get_menu(db)

    featured_id = site.get("homepage_album_id", "")
    if featured_id and str(featured_id).isdigit():
        featured = db.query(Album).filter(
            Album.id == int(featured_id), Album.is_public == True
        ).first()
        if featured:
            media_items = db.query(Media).filter(
                Media.album_id == featured.id,
                Media.conversion_status == "done",
            ).order_by(Media.sort_order, Media.created_at).all()
            return templates.TemplateResponse(request, "public/home.html", {
                "site": site, "site_title": site["site_title"],
                "menu": menu, "albums": [],
                "featured_album": featured, "media_items": media_items,
            })

    albums = (
        db.query(Album)
        .filter(Album.is_public == True, Album.parent_id == None)
        .order_by(Album.sort_order, Album.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(request, "public/home.html", {
        "site": site, "site_title": site["site_title"],
        "menu": menu, "albums": albums,
        "featured_album": None, "media_items": [],
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

    media_items = (
        db.query(Media)
        .filter(Media.album_id == album.id, Media.conversion_status == "done")
        .order_by(Media.sort_order, Media.created_at)
        .all()
    )
    sub_albums = (
        db.query(Album)
        .filter(Album.parent_id == album.id, Album.is_public == True)
        .order_by(Album.sort_order)
        .all()
    )
    breadcrumb = []
    if album.parent_id:
        parent = db.query(Album).filter(Album.id == album.parent_id).first()
        if parent:
            breadcrumb.append({"title": parent.title, "slug": parent.slug})

    return templates.TemplateResponse(request, "public/album.html", {
        "site": site, "site_title": site["site_title"],
        "menu": menu, "album": album,
        "media_items": media_items,
        "sub_albums": sub_albums,
        "breadcrumb": breadcrumb,
    })


@router.get("/s/{token}", response_class=HTMLResponse)
async def shared_album(token: str, request: Request, db: Session = Depends(get_db)):
    site = get_site_ctx(db)
    menu = get_menu(db)

    album = db.query(Album).filter(Album.share_token == token).first()
    if not album:
        return templates.TemplateResponse(request, "public/404.html", {
            "site": site, "site_title": site["site_title"], "menu": menu,
        }, status_code=404)

    media_items = (
        db.query(Media)
        .filter(Media.album_id == album.id, Media.conversion_status == "done")
        .order_by(Media.sort_order, Media.created_at)
        .all()
    )
    return templates.TemplateResponse(request, "public/album.html", {
        "site": site, "site_title": site["site_title"],
        "menu": menu, "album": album,
        "media_items": media_items,
        "sub_albums": [], "breadcrumb": [],
        "is_shared": True,
    })
