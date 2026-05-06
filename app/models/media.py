from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Media(Base):
    __tablename__ = "media"

    id                 = Column(Integer, primary_key=True, index=True)
    original_filename  = Column(String, nullable=False)
    slug               = Column(String, unique=True, nullable=False, index=True)
    media_type         = Column(String, nullable=False, index=True)  # photo|video|gif|audio

    # Legacy single-album FK kept for upload flow convenience (nullable)
    album_id           = Column(Integer, ForeignKey("albums.id", ondelete="SET NULL"), nullable=True, index=True)

    original_path      = Column(String, nullable=True)
    web_path           = Column(String, nullable=True)
    thumb_path         = Column(String, nullable=True)
    file_size_original = Column(Integer, nullable=True)
    file_size_web      = Column(Integer, nullable=True)
    width              = Column(Integer, nullable=True)
    height             = Column(Integer, nullable=True)
    duration_seconds   = Column(Float, nullable=True)
    conversion_status  = Column(String, default="pending", index=True)
    conversion_error   = Column(Text, nullable=True)
    exif_json          = Column(Text, nullable=True)
    sort_order         = Column(Integer, default=0)
    created_at         = Column(DateTime(timezone=True), server_default=func.now())
    updated_at         = Column(DateTime(timezone=True), onupdate=func.now())

    # Many-to-many back-reference
    albums = relationship(
        "Album",
        secondary="album_media",
        back_populates="media_items",
        lazy="select",
    )
