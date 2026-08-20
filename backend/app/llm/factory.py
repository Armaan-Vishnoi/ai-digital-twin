from app.core.config import settings
from app.llm.base import BaseLLM
from app.llm.groq import GroqLLM

SUPPORTED_MODELS = {
    "groq",
}


def get_llm(model: str = "auto") -> BaseLLM:
    selected_model = model.strip().lower()

    if selected_model == "auto":
        selected_model = settings.LLM_PROVIDER.strip().lower()

    if selected_model == "groq":
        return GroqLLM()

    raise ValueError(f"Unsupported LLM model: {model}")
