"""
Dominant color extraction from a thumbnail image.
Uses Pillow — no extra dependencies.

Algorithm:
  1. Resize to tiny (50x50) for speed
  2. Convert to RGB
  3. Collect all pixel colors, weight by saturation
  4. Average the top-N most saturated pixels
  5. Ensure luminance is readable (not too dark) by boosting if needed
  6. Return as #rrggbb hex string
"""
from __future__ import annotations
from pathlib import Path


def extract_dominant_color(image_path: str, media_dir: str) -> str | None:
    """
    Extract a readable dominant color from a thumbnail file.
    Returns hex string like '#a3c4f1', or None on failure.
    """
    try:
        from PIL import Image
        import colorsys

        full_path = Path(media_dir) / image_path
        if not full_path.exists():
            return None

        with Image.open(str(full_path)) as img:
            # Work on a tiny version for speed
            img = img.convert("RGB").resize((50, 50), Image.LANCZOS)
            pixels = list(img.getdata())  # list of (r, g, b)

        # Score each pixel by saturation (ignore near-grey and near-black)
        scored = []
        for r, g, b in pixels:
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            # Skip very dark pixels (v < 0.15) and near-white (v > 0.95, s < 0.1)
            if v < 0.15 or (v > 0.95 and s < 0.1):
                continue
            scored.append((s, r, g, b))

        if not scored:
            # Fallback: plain average of all pixels
            r = int(sum(p[0] for p in pixels) / len(pixels))
            g = int(sum(p[1] for p in pixels) / len(pixels))
            b = int(sum(p[2] for p in pixels) / len(pixels))
        else:
            # Take the top 30% most saturated pixels and average them
            scored.sort(reverse=True)  # highest saturation first
            top_n = max(1, len(scored) // 3)
            top   = scored[:top_n]
            r = int(sum(p[1] for p in top) / len(top))
            g = int(sum(p[2] for p in top) / len(top))
            b = int(sum(p[3] for p in top) / len(top))

        # Ensure the color is readable against the dark background:
        # If luminance < 35%, boost toward white proportionally
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if v < 0.35:
            # Boost value to at least 0.55 while keeping hue & saturation
            v = 0.55
            r_f, g_f, b_f = colorsys.hsv_to_rgb(h, s, v)
            r, g, b = int(r_f * 255), int(g_f * 255), int(b_f * 255)

        return f"#{r:02x}{g:02x}{b:02x}"

    except Exception:
        return None
