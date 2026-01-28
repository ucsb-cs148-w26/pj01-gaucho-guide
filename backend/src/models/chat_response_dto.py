from datetime import datetime
from pydantic import BaseModel, Field


class ChatResponseDTO(BaseModel):
    response: str
    model_name: str
    timestamp: datetime = Field(default_factory=datetime.now)
