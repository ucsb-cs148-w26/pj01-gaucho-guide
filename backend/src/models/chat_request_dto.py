import uuid
from typing import List

from langchain_core.messages import BaseMessage
from pydantic import BaseModel


class ChatRequestDTO(BaseModel):
    chat_history: List[BaseMessage]
    chat_session_id: uuid
    model_name: str
