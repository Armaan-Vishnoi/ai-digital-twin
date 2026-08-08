from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime


class MessagePairResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse