"""
Conversion Pipeline — Shared background worker.
Used by upload.py and folder_import.py.
"""
from __future__ import annotations


def convert_media_bg(media_id: int, job_id: str) -> None:
    """Background task: convert one media file. Uses its own DB session."""
    from app.config import get_settings as _gs
    from app.database import SessionLocal
    from app.models.job import Job as _Job
    from app.models.media import Media as _Media
    from app.services.image_processor import process_gif, process_image
    from app.services.video_processor import process_video

    cfg = _gs()
    db  = SessionLocal()

    def _mark_error(exc: Exception) -> None:
        try:
            m = db.query(_Media).filter(_Media.id == media_id).first()
            j = db.query(_Job).filter(_Job.id == job_id).first()
            if m:
                m.conversion_status = "error"
                m.conversion_error  = str(exc)[:500]
            if j:
                j.status        = "error"
                j.error_message = str(exc)[:500]
            db.commit()
        except Exception:
            pass

    try:
        j = db.query(_Job).filter(_Job.id == job_id).first()
        m = db.query(_Media).filter(_Media.id == media_id).first()
        if not m:
            return
        if j:
            j.status = "running"
        m.conversion_status = "processing"
        db.commit()

        if m.media_type == "photo":
            result = process_image(m.original_path, cfg.media_path, m.id)
        elif m.media_type == "gif":
            result = process_gif(m.original_path, cfg.media_path, m.id)
        elif m.media_type == "video":
            result = process_video(m.original_path, cfg.media_path, m.id)
        else:
            result = {
                "web_path": None, "thumb_path": None,
                "width": None,    "height": None,
                "file_size_web": None, "exif_json": None,
                "duration_seconds": None,
            }

        m.web_path          = result.get("web_path")
        m.thumb_path        = result.get("thumb_path")
        m.width             = result.get("width")
        m.height            = result.get("height")
        m.file_size_web     = result.get("file_size_web")
        m.exif_json         = result.get("exif_json")
        m.duration_seconds  = result.get("duration_seconds")
        m.conversion_status = "done"

        if j:
            j.status     = "done"
            j.progress   = 100
            j.done_items = 1

        db.commit()

    except Exception as exc:
        db.rollback()
        _mark_error(exc)
    finally:
        db.close()
