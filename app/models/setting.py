from sqlalchemy import Column, String, Text
from app.database import Base


class Setting(Base):
    __tablename__ = "settings"
    key         = Column(String, primary_key=True)
    value       = Column(Text, nullable=True)
    description = Column(String, nullable=True)


DEFAULT_SETTINGS = {
    # ─ Site
    "site_title":             ("Don Macaron Gallery", "Site title in browser tab and footer"),
    "site_tagline":           ("Photography",         "Short tagline / meta description"),
    # ─ Header
    "header_logo_text":       ("",        "Custom logo text (empty = use Site Title)"),
    "header_show_tagline":    ("0",       "Show tagline under logo: 1 = yes, 0 = no"),
    "header_bg_color":        ("",        "Header background color (empty = uses --bg)"),
    "header_border_color":    ("",        "Header bottom border color"),
    "header_text_color":      ("",        "Header logo + nav text color"),
    # ─ Gallery display
    "album_names_always":     ("0",       "Always show album names on covers: 1 = yes, 0 = hover only"),
    # ─ Social
    "social_telegram_url":    ("",        "Telegram URL (empty = hidden)"),
    "social_instagram_url":   ("",        "Instagram URL (empty = hidden)"),
    # ─ Theme
    "theme_bg_color":         ("#0a0a0a", "Background color"),
    "theme_fg_color":         ("#33ff33", "Text / phosphor color"),
    "theme_accent_color":     ("#ff6600", "Accent color"),
    "theme_scanline_opacity": ("0.05",    "CRT scanline opacity (0.0 \u2013 0.3)"),
    "theme_font":             ("VT323",   "Primary font (Google Fonts name)"),
    # ─ Homepage
    "homepage_album_id":      ("",        "Featured album ID (empty = list all public albums)"),
}
