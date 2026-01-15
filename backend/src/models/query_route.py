from pydantic import BaseModel, Field
from typing import Literal


class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    namespace: Literal["professor_data", "student_reviews"] = Field(description="Given a user question, choose which "
                                                                                "dataset is most relevant.")
