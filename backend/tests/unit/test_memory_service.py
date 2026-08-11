from uuid import uuid4

from app.services.memory_service import MemoryService


class FakeMemoryRepository:
    def __init__(self):
        self.memories = []

    def get_by_key(self, user_id, key):
        for memory in self.memories:
            if memory.user_id == user_id and memory.key == key:
                return memory

        return None

    def create(self, memory):
        self.memories.append(memory)
        return memory

    def update(self, memory):
        return memory

    def list_by_user(self, user_id):
        return [memory for memory in self.memories if memory.user_id == user_id]

    def get_by_id(self, memory_id, user_id):
        for memory in self.memories:
            if memory.id == memory_id and memory.user_id == user_id:
                return memory

        return None

    def delete(self, memory):
        self.memories.remove(memory)


def test_create_memory():
    repository = FakeMemoryRepository()
    service = MemoryService(repository)

    user_id = uuid4()

    memory = service.create(
        user_id=user_id,
        memory_type="preference",
        key="favorite_language",
        value="Python",
    )

    assert memory.user_id == user_id
    assert memory.memory_type == "preference"
    assert memory.key == "favorite_language"
    assert memory.value == "Python"


def test_create_updates_existing_memory():
    repository = FakeMemoryRepository()
    service = MemoryService(repository)

    user_id = uuid4()

    first = service.create(
        user_id=user_id,
        memory_type="preference",
        key="favorite_language",
        value="Python",
    )

    second = service.create(
        user_id=user_id,
        memory_type="preference",
        key="favorite_language",
        value="Rust",
    )

    assert first.id == second.id
    assert second.value == "Rust"
    assert len(repository.memories) == 1


def test_memories_are_isolated_by_user():
    repository = FakeMemoryRepository()
    service = MemoryService(repository)

    user_1 = uuid4()
    user_2 = uuid4()

    service.create(
        user_id=user_1,
        memory_type="preference",
        key="favorite_language",
        value="Python",
    )

    service.create(
        user_id=user_2,
        memory_type="preference",
        key="favorite_language",
        value="Rust",
    )

    memories_1 = service.list(user_1)
    memories_2 = service.list(user_2)

    assert len(memories_1) == 1
    assert len(memories_2) == 1

    assert memories_1[0].value == "Python"
    assert memories_2[0].value == "Rust"


def test_get_nonexistent_memory():
    repository = FakeMemoryRepository()
    service = MemoryService(repository)

    user_id = uuid4()
    memory_id = uuid4()

    try:
        service.get(
            memory_id,
            user_id,
        )
        assert False
    except ValueError as exc:
        assert str(exc) == "Memory not found"
