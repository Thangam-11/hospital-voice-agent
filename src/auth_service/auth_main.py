"""
src/auth/auth_service.py
========================

Handles Admin authentication.

Only Admin users can log in to the system.
Patients do not have application accounts.
"""

import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_service.jwt_service import JWTService
from src.auth_service.security import hash_password, verify_password
from src.configure.settings import get_settings
from src.database.models import User, RefreshToken


settings = get_settings()


def _hash_token(raw_token: str) -> str:
    """
    Hash refresh token before storing it in the database.

    Raw refresh tokens are never stored in PostgreSQL.
    """
    return hashlib.sha256(raw_token.encode()).hexdigest()


class AuthService:
        # =========================================================
    # REGISTER
    # =========================================================

    async def register(
        self,
        email: str,
        username: str,
        full_name: str,
        password: str,
        db: AsyncSession,
    ) -> User:

        # 1. Check whether email already exists
        result = await db.execute(
            select(User).where(User.email == email)
        )

        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # 2. Hash password using existing bcrypt implementation
        hashed_password = hash_password(password)

        # 3. Create admin user
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            role="ADMIN",
            is_active=True,
        )

        # 4. Save to PostgreSQL
        db.add(user)

        await db.commit()
        await db.refresh(user)

        return user


    # =========================================================
    # LOGIN
    # =========================================================

    async def login(
        self,
        email: str,
        password: str,
        db: AsyncSession,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> dict:

        # -----------------------------------------------------
        # 1. Find user by email
        # -----------------------------------------------------

        result = await db.execute(
            select(User).where(User.email == email)
        )

        user = result.scalar_one_or_none()

        # -----------------------------------------------------
        # 2. User doesn't exist / password incorrect
        # -----------------------------------------------------

        if not user or not verify_password(
            password,
            user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # -----------------------------------------------------
        # 3. Check account status
        # -----------------------------------------------------

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is disabled",
            )

        # -----------------------------------------------------
        # 4. Check Admin role
        # -----------------------------------------------------

        if user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        # -----------------------------------------------------
        # 5. Create JWT payload
        # -----------------------------------------------------

        token_data = {
            "user_id": str(user.id),
            "role": user.role,
        }

        # -----------------------------------------------------
        # 6. Create access token
        # -----------------------------------------------------

        access_token = JWTService.create_access_token(
            token_data
        )

        # -----------------------------------------------------
        # 7. Create refresh token
        # -----------------------------------------------------

        refresh_token = JWTService.create_refresh_token(
            token_data
        )

        # -----------------------------------------------------
        # 8. Calculate refresh-token expiry
        # -----------------------------------------------------

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                days=settings.refresh_token_expire_days
            )
        )

        # -----------------------------------------------------
        # 9. Store ONLY hashed refresh token
        # -----------------------------------------------------

        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=_hash_token(refresh_token),
            expires_at=expires_at,
            is_revoked=False,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        db.add(refresh_token_record)

        # -----------------------------------------------------
        # 10. Update last login
        # -----------------------------------------------------

        user.last_login = datetime.now(timezone.utc)

        # -----------------------------------------------------
        # 11. Save changes
        # -----------------------------------------------------

        await db.commit()

        # -----------------------------------------------------
        # 12. Return response
        # -----------------------------------------------------

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": (
                settings.access_token_expire_minutes * 60
            ),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
            },
        }

    # =========================================================
    # REFRESH
    # =========================================================

    async def refresh(
        self,
        raw_token: str,
        db: AsyncSession,
    ) -> dict:

        # -----------------------------------------------------
        # 1. Decode refresh JWT
        # -----------------------------------------------------

        try:
            payload = JWTService.decode_token(raw_token)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # -----------------------------------------------------
        # 2. Make sure this is an Admin token
        # -----------------------------------------------------

        if payload.get("role") != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        # -----------------------------------------------------
        # 3. Hash received refresh token
        # -----------------------------------------------------

        token_hash = _hash_token(raw_token)

        # -----------------------------------------------------
        # 4. Find token in database
        # -----------------------------------------------------

        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked.is_(False),
            )
        )

        stored_token = result.scalar_one_or_none()

        # -----------------------------------------------------
        # 5. Check token exists
        # -----------------------------------------------------

        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is invalid or revoked",
            )

        # -----------------------------------------------------
        # 6. Check expiration
        # -----------------------------------------------------

        now = datetime.now(timezone.utc)

        expires_at = stored_token.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        if expires_at < now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )

        # -----------------------------------------------------
        # 7. Find Admin
        # -----------------------------------------------------

        result = await db.execute(
            select(User).where(
                User.id == stored_token.user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin account not found",
            )

        # -----------------------------------------------------
        # 8. Check Admin account
        # -----------------------------------------------------

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is disabled",
            )

        if user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        # -----------------------------------------------------
        # 9. Create new access token
        # -----------------------------------------------------

        token_data = {
            "user_id": str(user.id),
            "role": user.role,
        }

        access_token = JWTService.create_access_token(
            token_data
        )

        return {
            "access_token": access_token,
            "refresh_token": raw_token,
            "token_type": "bearer",
            "expires_in": (
                settings.access_token_expire_minutes * 60
            ),
        }

    # =========================================================
    # LOGOUT
    # =========================================================

    async def logout(
        self,
        raw_token: str,
        db: AsyncSession,
    ) -> None:

        # -----------------------------------------------------
        # 1. Hash refresh token
        # -----------------------------------------------------

        token_hash = _hash_token(raw_token)

        # -----------------------------------------------------
        # 2. Find stored token
        # -----------------------------------------------------

        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )

        stored_token = result.scalar_one_or_none()

        # -----------------------------------------------------
        # 3. Revoke token
        # -----------------------------------------------------

        if stored_token:
            stored_token.is_revoked = True

            await db.commit()

    # =========================================================
    # GET CURRENT ADMIN
    # =========================================================

    async def get_current_admin(
        self,
        user_id: str,
        db: AsyncSession,
    ) -> User:

        result = await db.execute(
            select(User).where(
                User.id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin account not found",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is disabled",
            )

        if user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        return user