from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.memory import Memory


class MemoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, memory: Memory) -> Memory:
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)

        return memory

    def list_by_user(
        self,
        user_id: UUID,
    ) -> list[Memory]:

        statement = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(Memory.created_at.asc())
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_by_key(
        self,
        user_id: UUID,
        key: str,
    ) -> Memory | None:

        statement = (
            select(Memory)
            .where(
                Memory.user_id == user_id,
                Memory.key == key,
            )
        )

        return self.db.scalar(statement)

    def get_by_id(
        self,
        memory_id: UUID,
        user_id: UUID,
    ) -> Memory | None:

        statement = (
            select(Memory)
            .where(
                Memory.id == memory_id,
                Memory.user_id == user_id,
            )
        )

        return self.db.scalar(statement)

    def update(
        self,
        memory: Memory,
    ) -> Memory:

        self.db.commit()
        self.db.refresh(memory)

        return memory

    def delete(
        self,
        memory: Memory,
    ) -> None:

        self.db.delete(memory)
        self.db.commit()