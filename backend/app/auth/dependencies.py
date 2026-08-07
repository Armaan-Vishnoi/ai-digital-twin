from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt import verify_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)

TokenDep = Annotated[
    str,
    Depends(oauth2_scheme),
]


def get_current_payload(
    token: TokenDep,
):
    try:
        return verify_token(token)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

from app.api.deps import DBSession
from app.repositories.user_repository import UserRepository


def get_current_user(
    token: TokenDep,
    db: DBSession,
):
    payload = verify_token(token)

    user = UserRepository(db).get_by_id(
        payload["sub"]
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user