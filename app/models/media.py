from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)

    # photo | video | gif | audio
    media_type = Column(String, nullable=False, index=True)

    # Album assignment (nullable = unassigned / in global library)
    album_id = Column(Integer, ForeignKey("albums.id", ondelete="SET NULL"), nullable=True, index=True)

    # File paths
    original_path = Column(String, nullable=True)   # full path on originals drive
    web_path = Column(String, nullable=True)         # relative path: thumb/2K webp in media_path
    thumb_path = Column(String, nullable=True)       # relative path: thumbnail webp

    # File metadata
    file_size_original = Column(Integer, nullable=True)  # bytes
    file_size_web = Column(Integer, nullable=True)       # bytes
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration_seconds = Column(Float, nullable=True)      # video/audio

    # Conversion status: pending | processing | done | error
    conversion_status = Column(String, default="pending", index=True)
    conversion_error = Column(Text, nullable=True)

    # EXIF data as JSON string
    exif_json = Column(Text, nullable=True)

    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    album = relationship("Album", back_populates="media_items", foreign_keys=[album_id])
