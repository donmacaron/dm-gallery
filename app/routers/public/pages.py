import re
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.album import Album
from app.models.page import Page
from app.routers.public.gallery import get_menu, get_site_ctx

router = APIRouter(tags=["public-pages"])
templates = Jinja2Templates(directory="app/templates")

# Pattern: [[album:123]]
_ALBUM_SHORTCODE = re.compile(r'\[\[album:(\d+)\]\]')


def _render_album_card(album: Album) -> str:
    """Render an album shortcode as a clean card."""
    cover_html = (
        f'<img src="/media/{album.cover_thumb_path}" '
        f'alt="{album.title}" '
        f'loading="lazy">'
        if album.cover_thumb_path else
        '<div class="album-card-no-img">&#9633;</div>'
    )
    return (
        f'<a href="/a/{album.slug}" class="album-card-embed" title="{album.title}">'
        f'<div class="album-card-embed-img">{cover_html}</div>'
        f'<div class="album-card-embed-title">{album.title}</div>'
        f'</a>'
    )


def _process_shortcodes(html: str, db: Session) -> str:
    """Replace [[album:ID]] shortcodes with rendered HTML cards."""
    if not html or '[[album:' not in html:
        return html

    def replacer(match):
        album_id = int(match.group(1))
        album = db.query(Album).filter(
            Album.id == album_id,
            Album.is_public == True,
        ).first()
        if not album:
            return ''  # Album not found or not public: remove silently
        return _render_album_card(album)

    return _ALBUM_SHORTCODE.sub(replacer, html)


@router.get("/p/{slug}", response_class=HTMLResponse)
async def page_view(slug: str, request: Request, db: Session = Depends(get_db)):
    site = get_site_ctx(db)
    menu = get_menu(db)
    page = db.query(Page).filter(
        Page.slug == slug,
        Page.is_published == True,
    ).first()
    if not page:
        return templates.TemplateResponse(request, "public/404.html", {
            "site": site, "site_title": site["site_title"], "menu": menu,
        }, status_code=404)

    # Process album shortcodes in content
    processed_html = _process_shortcodes(page.content_html or "", db)

    return templates.TemplateResponse(request, "public/page.html", {
        "site": site, "site_title": f"{page.title} \u2014 {site['site_title']}",
        "menu": menu, "page": page,
        "content_html": processed_html,
    })
