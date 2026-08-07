from fastapi import Depends

from app.api.deps import DBSession
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


def get_auth_service(
    db: DBSession,
) -> AuthService:
    repository = UserRepository(db)
    return AuthService(repository)

from fastapi import Depends

from app.api.deps import DBSession
from app.repositories.conversation_repository import ConversationRepository
from app.services.conversation_service import ConversationService


def get_conversation_service(
    db: DBSession,
):
    repository = ConversationRepository(db)

    return ConversationService(repository)