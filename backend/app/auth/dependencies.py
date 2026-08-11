from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.deps import DBSession
from app.auth.jwt import verify_token
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)

TokenDep = Annotated[
    str,
    Depends(oauth2_scheme),
]


def get_current_payload(
    token: TokenDep,
) -> dict:
    """
    Validate the JWT and return its payload.

    This dependency is useful when an endpoint only needs
    the decoded token payload.
    """
    try:
        return verify_token(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def get_current_user(
    token: TokenDep,
    db: DBSession,
):
    """
    Authenticate the current user using an ACCESS token.

    Refresh tokens must never be accepted here.
    """
    try:
        payload = verify_token(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    # -------------------------------------------------
    # ACCESS TOKEN CHECK
    # -------------------------------------------------

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    # -------------------------------------------------
    # USER ID CHECK
    # -------------------------------------------------

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    # -------------------------------------------------
    # GET USER
    # -------------------------------------------------

    user = UserRepository(db).get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # -------------------------------------------------
    # ACTIVE USER CHECK
    # -------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )

    return user
