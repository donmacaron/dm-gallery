from sqlalchemy import Column, DateTime, ForeignKey, Integer, Table
from sqlalchemy.sql import func
from app.database import Base

album_media_tbl = Table(
    "album_media",
    Base.metadata,
    Column("album_id",   Integer, ForeignKey("albums.id", ondelete="CASCADE"), primary_key=True),
    Column("media_id",   Integer, ForeignKey("media.id",  ondelete="CASCADE"), primary_key=True),
    Column("sort_order", Integer, default=0),
    Column("added_at",   DateTime(timezone=True), server_default=func.now()),
)
