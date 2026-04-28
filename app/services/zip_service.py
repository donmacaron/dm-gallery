"""
ZIP Service — Phase 3
Pre-builds ZIP archives of album originals in the background.
Progress tracked in jobs table.
"""
from __future__ import annotations
import zipfile
from pathlib import Path


def build_album_zip(album_id: int, job_id: str, zips_path: str) -> str:
    """
    Stream all originals in an album into a ZIP file.
    Updates job.progress + job.done_items during build.
    Returns path to created ZIP file.
    """
    from app.database import SessionLocal
    from app.models.album import Album
    from app.models.job import Job
    from app.models.media import Media
    from slugify import slugify

    db = SessionLocal()
    job = None

    try:
        job   = db.query(Job).filter(Job.id == job_id).first()
        album = db.query(Album).filter(Album.id == album_id).first()

        if not album:
            if job:
                job.status = "error"
                job.error_message = f"Album {album_id} not found"
                db.commit()
            return ""

        media_items = (
            db.query(Media)
            .filter(Media.album_id == album_id, Media.original_path.isnot(None))
            .all()
        )
        total = len(media_items)

        if job:
            job.total_items = total
            job.status      = "running"
            db.commit()

        if total == 0:
            if job:
                job.status        = "error"
                job.error_message = "No original files found in album"
                db.commit()
            return ""

        # Create zip directory and file
        zips_dir = Path(zips_path)
        zips_dir.mkdir(parents=True, exist_ok=True)
        safe_title = slugify(album.title) or f"album_{album_id}"
        zip_path   = zips_dir / f"{safe_title}_{album_id}.zip"

        with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for i, media in enumerate(media_items):
                orig = Path(media.original_path)
                if orig.exists():
                    zf.write(str(orig), arcname=media.original_filename)

                done = i + 1
                if job:
                    job.done_items = done
                    job.progress   = int((done / total) * 100)
                    db.commit()

        # Mark complete
        if job:
            job.status      = "done"
            job.progress    = 100
            job.result_path = str(zip_path)
            db.commit()

        return str(zip_path)

    except Exception as exc:
        db.rollback()
        if job:
            try:
                job.status        = "error"
                job.error_message = str(exc)[:500]
                db.commit()
            except Exception:
                pass
        raise
    finally:
        db.close()
