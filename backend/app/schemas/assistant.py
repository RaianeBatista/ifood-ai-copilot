from pydantic import BaseModel, Field


class AssistantQuestion(BaseModel):
    restaurant_id: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=3, max_length=2000)


class AssistantAnswer(BaseModel):
    answer: str
    sources: list[str]
