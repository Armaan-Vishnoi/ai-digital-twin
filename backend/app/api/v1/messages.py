from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse
from app.services.dependencies import get_message_service
from app.services.message_service import MessageService

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


MessageServiceDep = Annotated[
    MessageService,
    Depends(get_message_service),
]


@router.post(
    "/{conversation_id}",
    response_model=dict[str, MessageResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    conversation_id: UUID,
    data: MessageCreate,
    current_user: CurrentUser,
    service: MessageServiceDep,
):
    try:
        return service.create(
            conversation_id=conversation_id,
            current_user=current_user,
            content=data.content,
            model=data.model,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{conversation_id}",
    response_model=list[MessageResponse],
)
def list_messages(
    conversation_id: UUID,
    current_user: CurrentUser,
    service: MessageServiceDep,
):
    try:
        return service.list(
            conversation_id=conversation_id,
            current_user=current_user,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_message(
    message_id: UUID,
    current_user: CurrentUser,
    service: MessageServiceDep,
):
    try:
        service.delete(
            message_id=message_id,
            current_user=current_user,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
