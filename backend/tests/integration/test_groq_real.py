import pytest

from app.core.config import settings
from app.llm.groq import GroqLLM


@pytest.mark.skipif(
    not settings.GROQ_API_KEY,
    reason="GROQ_API_KEY is not configured",
)
def test_real_groq_generate():
    llm = GroqLLM()

    response = llm.generate("Reply with exactly: GROQ_TEST_OK")

    assert response
    assert isinstance(response, str)
    assert response.strip()


@pytest.mark.skipif(
    not settings.GROQ_API_KEY,
    reason="GROQ_API_KEY is not configured",
)
def test_real_groq_memory_extraction():
    llm = GroqLLM()

    memories = llm.extract_memories("My favorite programming language is Python.")

    assert isinstance(memories, list)
    assert len(memories) >= 1

    assert any(
        memory["memory_type"] == "preference"
        and memory["key"] == "favorite_programming_language"
        and memory["value"] == "Python"
        for memory in memories
    )
