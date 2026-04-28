"""
Public Pages Router — Phase 4
Renders published pages at /p/{slug}.
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.menu import MenuItem
from app.models.page import Page
from app.models.setting import Setting

router = APIRouter(tags=["public-pages"])
templates = Jinja2Templates(directory="app/templates")


def _site_ctx(db: Session) -> dict:
    rows = db.query(Setting).all()
    ctx  = {s.key: s.value for s in rows}
    ctx.setdefault("site_title",             "Gallery")
    ctx.setdefault("theme_bg_color",         "#0a0a0a")
    ctx.setdefault("theme_fg_color",         "#33ff33")
    ctx.setdefault("theme_accent_color",     "#ff6600")
    ctx.setdefault("theme_scanline_opacity", "0.05")
    ctx.setdefault("theme_font",             "VT323")
    ctx.setdefault("social_telegram_url",    "")
    ctx.setdefault("social_instagram_url",   "")
    return ctx


def _get_menu(db: Session) -> list:
    return (
        db.query(MenuItem)
        .filter(MenuItem.is_visible == True, MenuItem.parent_id == None)
        .order_by(MenuItem.sort_order)
        .all()
    )


@router.get("/p/{slug}", response_class=HTMLResponse)
async def page_view(slug: str, request: Request, db: Session = Depends(get_db)):
    site = _site_ctx(db)
    menu = _get_menu(db)

    page = db.query(Page).filter(Page.slug == slug, Page.is_published == True).first()
    if not page:
        return templates.TemplateResponse(request, "public/404.html", {
            "site": site, "site_title": site["site_title"], "menu": menu,
        }, status_code=404)

    return templates.TemplateResponse(request, "public/page.html", {
        "site":       site,
        "site_title": site["site_title"],
        "menu":       menu,
        "page":       page,
    })
