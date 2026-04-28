from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import Base, SessionLocal, engine

settings = get_settings()

# ── Ensure data directories exist ──────────────────────────────
for _d in [
    settings.originals_path, settings.media_path,
    settings.zips_path, str(Path(settings.db_path).parent),
    "app/static/css", "app/static/js", "app/static/fonts",
]:
    Path(_d).mkdir(parents=True, exist_ok=True)

# ── Register all models with SQLAlchemy ───────────────────────
from app.models import album, job, media, menu, page, setting  # noqa: F401


def _seed_settings() -> None:
    from app.models.setting import DEFAULT_SETTINGS, Setting
    db = SessionLocal()
    try:
        for key, (value, desc) in DEFAULT_SETTINGS.items():
            if not db.query(Setting).filter(Setting.key == key).first():
                db.add(Setting(key=key, value=value, description=desc))
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _seed_settings()
    yield
    from app.services import job_runner
    job_runner.shutdown(wait=False)


# ── Application ──────────────────────────────────────────
app = FastAPI(
    title="Don Macaron Gallery",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.debug else None,
    redoc_url=None,
)

# ── Static + Media ───────────────────────────────────────
app.mount("/static", StaticFiles(directory="app/static"),       name="static")
app.mount("/media",  StaticFiles(directory=settings.media_path), name="media")

# ── Admin routers ───────────────────────────────────────
from app.routers.admin import albums        as adm_albums
from app.routers.admin import auth          as adm_auth
from app.routers.admin import cleanup       as adm_cleanup
from app.routers.admin import dashboard     as adm_dashboard
from app.routers.admin import folder_import as adm_folder
from app.routers.admin import jobs          as adm_jobs
from app.routers.admin import media         as adm_media
from app.routers.admin import menu          as adm_menu
from app.routers.admin import pages         as adm_pages
from app.routers.admin import settings      as adm_settings
from app.routers.admin import upload        as adm_upload

# ── Public routers ──────────────────────────────────────
from app.routers.public import downloads as pub_downloads
from app.routers.public import gallery   as pub_gallery
from app.routers.public import pages     as pub_pages

# Public
app.include_router(pub_gallery.router)
app.include_router(pub_pages.router)
app.include_router(pub_downloads.router)

# Admin
app.include_router(adm_auth.router,      prefix="/admin")
app.include_router(adm_dashboard.router, prefix="/admin")
app.include_router(adm_albums.router,    prefix="/admin")
app.include_router(adm_media.router,     prefix="/admin")
app.include_router(adm_upload.router,    prefix="/admin")
app.include_router(adm_jobs.router,      prefix="/admin")
app.include_router(adm_folder.router,    prefix="/admin")
app.include_router(adm_pages.router,     prefix="/admin")
app.include_router(adm_menu.router,      prefix="/admin")
app.include_router(adm_settings.router,  prefix="/admin")
app.include_router(adm_cleanup.router,   prefix="/admin")


@app.get("/admin", include_in_schema=False)
async def admin_root():
    return RedirectResponse(url="/admin/dashboard")


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "app": settings.site_title, "version": "1.0.0-complete"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Suppress 404 for favicon requests."""
    from fastapi.responses import Response
    return Response(status_code=204)
