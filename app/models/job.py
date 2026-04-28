from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Job(Base):
    """Background task tracker: image conversion, ZIP building, folder scans."""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)  # UUID string

    # zip | conversion | folder_scan
    job_type = Column(String, nullable=False, index=True)

    # pending | running | done | error
    status = Column(String, default="pending", index=True)

    target_id = Column(Integer, nullable=True)   # e.g. album_id for zip jobs
    target_type = Column(String, nullable=True)  # album | media

    result_path = Column(String, nullable=True)  # output file when done

    progress = Column(Integer, default=0)        # 0-100
    total_items = Column(Integer, default=0)
    done_items = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
