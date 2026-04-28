"""
Folder Scanner Service — Phase 3
Scans a local directory and imports all media as a new album.
"""
from __future__ import annotations
import shutil
import uuid
from pathlib import Path

SUPPORTED = {
    "photo": {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp"},
    "gif":   {".gif"},
    "video": {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"},
    "audio": {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a"},
}


def scan_folder(folder_path: str) -> dict:
    """Scan folder, return categorised file list."""
    path = Path(folder_path).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise ValueError(f"Folder not found: {folder_path}")

    result: dict = {"photos": [], "gifs": [], "videos": [], "audio": [], "other": []}
    for f in sorted(path.iterdir()):
        if not f.is_file() or f.name.startswith("."):
            continue
        ext = f.suffix.lower()
        matched = False
        for mtype, exts in SUPPORTED.items():
            if ext in exts:
                key = "gifs" if mtype == "gif" else f"{mtype}s"
                result[key].append(str(f))
                matched = True
                break
        if not matched:
            result["other"].append(str(f))

    result["total"] = sum(len(v) for k, v in result.items() if k not in ("total", "other"))
    return result


def import_folder(
    folder_path: str,
    album_title: str,
    originals_path: str,
    parent_id: int | None = None,
) -> dict:
    """
    Import all media from a folder:
    1. Scan folder
    2. Create album in DB
    3. Copy files to originals storage
    4. Create Media records + Job records
    5. Submit background conversions via job_runner

    Returns {album_id, total, job_ids, album_slug}
    """
    from app.database import SessionLocal
    from app.models.album import Album
    from app.models.job import Job
    from app.models.media import Media
    from app.services import job_runner
    from app.services.conversion_pipeline import convert_media_bg
    from app.services.image_processor import get_media_type
    from slugify import slugify

    scanned   = scan_folder(folder_path)
    all_files = scanned["photos"] + scanned["gifs"] + scanned["videos"] + scanned["audio"]

    if not all_files:
        raise ValueError("No supported media files found in folder")

    orig_dir = Path(originals_path)
    orig_dir.mkdir(parents=True, exist_ok=True)

    db      = SessionLocal()
    job_ids = []

    try:
        # Unique slug
        base_slug = slugify(album_title) or "imported-album"
        slug = base_slug
        counter = 1
        while db.query(Album).filter(Album.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        album = Album(
            slug      = slug,
            title     = album_title.strip(),
            is_public = False,
            parent_id = parent_id,
        )
        db.add(album)
        db.flush()  # get album.id

        for file_path_str in all_files:
            src = Path(file_path_str)
            if not src.exists():
                continue

            ext    = src.suffix.lower()
            unique = uuid.uuid4().hex
            dest   = orig_dir / f"{unique}{ext}"
            shutil.copy2(str(src), str(dest))

            mtype = get_media_type(src.name)
            media = Media(
                original_filename  = src.name,
                slug               = uuid.uuid4().hex[:16],
                media_type         = mtype,
                album_id           = album.id,
                original_path      = str(dest),
                file_size_original = dest.stat().st_size,
                conversion_status  = "pending",
                sort_order         = 0,
            )
            db.add(media)
            db.flush()  # get media.id

            job_id = uuid.uuid4().hex
            job    = Job(
                id          = job_id,
                job_type    = "conversion",
                status      = "pending",
                target_id   = media.id,
                target_type = "media",
                total_items = 1,
                done_items  = 0,
                progress    = 0,
            )
            db.add(job)
            job_ids.append(job_id)
            job_runner.submit(convert_media_bg, media.id, job_id)

        db.commit()
        return {
            "album_id":   album.id,
            "album_slug": album.slug,
            "total":      len(all_files),
            "job_ids":    job_ids,
        }

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
