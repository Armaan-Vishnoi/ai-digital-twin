from app.core.config import settings
from app.llm.groq import GroqLLM


def get_llm():

    if settings.LLM_PROVIDER == "groq":
        return GroqLLM()

    raise ValueError("Unsupported provider")