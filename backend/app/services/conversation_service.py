from uuid import UUID

from app.models.conversation import Conversation
from app.repositories.conversation_repository import ConversationRepository


class ConversationService:

    def __init__(self, repository: ConversationRepository):
        self.repository = repository

    def create(
        self,
        user_id: UUID,
        title: str,
    ) -> Conversation:

        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        return self.repository.create(conversation)

    def get_all(
        self,
        user_id: UUID,
    ) -> list[Conversation]:

        return self.repository.list_by_user(user_id)

    def get_one(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Conversation:

        conversation = self.repository.get_by_id(
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
    ) -> None:

        deleted = self.repository.delete(
            conversation_id,
            user_id,
        )

        if not deleted:
            raise ValueError("Conversation not found.")