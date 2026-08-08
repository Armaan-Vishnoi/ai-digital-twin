from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
)
from app.services.conversation_service import ConversationService
from app.services.dependencies import get_conversation_service


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


ConversationServiceDep = Annotated[
    ConversationService,
    Depends(get_conversation_service),
]


@router.get(
    "",
    response_model=list[ConversationResponse],
)
def list_conversations(
    current_user: CurrentUser,
    service: ConversationServiceDep,
):
    return service.get_all(
        current_user.id,
    )


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    data: ConversationCreate,
    current_user: CurrentUser,
    service: ConversationServiceDep,
):
    return service.create(
        current_user.id,
        data.title,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation(
    conversation_id: UUID,
    current_user: CurrentUser,
    service: ConversationServiceDep,
):
    try:
        return service.get_one(
            conversation_id,
            current_user.id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation(
    conversation_id: UUID,
    current_user: CurrentUser,
    service: ConversationServiceDep,
):
    try:
        service.delete(
            conversation_id,
            current_user.id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )