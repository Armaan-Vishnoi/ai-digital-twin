from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MemoryCreate(BaseModel):
    memory_type: str
    key: str
    value: str


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    memory_type: str
    key: str
    value: str
    created_at: datetime
    updated_at: datetime
