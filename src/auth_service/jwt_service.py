from datetime import datetime, timedelta, timezone

from jose import ExpiredSignatureError, JWTError, jwt

from src.configure.settings import get_settings


settings = get_settings()


class TokenExpiredError(Exception):
    """Raised when the token has expired."""


class TokenInvalidError(Exception):
    """Raised when the token is invalid or malformed."""


class JWTService:

    @staticmethod
    def _build_payload(
        data: dict,
        expire: datetime,
        token_type: str,
    ) -> dict:
        return {
            **data,
            "type": token_type,
            "iat": datetime.now(timezone.utc),
            "exp": expire,
        }

    # =========================================================
    # ACCESS TOKEN
    # =========================================================

    @staticmethod
    def create_access_token(data: dict) -> str:

        expire = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        )

        payload = JWTService._build_payload(
            data=data,
            expire=expire,
            token_type="access",
        )

        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    # =========================================================
    # REFRESH TOKEN
    # =========================================================

    @staticmethod
    def create_refresh_token(data: dict) -> str:

        expire = (
            datetime.now(timezone.utc)
            + timedelta(
                days=settings.refresh_token_expire_days
            )
        )

        payload = JWTService._build_payload(
            data=data,
            expire=expire,
            token_type="refresh",
        )

        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    # =========================================================
    # DECODE TOKEN
    # =========================================================

    @staticmethod
    def decode_token(token: str) -> dict:

        try:
            return jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )

        except ExpiredSignatureError as exc:
            raise TokenExpiredError(
                "Token has expired"
            ) from exc

        except JWTError as exc:
            raise TokenInvalidError(
                f"Invalid token: {exc}"
            ) from exc