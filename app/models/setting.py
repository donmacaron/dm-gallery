from sqlalchemy import Column, String, Text
from app.database import Base


class Setting(Base):
    """Key-value store for all site settings."""
    __tablename__ = "settings"

    key         = Column(String, primary_key=True)
    value       = Column(Text, nullable=True)
    description = Column(String, nullable=True)


DEFAULT_SETTINGS = {
    # ── Site ──
    "site_title":             ("Don Macaron Gallery", "Site title in browser tab and footer"),
    "site_tagline":           ("Photography",         "Short tagline (meta description)"),

    # ── Header ──
    "header_logo_text":       ("",                    "Custom logo text shown in header (empty = use site_title)"),
    "header_show_tagline":    ("0",                   "Show tagline under logo in header: 1 = yes, 0 = no"),

    # ── Social ──
    "social_telegram_url":    ("",                    "Telegram URL (empty = hidden)"),
    "social_instagram_url":   ("",                    "Instagram URL (empty = hidden)"),

    # ── Theme ──
    "theme_bg_color":         ("#0a0a0a",             "Background color"),
    "theme_fg_color":         ("#33ff33",             "Text / phosphor color"),
    "theme_accent_color":     ("#ff6600",             "Accent color (links, highlights)"),
    "theme_scanline_opacity": ("0.05",                "CRT scanline opacity (0.0 – 0.3)"),
    "theme_font":             ("VT323",               "Primary font (Google Fonts name)"),

    # ── Homepage ──
    "homepage_album_id":      ("",                    "Featured album ID on homepage (empty = show all albums)"),
}
