from datetime import datetime

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
from typing import Literal


class ChatResponseDTO(BaseModel):
    response: str
    model_name: str
    timestamp: datetime = Field(default_factory=datetime.now())
