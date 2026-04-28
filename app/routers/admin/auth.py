from datetime import timedelta

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth import authenticate_admin, create_access_token
from app.config import get_settings

router = APIRouter(tags=["admin-auth"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    # Starlette 0.40+: request is the first positional arg, NOT in context dict
    return templates.TemplateResponse(request, "admin/login.html", {
        "error": error,
        "site_title": settings.site_title,
    })


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if not authenticate_admin(username, password):
        return templates.TemplateResponse(request, "admin/login.html", {
            "error": "Invalid credentials. Try again.",
            "site_title": settings.site_title,
        }, status_code=401)

    token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax",
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_token")
    return response
