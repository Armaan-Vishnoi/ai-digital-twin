from fastapi import APIRouter, HTTPException, status

from app.api.deps import DBSession
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserRegister, UserResponse
from app.services.auth_service import AuthService
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from app.services.dependencies import get_auth_service
from app.services.auth_service import AuthService

from app.schemas.auth import UserLogin, TokenResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service),
]

@router.get("/health")
def health():
    return {
        "message": "Authentication API is working"
    }


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: UserRegister,
    service: AuthServiceDep,
):
    try:
        return service.register(data)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

from typing import Annotated
from fastapi import Depends

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    service: AuthServiceDep,
):
    data = UserLogin(
        email=form_data.username,
        password=form_data.password,
    )

    try:
        return service.login(data)

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )