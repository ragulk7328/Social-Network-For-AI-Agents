from pydantic import BaseModel, Field,  field_validator
from typing import List


class AgentCreate(BaseModel):
    agent_name: str = Field(..., min_length=2, max_length=100)
    company_name: str = Field(..., min_length=2, max_length=100)
    industry: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    interests: List[str] = Field(..., min_length=1, max_length=20)

    @field_validator("agent_name", "company_name", "industry", "description")
    @classmethod
    def validate_text(cls, value):
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value.strip()

    @field_validator("interests")
    @classmethod
    def validate_interests(cls, values):
        cleaned_values = [
            item.strip()
            for item in values
            if item.strip()
        ]

        if not cleaned_values:
            raise ValueError("At least one valid interest is required")

        return cleaned_values

class AgentUpdate(BaseModel):
    agent_name: str = Field(..., min_length=2, max_length=100)
    company_name: str = Field(..., min_length=2, max_length=100)
    industry: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    interests: List[str] = Field(..., min_length=1, max_length=20)

    @field_validator("agent_name", "company_name", "industry", "description")
    @classmethod
    def validate_text(cls, value):
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value.strip()

    @field_validator("interests")
    @classmethod
    def validate_interests(cls, values):
        cleaned_values = [
            item.strip()
            for item in values
            if item.strip()
        ]

        if not cleaned_values:
            raise ValueError("At least one valid interest is required")

        return cleaned_values

class PostCreate(BaseModel):
    agent_id: str
    content: str = Field(..., min_length=5, max_length=2000)
    category: str = Field(..., min_length=2, max_length=50)

    @field_validator("content", "category")
    @classmethod
    def validate_text(cls, value):
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value.strip()


class PostUpdate(BaseModel):
    content: str = Field(..., min_length=5, max_length=2000)
    category: str = Field(..., min_length=2, max_length=50)

    @field_validator("content", "category")
    @classmethod
    def validate_text(cls, value):
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value.strip()


class CommentCreate(BaseModel):
    post_id: str = Field(..., min_length=24, max_length=24)
    content: str = Field(..., min_length=2, max_length=1000)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value):
        if not value.strip():
            raise ValueError("Comment cannot be empty")
        return value.strip()

class SubscriptionCreate(BaseModel):
    agent_id: str = Field(..., min_length=24, max_length=24)
    target_agent_id: str = Field(..., min_length=24, max_length=24)

    @field_validator("agent_id", "target_agent_id")
    @classmethod
    def validate_ids(cls, value):
        if not value.strip():
            raise ValueError("Agent ID cannot be empty")
        return value.strip()

class FeedbackCreate(BaseModel):
    agent_id: str = Field(..., min_length=24, max_length=24)
    post_id: str = Field(..., min_length=24, max_length=24)
    notification_id: str = Field(..., min_length=24, max_length=24)
    feedback: str = Field(..., min_length=3, max_length=20)

    @field_validator("feedback")
    @classmethod
    def validate_feedback(cls, value):
        value = value.strip().lower()

        if value not in ["relevant", "not_relevant"]:
            raise ValueError(
                "Feedback must be relevant or not_relevant"
            )

        return value