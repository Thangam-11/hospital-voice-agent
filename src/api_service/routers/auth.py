"""
src/routers/auth_router.py

Authentication routes for Hospital Admin users.

Endpoints:
    POST /auth/register
    POST /auth/login
    POST /auth/refresh
    POST /auth/logout
    GET  /auth/me
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_service.auth_main import AuthService
from src.auth_service.dependencies import get_current_admin
from src.database.base_engine import get_db
from src.database.models import User
from src.api_service.schemas.auth_schema import (
    AuthRegisterRequest,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminResponse,
    RefreshTokenRequest,
    LogoutRequest,
)


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

auth_service = AuthService()


# =========================================================
# REGISTER
# =========================================================

@router.post(
    "/register",
    response_model=AdminResponse,
    status_code=201,
)
async def register_admin(
    request: AuthRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new Admin user.

    This endpoint should normally be restricted in production
    or used only for initial admin/bootstrap setup.
    """

    user = await auth_service.register(
        email=request.email,
        username=request.username,
        full_name=request.full_name,
        password=request.password,
        db=db,
    )

    return AdminResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=AdminLoginResponse,
)
async def login_admin(
    request: AdminLoginRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate an Admin user and return access + refresh tokens.
    """

    return await auth_service.login(
        email=request.email,
        password=request.password,
        db=db,
        user_agent=http_request.headers.get(
            "user-agent"
        ),
        ip_address=(
            http_request.client.host
            if http_request.client
            else None
        ),
    )


# =========================================================
# REFRESH
# =========================================================

@router.post(
    "/refresh",
    response_model=AdminLoginResponse,
)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a new access token using a refresh token.
    """

    return await auth_service.refresh(
        raw_token=request.refresh_token,
        db=db,
    )


# =========================================================
# LOGOUT
# =========================================================

@router.post(
    "/logout",
    status_code=204,
)
async def logout_admin(
    request: LogoutRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke the Admin refresh token.
    """

    await auth_service.logout(
        raw_token=request.refresh_token,
        db=db,
    )

    return None


# =========================================================
# CURRENT ADMIN
# =========================================================

@router.get(
    "/me",
    response_model=AdminResponse,
)
async def get_me(
    current_admin: User = Depends(
        get_current_admin
    ),
):
    """
    Return the currently authenticated Admin.
    """

    return AdminResponse(
        id=str(current_admin.id),
        email=current_admin.email,
        username=current_admin.username,
        full_name=current_admin.full_name,
        role=current_admin.role,
        is_active=current_admin.is_active,
    )