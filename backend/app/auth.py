import hmac
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


ACCESS_TOKEN_EXPIRE_MINUTES = 720
TOKEN_ISSUER = "ifood-ai-copilot"
TOKEN_AUDIENCE = "ifood-ai-copilot"
bearer_scheme = HTTPBearer(auto_error=False)


class AuthConfigurationError(Exception):
    pass


@dataclass(frozen=True)
class AuthConfiguration:
    username: str
    password: str
    secret_key: str
    restaurant_id: str


@dataclass(frozen=True)
class DemoAccount:
    username: str
    restaurant_id: str


def get_auth_configuration() -> AuthConfiguration:
    username = os.getenv("PROTOTYPE_USERNAME", "").strip()
    password = os.getenv("PROTOTYPE_PASSWORD", "")
    secret_key = os.getenv("AUTH_SECRET_KEY", "")
    restaurant_id = os.getenv("AUTH_RESTAURANT_ID", "demo-restaurant").strip()

    if not username or not password or not restaurant_id:
        raise AuthConfigurationError(
            "Configure PROTOTYPE_USERNAME, PROTOTYPE_PASSWORD e AUTH_RESTAURANT_ID."
        )
    if len(username) > 100 or len(password) > 256 or len(restaurant_id) > 100:
        raise AuthConfigurationError(
            "As credenciais e o identificador do restaurante excedem o tamanho permitido."
        )
    if len(secret_key.encode("utf-8")) < 32:
        raise AuthConfigurationError("AUTH_SECRET_KEY deve ter ao menos 32 bytes.")

    return AuthConfiguration(
        username=username,
        password=password,
        secret_key=secret_key,
        restaurant_id=restaurant_id,
    )


def verify_credentials(username: str, password: str, config: AuthConfiguration) -> bool:
    username_matches = hmac.compare_digest(
        username.encode("utf-8"), config.username.encode("utf-8")
    )
    password_matches = hmac.compare_digest(
        password.encode("utf-8"), config.password.encode("utf-8")
    )
    return username_matches and password_matches


def create_access_token(config: AuthConfiguration) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": config.username,
            "restaurant_id": config.restaurant_id,
            "iat": now,
            "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iss": TOKEN_ISSUER,
            "aud": TOKEN_AUDIENCE,
        },
        config.secret_key,
        algorithm="HS256",
    )


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_account(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> DemoAccount:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    try:
        config = get_auth_configuration()
    except AuthConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        claims: dict[str, Any] = jwt.decode(
            credentials.credentials,
            config.secret_key,
            algorithms=["HS256"],
            audience=TOKEN_AUDIENCE,
            issuer=TOKEN_ISSUER,
            options={
                "require": ["aud", "exp", "iat", "iss", "restaurant_id", "sub"],
            },
        )
    except jwt.InvalidTokenError as exc:
        raise _unauthorized() from exc

    username = claims.get("sub")
    restaurant_id = claims.get("restaurant_id")
    if (
        not isinstance(username, str)
        or not isinstance(restaurant_id, str)
        or username != config.username
        or restaurant_id != config.restaurant_id
    ):
        raise _unauthorized()

    return DemoAccount(username=username, restaurant_id=restaurant_id)


def ensure_restaurant_access(restaurant_id: str, account: DemoAccount) -> None:
    if restaurant_id != account.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A conta não tem acesso a este restaurante.",
        )
