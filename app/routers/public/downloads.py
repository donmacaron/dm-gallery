from mimetypes import guess_type
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.job import Job
from app.models.media import Media

router = APIRouter(tags=["public-downloads"])
settings = get_settings()


@router.get("/download/{media_id}/{version}")
async def download_media(media_id: int, version: str, db: Session = Depends(get_db)):
    """
    Download a media file.
    version: 'web'      → 2048px derived file
    version: 'original' → original uploaded file
    """
    from fastapi import HTTPException
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    if version == "web" and media.web_path:
        file_path = Path(settings.media_path) / media.web_path
        if file_path.exists():
            stem = Path(media.original_filename).stem
            media_type = guess_type(file_path.name)[0] or "application/octet-stream"
            return FileResponse(
                path=str(file_path),
                filename=f"{stem}_2k{file_path.suffix.lower()}",
                media_type=media_type,
            )

    elif version == "original" and media.original_path:
        file_path = Path(media.original_path)
        if file_path.exists():
            return FileResponse(path=str(file_path), filename=media.original_filename)

    raise HTTPException(status_code=404, detail="File not found on disk")


@router.get("/download/zip/{album_id}")
async def download_zip(album_id: int, db: Session = Depends(get_db)):
    """Download the latest completed ZIP for an album."""
    from fastapi import HTTPException
    job = (
        db.query(Job)
        .filter(Job.job_type == "zip", Job.target_id == album_id, Job.status == "done")
        .order_by(Job.created_at.desc())
        .first()
    )
    if not job or not job.result_path:
        raise HTTPException(status_code=404, detail="ZIP not built yet")

    zip_path = Path(job.result_path)
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="ZIP file missing from disk")

    return FileResponse(
        path=str(zip_path),
        filename=zip_path.name,
        media_type="application/zip",
    )
