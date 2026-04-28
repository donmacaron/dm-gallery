from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)

    # Quill.js output
    content_html = Column(Text, nullable=True)   # rendered HTML for display
    content_delta = Column(Text, nullable=True)  # Quill Delta JSON for re-editing

    is_published = Column(Boolean, default=False, index=True)
    cover_url = Column(String, nullable=True)  # optional header image URL
    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    menu_items = relationship("MenuItem", back_populates="page")
