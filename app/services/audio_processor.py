"""
Audio Processor Service
ffmpeg-based: transcode to MP3 128kbps for universal browser playback.
Falls back to copying the original if ffmpeg unavailable.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def _get_duration(original_path: str) -> float:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", original_path],
            capture_output=True, text=True, timeout=30,
        )
        data = json.loads(r.stdout)
        return float(data.get("format", {}).get("duration", 0))
    except Exception:
        return 0.0


def process_audio(
    original_path: str,
    media_dir: str,
    media_id: int,
) -> dict:
    """Transcode audio to MP3 128kbps. Falls back to copy if ffmpeg fails."""
    orig = Path(original_path)
    audio_dir = Path(media_dir) / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    duration = _get_duration(original_path)

    mp3_file = f"{media_id}_web.mp3"
    mp3_path  = audio_dir / mp3_file
    web_path  = None

    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(orig),
                "-c:a", "libmp3lame", "-b:a", "128k",
                str(mp3_path),
            ],
            capture_output=True, timeout=120,
        )
        if mp3_path.exists() and mp3_path.stat().st_size > 0:
            web_path = f"audio/{mp3_file}"
    except Exception:
        # Fallback: copy original into media dir as-is
        try:
            ext = orig.suffix.lower()
            copy_file = f"{media_id}_web{ext}"
            copy_path  = audio_dir / copy_file
            shutil.copy2(str(orig), str(copy_path))
            if copy_path.exists():
                web_path = f"audio/{copy_file}"
        except Exception:
            pass

    return {
        "web_path":         web_path,
        "thumb_path":       None,
        "width":            None,
        "height":           None,
        "file_size_web":    mp3_path.stat().st_size if mp3_path.exists() else None,
        "exif_json":        None,
        "duration_seconds": duration or None,
    }
