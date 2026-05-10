"""
Image Processor Service
Pillow-based conversion:
  Web version  — original format preserved, EXIF kept, longest side ≤ 2048px
  Thumbnail    — always WebP 400px, smaller file size for fast grid loading
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp", ".heic"}
GIF_EXT   = {".gif"}
VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".wmv"}
AUDIO_EXT = {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".opus"}

# PIL format name → (save_format, file_extension)
# Formats that Pillow can't save losslessly or that produce huge files
# are downgraded to JPEG.
_FMT_MAP = {
    "JPEG": ("JPEG", ".jpg"),
    "JPG":  ("JPEG", ".jpg"),
    "PNG":  ("PNG",  ".png"),
    "WEBP": ("WEBP", ".webp"),
    "TIFF": ("JPEG", ".jpg"),   # TIFF files are huge
    "TIF":  ("JPEG", ".jpg"),
    "BMP":  ("JPEG", ".jpg"),   # BMP is uncompressed
    "HEIC": ("JPEG", ".jpg"),   # Pillow cannot write HEIC
    "GIF":  ("JPEG", ".jpg"),   # animated GIFs handled separately
}


def get_media_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext in PHOTO_EXT: return "photo"
    if ext in GIF_EXT:   return "gif"
    if ext in VIDEO_EXT: return "video"
    if ext in AUDIO_EXT: return "audio"
    return "photo"


def _resize_longest(img, max_px: int):
    """Resize so longest side == max_px. Never upscales."""
    from PIL import Image
    w, h = img.size
    if max(w, h) <= max_px:
        return img.copy()
    scale = max_px / max(w, h)
    return img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)


def _extract_exif_json(img) -> Optional[str]:
    """Extract safe EXIF fields as JSON string."""
    try:
        from PIL import ExifTags
        raw = img._getexif()
        if not raw:
            return None
        data: dict = {}
        for tag_id, value in raw.items():
            tag = ExifTags.TAGS.get(tag_id, str(tag_id))
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
    thumb_px: int   = 400,
    thumb_quality: int = 80,
) -> dict:
    """
    Convert uploaded image to:
      Web version  — original format (JPEG→JPEG, PNG→PNG, etc.), EXIF preserved
      Thumbnail    — WebP 400px
    """
    from PIL import Image, ImageOps

    orig       = Path(original_path)
    photos_dir = Path(media_dir) / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(orig) as img:
        # Auto-fix EXIF orientation FIRST (portrait shots, rotated frames)
        img = ImageOps.exif_transpose(img)

        orig_w, orig_h = img.size
        src_format = (img.format or "JPEG").upper()

        # Extract EXIF bytes for re-embedding in the saved file
        exif_bytes: bytes = img.info.get("exif", b"")

        # Extract EXIF as JSON for DB storage (for display / search)
        exif_json = _extract_exif_json(img)

        # Determine output format + extension
        save_fmt, web_ext = _FMT_MAP.get(src_format, ("JPEG", ".jpg"))

        # ── Web version (2K) ──────────────────────────────────────
        web_img = _resize_longest(img, max_web_px)

        # Mode conversion only when the target format requires it
        if save_fmt == "JPEG" and web_img.mode not in ("RGB",):
            web_img = web_img.convert("RGB")
            exif_bytes = b""   # EXIF may be invalid after mode change
        elif save_fmt == "PNG" and web_img.mode == "CMYK":
            web_img = web_img.convert("RGB")

        web_file = f"{media_id}_web{web_ext}"
        web_path = photos_dir / web_file

        save_kwargs: dict = {}
        if save_fmt == "JPEG":
            save_kwargs = {"quality": 90, "optimize": True}
            if exif_bytes:
                save_kwargs["exif"] = exif_bytes
        elif save_fmt == "PNG":
            save_kwargs = {"optimize": True}
            # PNG EXIF support depends on Pillow version; attempt it
            if exif_bytes:
                try:
                    save_kwargs["exif"] = exif_bytes
                except Exception:
                    pass
        elif save_fmt == "WEBP":
            save_kwargs = {"quality": 90, "method": 6}
            if exif_bytes:
                save_kwargs["exif"] = exif_bytes

        web_img.save(str(web_path), save_fmt, **save_kwargs)

        # ── Thumbnail (always WebP) ─────────────────────────────────
        # Always convert to RGB for WebP thumbnail (no RGBA/palette issues)
        thumb_src = img.convert("RGB") if img.mode != "RGB" else img
        thumb_img = _resize_longest(thumb_src, thumb_px)
        thumb_file = f"{media_id}_thumb.webp"
        thumb_path = photos_dir / thumb_file
        thumb_img.save(str(thumb_path), "WEBP", quality=thumb_quality, method=6)

    return {
        "web_path":         f"photos/{web_file}",
        "thumb_path":       f"photos/{thumb_file}",
        "width":            orig_w,
        "height":           orig_h,
        "file_size_web":    web_path.stat().st_size,
        "exif_json":        exif_json,
        "duration_seconds": None,
    }


def process_gif(
    original_path: str,
    media_dir: str,
    media_id: int,
    thumb_px: int = 400,
    thumb_quality: int = 80,
) -> dict:
    """GIF: extract first frame as WebP thumbnail. Original served as-is."""
    from PIL import Image

    orig       = Path(original_path)
    photos_dir = Path(media_dir) / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(orig) as img:
        orig_w, orig_h = img.size
        first_frame = img.convert("RGBA").convert("RGB")
        thumb_img = _resize_longest(first_frame, thumb_px)
        thumb_file = f"{media_id}_thumb.webp"
        thumb_path = photos_dir / thumb_file
        thumb_img.save(str(thumb_path), "WEBP", quality=thumb_quality, method=6)

    return {
        "web_path":         None,
        "thumb_path":       f"photos/{thumb_file}",
        "width":            orig_w,
        "height":           orig_h,
        "file_size_web":    None,
        "exif_json":        None,
        "duration_seconds": None,
    }
