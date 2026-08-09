import pytest

from app.core.config import settings
from app.llm.groq import GroqLLM


pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not settings.GROQ_API_KEY,
    reason="GROQ_API_KEY is not configured",
)
def test_real_groq_generate():
    llm = GroqLLM()

    response = llm.generate(
        "Reply with exactly: REAL GROQ TEST PASSED"
    )

    assert response
    assert isinstance(response, str)
    assert len(response.strip()) > 0


@pytest.mark.skipif(
    not settings.GROQ_API_KEY,
    reason="GROQ_API_KEY is not configured",
)
def test_real_groq_memory_extraction():
    llm = GroqLLM()

    memory = llm.extract_memory(
        "My favorite programming language is Python."
    )

    assert memory is not None

    assert memory["memory_type"]
    assert memory["key"]
    assert memory["value"]

    assert memory["value"].lower() == "python"