"""
Conversion Pipeline — Background worker.
Deletes old web/thumb files before re-converting.
Auto-sets album cover if album has no cover yet.
"""
from __future__ import annotations


def _try_auto_cover(db, media_id: int, thumb_path: str) -> None:
    """
    If the converted media belongs to one or more albums that have no
    cover_thumb_path yet, set this thumbnail as their cover automatically.
    """
    try:
        from sqlalchemy import text
        from app.models.album import Album

        # Find all albums this media belongs to
        rows = db.execute(
            text("SELECT album_id FROM album_media WHERE media_id = :mid"),
            {"mid": media_id},
        ).fetchall()

        for row in rows:
            album = db.query(Album).filter(Album.id == row[0]).first()
            if album and not album.cover_thumb_path:
                album.cover_thumb_path = thumb_path

        db.commit()
    except Exception:
        pass  # Auto-cover is best-effort; never break the main pipeline


def convert_media_bg(media_id: int, job_id: str) -> None:
    """Background task: convert one media file. Uses its own DB session."""
    from pathlib import Path

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

    def _delete_old_file(rel_path: str | None) -> None:
        if not rel_path:
            return
        try:
            Path(cfg.media_path, rel_path).unlink(missing_ok=True)
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

        # Delete old web/thumb files (handles format change e.g. .webp → .jpg)
        _delete_old_file(m.web_path)
        _delete_old_file(m.thumb_path)

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

        # Auto-set album cover if this album has none yet
        if m.thumb_path:
            _try_auto_cover(db, media_id, m.thumb_path)

    except Exception as exc:
        db.rollback()
        _mark_error(exc)
    finally:
        db.close()
