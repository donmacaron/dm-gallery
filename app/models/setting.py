from sqlalchemy import Column, String, Text
from app.database import Base


class Setting(Base):
    __tablename__ = "settings"
    key         = Column(String, primary_key=True)
    value       = Column(Text, nullable=True)
    description = Column(String, nullable=True)


DEFAULT_SETTINGS = {
    # Site
    "site_title":             ("Don Macaron Gallery", "Site title in browser tab and footer"),
    "site_tagline":           ("Photography",         "Short tagline / meta description"),
    # Header
    "header_logo_text":       ("",        "Custom logo text (empty = use Site Title)"),
    "header_show_tagline":    ("0",       "Show tagline under logo: 1 = yes, 0 = no"),
    "header_bg_color":        ("",        "Header background color"),
    "header_border_color":    ("",        "Header bottom border color"),
    "header_text_color":      ("",        "Header logo + nav text color"),
    # Gallery display
    "album_names_always":     ("0",       "Always show album names: 1 = yes, 0 = hover only"),
    # Social
    "social_telegram_url":    ("",        "Telegram URL (empty = hidden)"),
    "social_instagram_url":   ("",        "Instagram URL (empty = hidden)"),
    # Theme
    "theme_bg_color":         ("#0a0a0a", "Background color"),
    "theme_fg_color":         ("#33ff33", "Text / phosphor color"),
    "theme_accent_color":     ("#ff6600", "Accent color"),
    "theme_scanline_opacity": ("0.05",    "CRT scanline opacity (0.0 - 0.3)"),
    "theme_font":             ("VT323",   "Primary font (Google Fonts name)"),
    # Homepage
    "homepage_mode":          ("all_albums",  "Homepage display mode"),
    "homepage_album_id":      ("",            "Featured album ID (for random_photo / specific_photo modes)"),
    "homepage_selected_albums": ("",          "Comma-separated album IDs for selected_albums mode"),
    "homepage_page_id":       ("",            "Page ID to display on homepage (page mode)"),
    "homepage_photo_id":      ("",            "Specific photo media ID (specific_photo mode)"),
    "homepage_rotation":      ("reload",      "Photo rotation: reload / daily / weekly / monthly"),
    # Footer
    "footer_bg_color":     ("",        "Footer background color (empty = match header)"),
    "footer_fg_color":     ("",        "Footer text color (empty = match header)"),
    "footer_border_color": ("",        "Footer top border color (empty = match header)"),
}
