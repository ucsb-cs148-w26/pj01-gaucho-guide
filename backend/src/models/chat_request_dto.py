import uuid
from typing import List, Union, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel


#class ChatRequestDTO(BaseModel):
#    chat_history: List[Union[HumanMessage, AIMessage, SystemMessage]]
#    chat_session_id: uuid.UUID 
#    model_name: str

class ChatRequestDTO(BaseModel):
    chat_session_id: str
    message: str
    model_name: Optional[str] = None