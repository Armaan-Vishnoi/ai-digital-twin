from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.memory_repository import MemoryRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.conversation_service import ConversationService
from app.services.memory_service import MemoryService
from app.services.message_service import MessageService


def get_auth_service(
    db: Annotated[Session, Depends(get_db)],
) -> AuthService:

    repository = UserRepository(db)

    return AuthService(repository)


def get_conversation_service(
    db: Annotated[Session, Depends(get_db)],
) -> ConversationService:

    repository = ConversationRepository(db)

    return ConversationService(repository)


def get_memory_service(
    db: Annotated[Session, Depends(get_db)],
) -> MemoryService:

    repository = MemoryRepository(db)

    return MemoryService(repository)


def get_message_service(
    db: Annotated[Session, Depends(get_db)],
) -> MessageService:

    message_repository = MessageRepository(db)

    conversation_repository = ConversationRepository(db)

    memory_repository = MemoryRepository(db)

    memory_service = MemoryService(
        repository=memory_repository,
    )

    return MessageService(
        repository=message_repository,
        conversation_repository=conversation_repository,
        memory_service=memory_service,
    )