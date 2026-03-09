from pydantic import BaseModel
from typing import Any, Union, List, Dict


class ChatResponseDTO(BaseModel):
    response: Union[str, List[Dict[str, Any]]]
    model_name: str