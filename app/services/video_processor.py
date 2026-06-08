"""
Video Processor Service — Phase 2
ffmpeg via subprocess: extract thumbnail frame → WebP
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


def _run_ffprobe(original_path: str) -> tuple[float, int, int]:
    """Return (duration_sec, width, height) via ffprobe. Returns (0, 0, 0) on failure."""
    try:
        import json
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_streams", "-show_format",
                original_path,
            ],
            capture_output=True, text=True, timeout=30,
        )
        data = json.loads(result.stdout)
        duration = float(data.get("format", {}).get("duration", 0))
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                return duration, int(stream.get("width", 0)), int(stream.get("height", 0))
        return duration, 0, 0
    except Exception:
        return 0.0, 0, 0


def process_video(
    original_path: str,
    media_dir: str,
    media_id: int,
    thumb_px: int = 400,
    thumb_quality: int = 80,
) -> dict:
    """
    Extract a thumbnail frame from a video at t=1s (or 10% in).
    Saves as WebP thumbnail.

    Returns dict with thumb_path, width, height, duration_seconds.
    """
    orig = Path(original_path)
    videos_dir = Path(media_dir) / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    duration, width, height = _run_ffprobe(str(orig))
    seek_time = min(1.0, duration * 0.1) if duration > 0.5 else 0.0

    # Extract as JPEG first (widely supported by ffmpeg), then convert to WebP with Pillow
    jpg_path  = videos_dir / f"{media_id}_thumb_tmp.jpg"
    webp_file = f"{media_id}_thumb.webp"
    webp_path = videos_dir / webp_file

    thumb_file: Optional[str] = None

    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(seek_time),
                "-i", str(orig),
                "-vframes", "1",
                "-vf", f"scale={thumb_px}:-1",
                str(jpg_path),
            ],
            capture_output=True, timeout=60,
        )

        if jpg_path.exists() and jpg_path.stat().st_size > 0:
            # Convert to WebP via Pillow for consistency with photos
            try:
                from PIL import Image
                with Image.open(jpg_path) as img:
                    img = img.convert("RGB")
                    img.save(str(webp_path), "WEBP", quality=thumb_quality, method=4)
                jpg_path.unlink(missing_ok=True)
                thumb_file = webp_file
            except Exception:
                # Pillow unavailable / failed — keep the jpg
                thumb_file = f"{media_id}_thumb_tmp.jpg"
    except Exception:
        pass  # ffmpeg not installed or failed — thumb_file stays None

    # Transcode to H.264 MP4 for web playback
    mp4_file = f"{media_id}_web.mp4"
    mp4_path  = videos_dir / mp4_file
    web_path_result: Optional[str] = None

    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(orig),
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart",
                str(mp4_path),
            ],
            capture_output=True, timeout=300,
        )
        if mp4_path.exists() and mp4_path.stat().st_size > 0:
            web_path_result = f"videos/{mp4_file}"
    except Exception:
        pass

    return {
        "web_path":         web_path_result,
        "thumb_path":       f"videos/{thumb_file}" if thumb_file else None,
        "width":            width or None,
        "height":           height or None,
        "file_size_web":    mp4_path.stat().st_size if mp4_path.exists() else None,
        "exif_json":        None,
        "duration_seconds": duration or None,
    }
