from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)

    # page | album | external
    item_type = Column(String, nullable=False, default="external")

    page_id = Column(Integer, ForeignKey("pages.id", ondelete="SET NULL"), nullable=True)
    album_id = Column(Integer, ForeignKey("albums.id", ondelete="SET NULL"), nullable=True)
    ext_url = Column(String, nullable=True)

    # Self-referential: nested menus (1 level deep recommended)
    parent_id = Column(Integer, ForeignKey("menu_items.id", ondelete="SET NULL"), nullable=True)

    sort_order = Column(Integer, default=0)
    is_visible = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    page = relationship("Page", back_populates="menu_items")
    album = relationship("Album", back_populates="menu_items")
    parent = relationship("MenuItem", remote_side=[id], back_populates="children")
    children = relationship("MenuItem", back_populates="parent")
