from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import SessionLocal, get_db
from app.main import app
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.services.dependencies import get_message_service


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
        full_name="Message API Test User",
        email=f"message-api-{uuid4()}@example.com",
        hashed_password="test-hash",
        is_active=True,
        is_verified=True,
    )

    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    yield test_user

    db.query(Message).filter(
        Message.conversation_id.in_(
            db.query(Conversation.id).filter(Conversation.user_id == test_user.id)
        )
    ).delete(synchronize_session=False)

    db.query(Conversation).filter(Conversation.user_id == test_user.id).delete()

    db.delete(test_user)
    db.commit()


@pytest.fixture
def other_user(db: Session) -> User:
    test_user = User(
        full_name="Other Message API User",
        email=f"message-api-other-{uuid4()}@example.com",
        hashed_password="test-hash",
        is_active=True,
        is_verified=True,
    )

    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    yield test_user

    db.query(Message).filter(
        Message.conversation_id.in_(
            db.query(Conversation.id).filter(Conversation.user_id == test_user.id)
        )
    ).delete(synchronize_session=False)

    db.query(Conversation).filter(Conversation.user_id == test_user.id).delete()

    db.delete(test_user)
    db.commit()


@pytest.fixture
def conversation(
    db: Session,
    user: User,
) -> Conversation:
    conversation = Conversation(
        user_id=user.id,
        title="Test Conversation",
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


class FakeMessageService:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        conversation_id,
        current_user,
        content,
    ):
        conversation = self.db.get(
            Conversation,
            conversation_id,
        )

        if conversation is None:
            raise ValueError("Conversation not found")

        if conversation.user_id != current_user.id:
            raise ValueError("Conversation not found")

        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=content,
        )

        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content="Fake assistant response",
        )

        self.db.add(user_message)
        self.db.add(assistant_message)
        self.db.commit()

        self.db.refresh(user_message)
        self.db.refresh(assistant_message)

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
        }

    def list(
        self,
        conversation_id,
        current_user,
    ):
        conversation = self.db.get(
            Conversation,
            conversation_id,
        )

        if conversation is None:
            raise ValueError("Conversation not found")

        if conversation.user_id != current_user.id:
            raise ValueError("Conversation not found")

        return list(
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    def delete(
        self,
        message_id,
        current_user,
    ):
        message = self.db.get(
            Message,
            message_id,
        )

        if message is None:
            raise ValueError("Message not found")

        conversation = self.db.get(
            Conversation,
            message.conversation_id,
        )

        if conversation is None:
            raise ValueError("Conversation not found")

        if conversation.user_id != current_user.id:
            raise ValueError("Message not found")

        self.db.delete(message)
        self.db.commit()


@pytest.fixture
def client(
    db: Session,
    user: User,
):
    def override_get_db():
        yield db

    def override_get_current_user():
        return user

    def override_get_message_service():
        return FakeMessageService(db)

    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[get_current_user] = override_get_current_user

    app.dependency_overrides[get_message_service] = override_get_message_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_message(
    client: TestClient,
    conversation: Conversation,
):
    response = client.post(
        f"/api/v1/messages/{conversation.id}",
        json={
            "content": "Hello AI",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "user_message" in data
    assert "assistant_message" in data

    assert data["user_message"]["role"] == "user"
    assert data["user_message"]["content"] == "Hello AI"

    assert data["assistant_message"]["role"] == "assistant"
    assert data["assistant_message"]["content"] == "Fake assistant response"


def test_list_messages(
    client: TestClient,
    db: Session,
    conversation: Conversation,
):
    first = Message(
        conversation_id=conversation.id,
        role="user",
        content="Hello",
    )

    second = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="Hi there",
    )

    db.add(first)
    db.add(second)
    db.commit()

    response = client.get(f"/api/v1/messages/{conversation.id}")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["role"] == "user"
    assert data[0]["content"] == "Hello"
    assert data[1]["role"] == "assistant"
    assert data[1]["content"] == "Hi there"


def test_create_message_for_nonexistent_conversation(
    client: TestClient,
):
    conversation_id = uuid4()

    response = client.post(
        f"/api/v1/messages/{conversation_id}",
        json={
            "content": "Hello",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found"


def test_user_cannot_access_another_users_conversation(
    client: TestClient,
    db: Session,
    other_user: User,
):
    conversation = Conversation(
        user_id=other_user.id,
        title="Private Conversation",
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    response = client.get(f"/api/v1/messages/{conversation.id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found"


def test_user_cannot_send_message_to_another_users_conversation(
    client: TestClient,
    db: Session,
    other_user: User,
):
    conversation = Conversation(
        user_id=other_user.id,
        title="Private Conversation",
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    response = client.post(
        f"/api/v1/messages/{conversation.id}",
        json={
            "content": "Unauthorized message",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found"


def test_delete_message(
    client: TestClient,
    db: Session,
    conversation: Conversation,
):
    message = Message(
        conversation_id=conversation.id,
        role="user",
        content="Delete me",
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    message_id = message.id

    response = client.delete(f"/api/v1/messages/{message_id}")

    assert response.status_code == 204

    deleted = db.get(
        Message,
        message_id,
    )

    assert deleted is None


def test_delete_nonexistent_message(
    client: TestClient,
):
    message_id = uuid4()

    response = client.delete(f"/api/v1/messages/{message_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Message not found"


def test_message_validation(
    client: TestClient,
    conversation: Conversation,
):
    response = client.post(
        f"/api/v1/messages/{conversation.id}",
        json={},
    )

    assert response.status_code == 422
