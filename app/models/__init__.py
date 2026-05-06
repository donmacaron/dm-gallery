# Import all models so SQLAlchemy registers them with Base.metadata
# Order matters: album_media must be imported AFTER Album and Media
from app.models.album      import Album       # noqa: F401
from app.models.media      import Media       # noqa: F401
from app.models.album_media import album_media_tbl  # noqa: F401
from app.models.page       import Page        # noqa: F401
from app.models.menu       import MenuItem    # noqa: F401
from app.models.job        import Job         # noqa: F401
from app.models.setting    import Setting     # noqa: F401

__all__ = ["Album", "Media", "album_media_tbl", "Page", "MenuItem", "Job", "Setting"]
