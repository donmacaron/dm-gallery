from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Request

from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_admin_credentials() -> tuple[str, str]:
    """
    Return (username, hashed_password).
    Checks DB first (admin_username / admin_password_hash keys in Settings),
    falls back to .env values.
    """
    try:
        from app.database import SessionLocal
        from app.models.setting import Setting
        db = SessionLocal()
        try:
            username_row = db.query(Setting).filter(Setting.key == "admin_username").first()
            password_row = db.query(Setting).filter(Setting.key == "admin_password_hash").first()
            username = username_row.value if username_row and username_row.value else settings.admin_username
            pwd_hash = password_row.value if password_row and password_row.value else None
            return username, pwd_hash
        finally:
            db.close()
    except Exception:
        return settings.admin_username, None


def authenticate_admin(username: str, password: str) -> bool:
    stored_username, pwd_hash = _get_admin_credentials()

    if username != stored_username:
        return False

    if pwd_hash:
        # DB hash takes priority
        return pwd_context.verify(password, pwd_hash)
    else:
        # Fall back to plain-text .env password
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
