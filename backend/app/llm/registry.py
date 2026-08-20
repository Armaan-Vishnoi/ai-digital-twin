from app.llm.base import BaseLLM
from app.llm.groq import GroqLLM
from app.llm.models import DEFAULT_MODEL_ID, MODELS, ModelInfo


class ModelRegistry:
    def __init__(self) -> None:
        self._models = {model.id: model for model in MODELS}

    def list_models(self) -> list[ModelInfo]:
        return list(self._models.values())

    def get_model_info(self, model_id: str) -> ModelInfo:
        model = self._models.get(model_id)

        if model is None:
            raise ValueError(f"Unknown model: {model_id}")

        return model

    def resolve_model_id(self, model_id: str) -> str:
        if model_id == "auto":
            return DEFAULT_MODEL_ID

        self.get_model_info(model_id)

        return model_id

    def get_llm(self, model_id: str) -> BaseLLM:
        model = self.get_model_info(model_id)

        if model.provider == "groq":
            return GroqLLM()

        raise ValueError(f"Unsupported model provider: {model.provider}")
