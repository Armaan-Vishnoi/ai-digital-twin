from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.memory import Memory
from app.models.user import User
from app.repositories.memory_repository import MemoryRepository


@pytest.fixture
def db() -> Session:
    """
    Create a database session for an integration test.

    The test uses the application's configured PostgreSQL database.
    Data created by each test is cleaned up afterwards.
    """

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def user(db: Session) -> User:
    """
    Create a unique test user.

    The user is required because Memory.user_id
    has a foreign key to users.id.
    """

    test_user = User(
        full_name="Memory Test User",
        email=f"memory-test-{uuid4()}@example.com",
        hashed_password="test-hash",
        is_active=True,
        is_verified=True,
    )

    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    yield test_user

    # Clean up memories first.
    db.query(Memory).filter(Memory.user_id == test_user.id).delete()

    db.delete(test_user)
    db.commit()


def test_create_memory(
    db: Session,
    user: User,
):
    repository = MemoryRepository(db)

    memory = Memory(
        user_id=user.id,
        memory_type="preference",
        key="favorite_language",
        value="Python",
    )

    result = repository.create(memory)

    assert result.id is not None
    assert result.user_id == user.id
    assert result.memory_type == "preference"
    assert result.key == "favorite_language"
    assert result.value == "Python"


def test_get_by_key(
    db: Session,
    user: User,
):
    repository = MemoryRepository(db)

    memory = Memory(
        user_id=user.id,
        memory_type="preference",
        key="favorite_language",
        value="Python",
    )

    repository.create(memory)

    result = repository.get_by_key(
        user.id,
        "favorite_language",
    )

    assert result is not None
    assert result.id == memory.id
    assert result.value == "Python"


def test_get_by_key_returns_none_for_wrong_user(
    db: Session,
    user: User,
):
    repository = MemoryRepository(db)

    memory = Memory(
        user_id=user.id,
        memory_type="preference",
        key="favorite_language",
        value="Python",
    )

    repository.create(memory)

    wrong_user_id = uuid4()

    result = repository.get_by_key(
        wrong_user_id,
        "favorite_language",
    )

    assert result is None


def test_get_by_id(
    db: Session,
    user: User,
):
    repository = MemoryRepository(db)

    memory = Memory(
        user_id=user.id,
        memory_type="preference",
        key="favorite_language",
        value="Python",
    )

    repository.create(memory)

    result = repository.get_by_id(
        memory.id,
        user.id,
    )

    assert result is not None
    assert result.id == memory.id
    assert result.user_id == user.id
    assert result.value == "Python"


def test_get_by_id_returns_none_for_wrong_user(
    db: Session,
    user: User,
):
    repository = MemoryRepository(db)

    memory = Memory(
        user_id=user.id,
        memory_type="preference",
        key="favorite_language",
        value="Python",
    )

    repository.create(memory)

    wrong_user_id = uuid4()

    result = repository.get_by_id(
        memory.id,
        wrong_user_id,
    )

    assert result is None


def test_list_by_user(
    db: Session,
    user: User,
):
    repository = MemoryRepository(db)

    first = Memory(
        user_id=user.id,
        memory_type="preference",
        key="favorite_language",
        value="Python",
    )

    second = Memory(
        user_id=user.id,
        memory_type="education",
        key="degree",
        value="BCA",
    )

    repository.create(first)
    repository.create(second)

    memories = repository.list_by_user(user.id)

    assert len(memories) == 2

    assert memories[0].key == "favorite_language"
    assert memories[0].value == "Python"

    assert memories[1].key == "degree"
    assert memories[1].value == "BCA"


def test_update_memory(
    db: Session,
    user: User,
):
    repository = MemoryRepository(db)

    memory = Memory(
        user_id=user.id,
        memory_type="preference",
        key="favorite_language",
        value="Python",
    )

    repository.create(memory)

    memory.value = "Rust"
    memory.memory_type = "preference"

    result = repository.update(memory)

    assert result.id == memory.id
    assert result.value == "Rust"

    # Verify the change actually reached PostgreSQL.
    db.expire_all()

    saved = repository.get_by_id(
        memory.id,
        user.id,
    )

    assert saved is not None
    assert saved.value == "Rust"


def test_delete_memory(
    db: Session,
    user: User,
):
    repository = MemoryRepository(db)

    memory = Memory(
        user_id=user.id,
        memory_type="preference",
        key="favorite_language",
        value="Python",
    )

    repository.create(memory)

    memory_id = memory.id

    repository.delete(memory)

    result = repository.get_by_id(
        memory_id,
        user.id,
    )

    assert result is None
