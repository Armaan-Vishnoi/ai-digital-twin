from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    current_user: CurrentUser,
):
    return current_user