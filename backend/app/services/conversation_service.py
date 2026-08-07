from uuid import UUID

from app.models.conversation import Conversation
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.conversation import ConversationCreate


class ConversationService:

    def __init__(self, repository: ConversationRepository):
        self.repository = repository

    def create(
        self,
        data: ConversationCreate,
        user_id: UUID,
    ):
        conversation = Conversation(
            title=data.title,
            user_id=user_id,
        )

        return self.repository.create(conversation)

    def get_all(self, user_id: UUID):
        return self.repository.get_all(user_id)

    def get_one(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ):
        conversation = self.repository.get_by_user(
            conversation_id,
            user_id,
        )

        if conversation is None:
            raise ValueError("Conversation not found.")

        return conversation

    def delete(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ):
        conversation = self.repository.get_by_user(
            conversation_id,
            user_id,
        )

        if conversation is None:
            raise ValueError("Conversation not found.")

        self.repository.delete(conversation)