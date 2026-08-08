from uuid import UUID

from app.models.memory import Memory
from app.repositories.memory_repository import MemoryRepository


class MemoryService:

    def __init__(
        self,
        repository: MemoryRepository,
    ):
        self.repository = repository

    def get_for_context(
        self,
        user_id: UUID,
    ) -> list[Memory]:

        return self.repository.list_by_user(user_id)

    def create(
        self,
        user_id: UUID,
        memory_type: str,
        key: str,
        value: str,
    ) -> Memory:

        existing = self.repository.get_by_key(
            user_id,
            key,
        )

        # Update existing memory instead of creating duplicates.
        if existing is not None:
            existing.memory_type = memory_type
            existing.value = value

            return self.repository.update(existing)

        memory = Memory(
            user_id=user_id,
            memory_type=memory_type,
            key=key,
            value=value,
        )

        return self.repository.create(memory)

    def save_extracted_memory(
        self,
        user_id: UUID,
        memory: dict | None,
    ) -> Memory | None:

        if memory is None:
            return None

        return self.create(
            user_id=user_id,
            memory_type=memory["memory_type"],
            key=memory["key"],
            value=memory["value"],
        )

    def list(
        self,
        user_id: UUID,
    ) -> list[Memory]:

        return self.repository.list_by_user(user_id)

    def get(
        self,
        memory_id: UUID,
        user_id: UUID,
    ) -> Memory:

        memory = self.repository.get_by_id(
            memory_id,
            user_id,
        )

        if memory is None:
            raise ValueError("Memory not found")

        return memory

    def delete(
        self,
        memory_id: UUID,
        user_id: UUID,
    ) -> None:

        memory = self.repository.get_by_id(
            memory_id,
            user_id,
        )

        if memory is None:
            raise ValueError("Memory not found")

        self.repository.delete(memory)