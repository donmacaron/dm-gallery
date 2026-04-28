from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Self-referential: albums within albums
    parent_id = Column(Integer, nullable=True, index=True)  # FK handled manually

    # Cover image: stored as plain path (avoids circular FK with Media)
    cover_thumb_path = Column(String, nullable=True)

    is_public = Column(Boolean, default=False, index=True)
    share_token = Column(String, unique=True, nullable=True, index=True)  # private sharing
    sort_order = Column(Integer, default=0)
    auto_zip = Column(Boolean, default=False)  # pre-build ZIP on upload

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    media_items = relationship(
        "Media",
        back_populates="album",
        foreign_keys="Media.album_id",
        order_by="Media.sort_order, Media.created_at",
    )
    menu_items = relationship("MenuItem", back_populates="album")

    @property
    def media_count(self) -> int:
        return len(self.media_items) if self.media_items else 0
