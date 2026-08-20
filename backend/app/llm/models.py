from dataclasses import dataclass


@dataclass(frozen=True)
class ModelInfo:
    id: str
    name: str
    provider: str
    description: str
    available: bool = True


DEFAULT_MODEL_ID = "groq:openai/gpt-oss-120b"


MODELS: list[ModelInfo] = [
    ModelInfo(
        id=DEFAULT_MODEL_ID,
        name="GPT OSS 120B",
        provider="groq",
        description="Large reasoning model running through Groq.",
    ),
]
