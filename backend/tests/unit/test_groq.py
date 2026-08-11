from types import SimpleNamespace

import pytest

from app.llm.groq import GroqLLM

# ============================================================
# Fake Groq client
# ============================================================


class FakeCompletions:
    def __init__(self, response):
        self.response = response
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return self.response


class FakeChat:
    def __init__(self, response):
        self.completions = FakeCompletions(response)


class FakeGroqClient:
    def __init__(self, response):
        self.chat = FakeChat(response)


# ============================================================
# Helpers
# ============================================================


def fake_response(content):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=content,
                )
            )
        ]
    )


def create_llm(response):
    llm = GroqLLM.__new__(GroqLLM)

    llm.client = FakeGroqClient(fake_response(response))

    llm.model = "test-model"

    return llm


# ============================================================
# Generate tests
# ============================================================


def test_generate_returns_assistant_response():
    llm = create_llm("Hello! How can I help you?")

    result = llm.generate(
        "Hello",
    )

    assert result == "Hello! How can I help you?"

    request = llm.client.chat.completions.last_kwargs

    assert request["model"] == "test-model"

    assert request["messages"][-1] == {
        "role": "user",
        "content": "Hello",
    }


def test_generate_includes_conversation_history():
    llm = create_llm("I remember our conversation.")

    history = [
        {
            "role": "user",
            "content": "My name is Prem.",
        },
        {
            "role": "assistant",
            "content": "Nice to meet you, Prem.",
        },
    ]

    llm.generate(
        "What is my name?",
        history=history,
    )

    messages = llm.client.chat.completions.last_kwargs["messages"]

    assert {
        "role": "user",
        "content": "My name is Prem.",
    } in messages

    assert {
        "role": "assistant",
        "content": "Nice to meet you, Prem.",
    } in messages


def test_generate_includes_long_term_memories():
    llm = create_llm("Your favorite language is Python.")

    memories = [
        {
            "memory_type": "preference",
            "key": "favorite_programming_language",
            "value": "Python",
        }
    ]

    llm.generate(
        "What is my favorite programming language?",
        memories=memories,
    )

    messages = llm.client.chat.completions.last_kwargs["messages"]

    # Find only the dedicated memory-context message.
    memory_messages = [
        message
        for message in messages
        if (
            message["role"] == "system"
            and message["content"].startswith("Long-term memories about the user:")
        )
    ]

    assert len(memory_messages) == 1

    memory_content = memory_messages[0]["content"]

    assert "favorite_programming_language" in memory_content

    assert "Python" in memory_content


def test_generate_ignores_invalid_history_roles():
    llm = create_llm("Response")

    history = [
        {
            "role": "user",
            "content": "Valid user message",
        },
        {
            "role": "system",
            "content": "Should not be copied",
        },
        {
            "role": "tool",
            "content": "Should not be copied",
        },
        {
            "role": "assistant",
            "content": "Valid assistant message",
        },
    ]

    llm.generate(
        "Current question",
        history=history,
    )

    messages = llm.client.chat.completions.last_kwargs["messages"]

    assert {
        "role": "user",
        "content": "Valid user message",
    } in messages

    assert {
        "role": "assistant",
        "content": "Valid assistant message",
    } in messages

    assert not any(
        message.get("content") == "Should not be copied" for message in messages
    )


def test_generate_raises_when_llm_returns_empty_response():
    llm = create_llm("")

    with pytest.raises(
        ValueError,
        match="LLM returned an empty response",
    ):
        llm.generate("Hello")


# ============================================================
# Memory extraction tests
# ============================================================


def test_extract_memory_returns_valid_memory():
    llm = create_llm(
        """
        {
            "memory_type": "preference",
            "key": "favorite_programming_language",
            "value": "Python"
        }
        """
    )

    result = llm.extract_memory("My favorite programming language is Python.")

    assert result == {
        "memory_type": "preference",
        "key": "favorite_programming_language",
        "value": "Python",
    }


def test_extract_memory_handles_markdown_json():
    llm = create_llm(
        """```json
{
    "memory_type": "identity",
    "key": "name",
    "value": "Prem"
}
```"""
    )

    result = llm.extract_memory("My name is Prem.")

    assert result == {
        "memory_type": "identity",
        "key": "name",
        "value": "Prem",
    }


def test_extract_memory_returns_none_for_null():
    llm = create_llm("null")

    result = llm.extract_memory("What is Python?")

    assert result is None


def test_extract_memory_returns_none_for_invalid_json():
    llm = create_llm("This is not JSON.")

    result = llm.extract_memory("My name is Prem.")

    assert result is None


def test_extract_memory_returns_none_for_missing_fields():
    llm = create_llm(
        """
        {
            "memory_type": "identity",
            "key": "name"
        }
        """
    )

    result = llm.extract_memory("My name is Prem.")

    assert result is None


def test_extract_memory_returns_none_for_empty_fields():
    llm = create_llm(
        """
        {
            "memory_type": "identity",
            "key": "",
            "value": "Prem"
        }
        """
    )

    result = llm.extract_memory("My name is Prem.")

    assert result is None


def test_extract_memory_strips_whitespace():
    llm = create_llm(
        """
        {
            "memory_type": " preference ",
            "key": " favorite_language ",
            "value": " Python "
        }
        """
    )

    result = llm.extract_memory("My favorite language is Python.")

    assert result == {
        "memory_type": "preference",
        "key": "favorite_language",
        "value": "Python",
    }
