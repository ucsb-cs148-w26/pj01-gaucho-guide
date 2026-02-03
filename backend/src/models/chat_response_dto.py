from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Union, List, Dict

#class ChatResponseDTO(BaseModel):
#    response: str
#    model_name: str
#    timestamp: datetime = Field(default_factory=datetime.now)


class ChatResponseDTO(BaseModel):
    response: Union[str, List[Dict[str, Any]]]
    model_name: str