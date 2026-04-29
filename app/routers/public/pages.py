from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.page import Page
from app.models.setting import Setting
# Re-use the same get_menu/get_site_ctx from gallery router
from app.routers.public.gallery import get_menu, get_site_ctx

router = APIRouter(tags=["public-pages"])
templates = Jinja2Templates(directory="app/templates")
settings_obj = get_settings()


@router.get("/p/{slug}", response_class=HTMLResponse)
async def page_view(slug: str, request: Request, db: Session = Depends(get_db)):
    site = get_site_ctx(db)
    menu = get_menu(db)

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
