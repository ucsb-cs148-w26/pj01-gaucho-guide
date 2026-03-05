from pydantic import BaseModel, Field
from typing import Literal


class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""
    namespace: Literal["professor_data", "school_reviews", "reddit_class_data"] = Field(
        description=(
            "Choose professor_data for teacher info, "
            "school_reviews for broad campus sentiment, or "
            "reddit_class_data for course-specific student experiences/discussion."
        )
    )
