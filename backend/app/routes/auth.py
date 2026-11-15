from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    AuthConfigurationError,
    DemoAccount,
    create_access_token,
    ensure_restaurant_access,
    get_auth_configuration,
    get_current_account,
    verify_credentials,
)
from app.schemas.auth import AccessToken, CurrentAccount, LoginRequest

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=AccessToken)
def login(payload: LoginRequest) -> AccessToken:
    try:
        config = get_auth_configuration()
    except AuthConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if not verify_credentials(payload.username, payload.password, config):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AccessToken(
        access_token=create_access_token(config),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=CurrentAccount)
def current_account(
    account: DemoAccount = Depends(get_current_account),
) -> CurrentAccount:
    return CurrentAccount(
        username=account.username,
        restaurant_id=account.restaurant_id,
    )
