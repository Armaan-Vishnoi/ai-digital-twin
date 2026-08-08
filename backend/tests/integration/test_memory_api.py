from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import SessionLocal, get_db
from app.main import app
from app.models.memory import Memory
from app.models.user import User


@pytest.fixture
def db() -> Session:
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def user(db: Session) -> User:
    test_user = User(
        full_name="Memory API Test User",
        email=f"memory-api-{uuid4()}@example.com",
        hashed_password="test-hash",
        is_active=True,
        is_verified=True,
    )

    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    yield test_user

    db.query(Memory).filter(
        Memory.user_id == test_user.id
    ).delete()

    db.delete(test_user)
    db.commit()


@pytest.fixture
def other_user(db: Session) -> User:
    test_user = User(
        full_name="Other Memory API User",
        email=f"memory-api-other-{uuid4()}@example.com",
        hashed_password="test-hash",
        is_active=True,
        is_verified=True,
    )

    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    yield test_user

    db.query(Memory).filter(
        Memory.user_id == test_user.id
    ).delete()

    db.delete(test_user)
    db.commit()


@pytest.fixture
def client(db: Session, user: User):
    def override_get_db():
        yield db

    def override_get_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_memory(client: TestClient):
    response = client.post(
        "/api/v1/memories",
        json={
            "memory_type": "preference",
            "key": "favorite_language",
            "value": "Python",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["memory_type"] == "preference"
    assert data["key"] == "favorite_language"
    assert data["value"] == "Python"
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_list_memories(
    client: TestClient,
    db: Session,
    user: User,
):
    memory = Memory(
        user_id=user.id,
        memory_type="education",
        key="degree",
        value="BCA",
    )

    db.add(memory)
    db.commit()

    response = client.get("/api/v1/memories")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["key"] == "degree"
    assert data[0]["value"] == "BCA"


def test_get_memory(
    client: TestClient,
    db: Session,
    user: User,
):
    memory = Memory(
        user_id=user.id,
        memory_type="preference",
        key="favorite_language",
        value="Python",
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    response = client.get(
        f"/api/v1/memories/{memory.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(memory.id)
    assert data["value"] == "Python"


def test_get_nonexistent_memory(
    client: TestClient,
):
    memory_id = uuid4()

    response = client.get(
        f"/api/v1/memories/{memory_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Memory not found"


def test_user_cannot_access_another_users_memory(
    client: TestClient,
    db: Session,
    other_user: User,
):
    memory = Memory(
        user_id=other_user.id,
        memory_type="preference",
        key="favorite_language",
        value="Rust",
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    response = client.get(
        f"/api/v1/memories/{memory.id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Memory not found"


def test_delete_memory(
    client: TestClient,
    db: Session,
    user: User,
):
    memory = Memory(
        user_id=user.id,
        memory_type="preference",
        key="favorite_language",
        value="Python",
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    memory_id = memory.id

    response = client.delete(
        f"/api/v1/memories/{memory_id}"
    )

    assert response.status_code == 204

    deleted = db.get(Memory, memory_id)

    assert deleted is None


def test_delete_nonexistent_memory(
    client: TestClient,
):
    memory_id = uuid4()

    response = client.delete(
        f"/api/v1/memories/{memory_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Memory not found"


def test_create_memory_validation(
    client: TestClient,
):
    response = client.post(
        "/api/v1/memories",
        json={
            "memory_type": "preference",
            "key": "favorite_language",
        },
    )

    assert response.status_code == 422