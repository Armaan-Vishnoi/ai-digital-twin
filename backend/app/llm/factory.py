from app.core.config import settings
from app.llm.base import BaseLLM
from app.llm.groq import GroqLLM


def get_llm() -> BaseLLM:
    provider = settings.LLM_PROVIDER.strip().lower()

    if provider == "groq":
        return GroqLLM()

    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
