# Import all models so SQLAlchemy registers them with Base.metadata
from app.models.album import Album
from app.models.media import Media
from app.models.page import Page
from app.models.menu import MenuItem
from app.models.job import Job
from app.models.setting import Setting

__all__ = ["Album", "Media", "Page", "MenuItem", "Job", "Setting"]
