from pydantic import BaseModel


class ModelResponse(BaseModel):
    id: str
    name: str
    provider: str
    description: str
    available: bool
