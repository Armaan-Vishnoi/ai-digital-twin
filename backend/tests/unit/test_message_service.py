from uuid import uuid4

import pytest

import app.models.user  # noqa: F401
from app.models.conversation import Conversation
from app.models.memory import Memory
from app.models.message import Message
from app.services.message_service import MessageService

# ============================================================
# Fake Message Repository
# ============================================================


class FakeMessageRepository:
    def __init__(self):
        self.messages = []

    def list_by_conversation(self, conversation_id):
        return [
            message
            for message in self.messages
            if message.conversation_id == conversation_id
        ]

    def create(self, message):
        if message.id is None:
            message.id = uuid4()

        self.messages.append(message)

        return message

    def get_by_id(self, message_id):
        for message in self.messages:
            if message.id == message_id:
                return message

        return None

    def delete(self, message_id):
        self.messages = [
            message for message in self.messages if message.id != message_id
        ]


# ============================================================
# Fake Conversation Repository
# ============================================================


class FakeConversationRepository:
    def __init__(self):
        self.conversations = []

    def add(self, conversation):
        self.conversations.append(conversation)

    def get_by_id(self, conversation_id, user_id):
        for conversation in self.conversations:
            if conversation.id == conversation_id and conversation.user_id == user_id:
                return conversation

        return None


# ============================================================
# Fake Memory Service
# ============================================================


class FakeMemoryService:
    def __init__(self):
        self.memories = []
        self.saved_memories = []

    def save_extracted_memory(
        self,
        user_id,
        memory,
    ):
        self.saved_memories.append(
            {
                "user_id": user_id,
                "memory": memory,
            }
        )

        return memory

    def list(self, user_id):
        return [memory for memory in self.memories if memory.user_id == user_id]


# ============================================================
# Fake LLM
# ============================================================


class FakeLLM:
    def __init__(
        self,
        extracted_memory=None,
        generated_response="Fake assistant response",
    ):
        self.extracted_memory = extracted_memory
        self.generated_response = generated_response

        self.extract_memories_calls = []
        self.generate_calls = []

    def extract_memories(self, user_message):
        self.extract_memories_calls.append(user_message)

        if self.extracted_memory is None:
            return []

        return [self.extracted_memory]

    def generate(
        self,
        prompt,
        history=None,
        memories=None,
    ):
        self.generate_calls.append(
            {
                "prompt": prompt,
                "history": history,
                "memories": memories,
            }
        )

        return self.generated_response


# ============================================================
# Fake User
# ============================================================


class FakeUser:
    def __init__(self, user_id):
        self.id = user_id


# ============================================================
# Test Helpers
# ============================================================


def create_conversation(user_id):
    conversation = Conversation(
        id=uuid4(),
        user_id=user_id,
        title="Test Conversation",
    )

    return conversation


def create_service(
    user_id,
    extracted_memory=None,
    generated_response="Fake assistant response",
):
    message_repository = FakeMessageRepository()

    conversation_repository = FakeConversationRepository()

    memory_service = FakeMemoryService()

    llm = FakeLLM(
        extracted_memory=extracted_memory,
        generated_response=generated_response,
    )

    conversation = create_conversation(user_id)

    conversation_repository.add(conversation)

    service = MessageService(
        repository=message_repository,
        conversation_repository=conversation_repository,
        memory_service=memory_service,
        llm=llm,
    )

    return (
        service,
        message_repository,
        conversation_repository,
        memory_service,
        llm,
        conversation,
    )


# ============================================================
# 1. Create Message + Generate Assistant Response
# ============================================================


def test_create_message_generates_assistant_response():
    user_id = uuid4()

    (
        service,
        message_repository,
        _,
        _,
        llm,
        conversation,
    ) = create_service(
        user_id=user_id,
        generated_response="Hello from the fake AI.",
    )

    result = service.create(
        conversation_id=conversation.id,
        current_user=FakeUser(user_id),
        content="Hello",
    )

    assert result["user_message"].role == "user"

    assert result["user_message"].content == "Hello"

    assert result["assistant_message"].role == "assistant"

    assert result["assistant_message"].content == "Hello from the fake AI."

    assert len(message_repository.messages) == 2

    assert len(llm.generate_calls) == 1

    assert llm.generate_calls[0]["prompt"] == "Hello"


# ============================================================
# 2. Memory Extraction + Saving
# ============================================================


def test_create_extracts_and_saves_memory():
    user_id = uuid4()

    extracted_memory = {
        "memory_type": "preference",
        "key": "favorite_programming_language",
        "value": "Python",
    }

    (
        service,
        _,
        _,
        memory_service,
        llm,
        conversation,
    ) = create_service(
        user_id=user_id,
        extracted_memory=extracted_memory,
    )

    service.create(
        conversation_id=conversation.id,
        current_user=FakeUser(user_id),
        content="My favorite programming language is Python.",
    )

    assert len(llm.extract_memories_calls) == 1

    assert (
        llm.extract_memories_calls[0] == "My favorite programming language is Python."
    )

    assert len(memory_service.saved_memories) == 1

    saved = memory_service.saved_memories[0]

    assert saved["user_id"] == user_id

    assert saved["memory"] == extracted_memory


# ============================================================
# 3. No Memory When Extraction Returns None
# ============================================================


def test_no_memory_is_saved_when_extraction_returns_none():
    user_id = uuid4()

    (
        service,
        _,
        _,
        memory_service,
        llm,
        conversation,
    ) = create_service(
        user_id=user_id,
        extracted_memory=None,
    )

    service.create(
        conversation_id=conversation.id,
        current_user=FakeUser(user_id),
        content="What is Python?",
    )

    assert len(llm.extract_memories_calls) == 1

    assert len(memory_service.saved_memories) == 0


# ============================================================
# 4. Long-Term Memories Are Sent To LLM
# ============================================================


def test_long_term_memories_are_sent_to_llm():
    user_id = uuid4()

    (
        service,
        _,
        _,
        memory_service,
        llm,
        conversation,
    ) = create_service(
        user_id=user_id,
    )

    # IMPORTANT:
    # Store a real Memory model object, not a dictionary.
    #
    # MessageService expects:
    # memory.memory_type
    # memory.key
    # memory.value

    memory = Memory(
        user_id=user_id,
        memory_type="preference",
        key="favorite_programming_language",
        value="Python",
    )

    memory_service.memories.append(memory)

    service.create(
        conversation_id=conversation.id,
        current_user=FakeUser(user_id),
        content="What is my favorite programming language?",
    )

    assert len(llm.generate_calls) == 1

    memories = llm.generate_calls[0]["memories"]

    assert len(memories) == 1

    assert memories[0]["memory_type"] == "preference"

    assert memories[0]["key"] == "favorite_programming_language"

    assert memories[0]["value"] == "Python"


# ============================================================
# 5. Previous Messages Are Sent As History
# ============================================================


def test_previous_messages_are_sent_as_history():
    user_id = uuid4()

    (
        service,
        message_repository,
        _,
        _,
        llm,
        conversation,
    ) = create_service(
        user_id=user_id,
    )

    previous_user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content="My name is Prem.",
    )

    previous_assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="Nice to meet you, Prem.",
    )

    message_repository.create(previous_user_message)

    message_repository.create(previous_assistant_message)

    service.create(
        conversation_id=conversation.id,
        current_user=FakeUser(user_id),
        content="What is my name?",
    )

    history = llm.generate_calls[0]["history"]

    assert len(history) == 2

    assert history[0] == {
        "role": "user",
        "content": "My name is Prem.",
    }

    assert history[1] == {
        "role": "assistant",
        "content": "Nice to meet you, Prem.",
    }


# ============================================================
# 6. User Cannot Access Another User's Conversation
# ============================================================


def test_user_cannot_send_message_to_another_users_conversation():
    owner_id = uuid4()

    attacker_id = uuid4()

    (
        service,
        message_repository,
        _,
        _,
        llm,
        conversation,
    ) = create_service(
        user_id=owner_id,
    )

    with pytest.raises(ValueError) as exc:
        service.create(
            conversation_id=conversation.id,
            current_user=FakeUser(attacker_id),
            content="This should not work.",
        )

    assert str(exc.value) == "Conversation not found"

    assert len(message_repository.messages) == 0

    assert len(llm.generate_calls) == 0

    assert len(llm.extract_memories_calls) == 0


# ============================================================
# 7. Nonexistent Conversation Fails
# ============================================================


def test_message_to_nonexistent_conversation_fails():
    user_id = uuid4()

    (
        service,
        message_repository,
        _,
        _,
        llm,
        _,
    ) = create_service(
        user_id=user_id,
    )

    with pytest.raises(ValueError) as exc:
        service.create(
            conversation_id=uuid4(),
            current_user=FakeUser(user_id),
            content="Hello",
        )

    assert str(exc.value) == "Conversation not found"

    assert len(message_repository.messages) == 0

    assert len(llm.generate_calls) == 0

    assert len(llm.extract_memories_calls) == 0


# ============================================================
# 8. Memory Extraction Failure Does Not Break Chat
# ============================================================


def test_memory_extraction_failure_does_not_break_chat():
    user_id = uuid4()

    message_repository = FakeMessageRepository()

    conversation_repository = FakeConversationRepository()

    memory_service = FakeMemoryService()

    conversation = create_conversation(user_id)

    conversation_repository.add(conversation)

    class FailingMemoryLLM:
        def extract_memories(self, user_message):
            raise RuntimeError("LLM memory extraction failed")

        def generate(
            self,
            prompt,
            history=None,
            memories=None,
        ):
            return "Chat still works."

    llm = FailingMemoryLLM()

    service = MessageService(
        repository=message_repository,
        conversation_repository=conversation_repository,
        memory_service=memory_service,
        llm=llm,
    )

    result = service.create(
        conversation_id=conversation.id,
        current_user=FakeUser(user_id),
        content="Hello",
    )

    assert result["user_message"].content == "Hello"

    assert result["assistant_message"].content == "Chat still works."

    assert len(message_repository.messages) == 2
