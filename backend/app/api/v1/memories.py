from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.memory import MemoryCreate, MemoryResponse
from app.services.dependencies import get_memory_service
from app.services.memory_service import MemoryService


router = APIRouter(
    prefix="/memories",
    tags=["Memories"],
)


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


MemoryServiceDep = Annotated[
    MemoryService,
    Depends(get_memory_service),
]


@router.post(
    "",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_memory(
    data: MemoryCreate,
    current_user: CurrentUser,
    service: MemoryServiceDep,
):
    return service.create(
        user_id=current_user.id,
        memory_type=data.memory_type,
        key=data.key,
        value=data.value,
    )


@router.get(
    "",
    response_model=list[MemoryResponse],
)
def list_memories(
    current_user: CurrentUser,
    service: MemoryServiceDep,
):
    return service.list(current_user.id)


@router.get(
    "/{memory_id}",
    response_model=MemoryResponse,
)
def get_memory(
    memory_id: UUID,
    current_user: CurrentUser,
    service: MemoryServiceDep,
):
    try:
        return service.get(
            memory_id,
            current_user.id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{memory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_memory(
    memory_id: UUID,
    current_user: CurrentUser,
    service: MemoryServiceDep,
):
    try:
        service.delete(
            memory_id,
            current_user.id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )