from sqlalchemy import Column, String, Text
from app.database import Base


class Setting(Base):
    """Key-value store for site settings: theme, social links, etc."""
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(Text, nullable=True)
    description = Column(String, nullable=True)


# Default settings with their initial values
DEFAULT_SETTINGS = {
    "site_title":             ("Don Macaron Gallery", "Site title shown in header and browser tab"),
    "site_tagline":           ("Photography",         "Short tagline shown under title"),
    "social_telegram_url":    ("",                    "Telegram blog URL (leave empty to hide)"),
    "social_instagram_url":   ("",                    "Instagram URL (leave empty to hide)"),
    "theme_bg_color":         ("#0a0a0a",             "Background color hex"),
    "theme_fg_color":         ("#33ff33",             "Foreground/text color hex"),
    "theme_accent_color":     ("#ff6600",             "Accent color hex (links, highlights)"),
    "theme_scanline_opacity": ("0.05",                "CRT scanline overlay opacity (0.0 – 0.3)"),
    "theme_font":             ("VT323",               "Primary font name (Google Fonts)"),
    "homepage_album_id":      ("",                    "Album ID to feature on homepage (empty = show all public)"),
}
