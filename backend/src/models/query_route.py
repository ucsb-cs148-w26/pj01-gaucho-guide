from pydantic import BaseModel, Field
from typing import Literal


class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""
    namespace: Literal["professor_data", "school_reviews"] = Field(
        description="Choose school_reviews for general campus life or professor_data for teacher info."
    )
