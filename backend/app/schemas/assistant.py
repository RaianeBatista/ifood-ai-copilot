from pydantic import BaseModel, Field


class AssistantConversationTurn(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    answer: str = Field(min_length=1, max_length=1000)


class AssistantQuestion(BaseModel):
    restaurant_id: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=3, max_length=2000)
    history: list[AssistantConversationTurn] = Field(default_factory=list, max_length=4)


class AssistantAnswer(BaseModel):
    answer: str
    sources: list[str]
