"""
Image Processor Service — Phase 2
Pillow-based conversion: original → 2K WebP + thumbnail WebP
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

# ── Supported extension sets ───────────────────────────────────────
PHOTO_EXT = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp", ".heic"}
GIF_EXT   = {".gif"}
VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".wmv"}
AUDIO_EXT = {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".opus"}


def get_media_type(filename: str) -> str:
    """Return 'photo' | 'gif' | 'video' | 'audio' from filename extension."""
    ext = Path(filename).suffix.lower()
    if ext in PHOTO_EXT:
        return "photo"
    if ext in GIF_EXT:
        return "gif"
    if ext in VIDEO_EXT:
        return "video"
    if ext in AUDIO_EXT:
        return "audio"
    return "photo"  # fallback


def _resize_longest(img, max_px: int):
    """Resize image so its longest side equals max_px. Never upscales."""
    from PIL import Image
    w, h = img.size
    if max(w, h) <= max_px:
        return img.copy()
    scale = max_px / max(w, h)
    return img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)


def _extract_exif(img) -> Optional[str]:
    """Extract safe EXIF fields as JSON string, or None."""
    try:
        from PIL import ExifTags
        raw = img._getexif()
        if not raw:
            return None
        data: dict = {}
        for tag_id, value in raw.items():
            tag = ExifTags.TAGS.get(tag_id, str(tag_id))
            # Keep only primitive, short values (skip binary blobs)
            if isinstance(value, (str, int, float)) and len(str(value)) < 250:
                data[tag] = value
        return json.dumps(data) if data else None
    except Exception:
        return None


def process_image(
    original_path: str,
    media_dir: str,
    media_id: int,
    max_web_px: int = 2048,
    thumb_px: int = 400,
    web_quality: int = 85,
    thumb_quality: int = 80,
) -> dict:
    """
    Convert uploaded image to:
      ─ Web version:  longest side = max_web_px (default 2048), WebP q=85
      ─ Thumbnail:    longest side = thumb_px   (default 400),  WebP q=80

    Returns dict with web_path, thumb_path, width, height, file_size_web, exif_json.
    Paths are RELATIVE to media_dir.
    """
    from PIL import Image, ImageOps

    orig = Path(original_path)
    photos_dir = Path(media_dir) / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(orig) as img:
        # Auto-fix EXIF orientation (portrait shots, etc.)
        img = ImageOps.exif_transpose(img)

        exif_json = _extract_exif(img)
        orig_w, orig_h = img.size

        # Convert to RGB (handles RGBA, palette, greyscale, CMYK, etc.)
        if img.mode not in ("RGB",):
            img = img.convert("RGB")

        # ── Web version (2K) ──
        web_img = _resize_longest(img, max_web_px)
        web_file = f"{media_id}_web.webp"
        web_path = photos_dir / web_file
        web_img.save(str(web_path), "WEBP", quality=web_quality, method=6)

        # ── Thumbnail ──
        thumb_img = _resize_longest(img, thumb_px)
        thumb_file = f"{media_id}_thumb.webp"
        thumb_path = photos_dir / thumb_file
        thumb_img.save(str(thumb_path), "WEBP", quality=thumb_quality, method=6)

    return {
        "web_path":      f"photos/{web_file}",
        "thumb_path":    f"photos/{thumb_file}",
        "width":         orig_w,
        "height":        orig_h,
        "file_size_web": web_path.stat().st_size,
        "exif_json":     exif_json,
        "duration_seconds": None,
    }


def process_gif(
    original_path: str,
    media_dir: str,
    media_id: int,
    thumb_px: int = 400,
    thumb_quality: int = 80,
) -> dict:
    """
    GIF processing: extract first frame as thumbnail only.
    Original GIF stays as-is (no re-encoding to preserve animation).
    """
    from PIL import Image

    orig = Path(original_path)
    photos_dir = Path(media_dir) / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(orig) as img:
        orig_w, orig_h = img.size
        # Extract first frame for thumbnail
        first_frame = img.convert("RGBA").convert("RGB")
        thumb_img = _resize_longest(first_frame, thumb_px)
        thumb_file = f"{media_id}_thumb.webp"
        thumb_path = photos_dir / thumb_file
        thumb_img.save(str(thumb_path), "WEBP", quality=thumb_quality, method=6)

    return {
        "web_path":      None,        # GIF: serve original directly
        "thumb_path":    f"photos/{thumb_file}",
        "width":         orig_w,
        "height":        orig_h,
        "file_size_web": None,
        "exif_json":     None,
        "duration_seconds": None,
    }
