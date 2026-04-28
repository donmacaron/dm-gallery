from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Request
from fastapi.responses import RedirectResponse

from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def authenticate_admin(username: str, password: str) -> bool:
    """Verify admin credentials against .env values."""
    return username == settings.admin_username and password == settings.admin_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Optional[str]:
    """Decode JWT and return username, or None if invalid."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("sub")
    except JWTError:
        return None


def require_admin(request: Request) -> Optional[str]:
    """
    Dependency helper: returns admin username from cookie, or None.
    Use in routes to gate admin access.
    """
    token = request.cookies.get("admin_token")
    if not token:
        return None
    return decode_token(token)
