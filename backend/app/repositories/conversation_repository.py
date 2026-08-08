from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation


class ConversationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, conversation: Conversation) -> Conversation:
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def list_by_user(self, user_id: UUID) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_by_id(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Conversation | None:

        statement = (
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        return self.db.scalars(statement).first()

    def delete(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> bool:

        conversation = self.get_by_id(
            conversation_id,
            user_id,
        )

        if conversation is None:
            return False

        self.db.delete(conversation)
        self.db.commit()

        return True

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation


class ConversationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, conversation: Conversation) -> Conversation:
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def get_by_id(
        self,
        conversation_id: UUID,
    ) -> Conversation | None:
        return self.db.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id
            )
        )

    def get_by_id_for_user(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Conversation | None:
        return self.db.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

    def list_by_user(
        self,
        user_id: UUID,
    ) -> list[Conversation]:
        return list(
            self.db.scalars(
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(Conversation.updated_at.desc())
            ).all()
        )

    def delete(
        self,
        conversation: Conversation,
    ) -> None:
        self.db.delete(conversation)
        self.db.commit()