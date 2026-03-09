from typing import Optional
from pydantic import BaseModel


class ChatRequestDTO(BaseModel):
    chat_session_id: str
    message: str
    model_name: Optional[str] = None