from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)
    model: str = "auto"


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    model: str | None
    created_at: datetime


class MessagePairResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
