from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.message import Message


class MessageRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, message: Message) -> Message:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def list_by_conversation(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )

        return list(self.db.scalars(statement).all())

    def get_by_id(
        self,
        message_id: UUID,
    ) -> Message | None:
        statement = select(Message).where(
            Message.id == message_id
        )

        return self.db.scalar(statement)

    def delete(
        self,
        message_id: UUID,
    ) -> bool:
        message = self.get_by_id(message_id)

        if message is None:
            return False

        self.db.delete(message)
        self.db.commit()

        return True