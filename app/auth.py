from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from fastapi import Request

from app.config import get_settings

settings = get_settings()


# ── Password helpers (bcrypt direct — no passlib) ──────────────────
def hash_password(password: str) -> str:
    """Hash a plain-text password, return the bcrypt hash string."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ── Credential lookup ────────────────────────────────────────
def _get_admin_credentials() -> tuple[str, Optional[str]]:
    """
    Return (username, bcrypt_hash_or_None).
    Checks DB Settings first, falls back to .env values.
    """
    try:
        from app.database import SessionLocal
        from app.models.setting import Setting
        db = SessionLocal()
        try:
            u_row = db.query(Setting).filter(Setting.key == "admin_username").first()
            p_row = db.query(Setting).filter(Setting.key == "admin_password_hash").first()
            username = u_row.value if u_row and u_row.value else settings.admin_username
            pwd_hash = p_row.value if p_row and p_row.value else None
            return username, pwd_hash
        finally:
            db.close()
    except Exception:
        return settings.admin_username, None


# ── Auth ───────────────────────────────────────────────────
def authenticate_admin(username: str, password: str) -> bool:
    stored_username, pwd_hash = _get_admin_credentials()
    if username != stored_username:
        return False
    if pwd_hash:
        return verify_password(password, pwd_hash)
    # Fallback: plain-text .env password (no hash stored yet)
    return password == settings.admin_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def require_admin(request: Request) -> Optional[str]:
    token = request.cookies.get("admin_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        return username if username else None
    except JWTError:
        return None
