from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Album(Base):
    __tablename__ = "albums"

    id               = Column(Integer, primary_key=True, index=True)
    slug             = Column(String, unique=True, nullable=False, index=True)
    title            = Column(String, nullable=False)
    description      = Column(Text, nullable=True)
    parent_id        = Column(Integer, nullable=True, index=True)
    cover_thumb_path = Column(String, nullable=True)
    dominant_color   = Column(String(7), nullable=True)  # hex e.g. #a3c4f1
    is_public        = Column(Boolean, default=False, index=True)
    share_token      = Column(String, unique=True, nullable=True, index=True)
    sort_order       = Column(Integer, default=0)
    auto_zip         = Column(Boolean, default=False)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())

    media_items = relationship(
        "Media",
        secondary="album_media",
        back_populates="albums",
        lazy="select",
    )
    menu_items = relationship("MenuItem", back_populates="album")
