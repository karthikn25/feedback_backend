from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class FeedbackRating(str, Enum):
    very_good = "😄"
    good = "🙂"
    average = "😐"
    bad = "🙁"
    very_bad = "😞"


REQUIRES_MESSAGE = {FeedbackRating.average, FeedbackRating.bad, FeedbackRating.very_bad}


class Feedback(BaseModel):
    id: Optional[str] = None
    name: str
    userId: str
    rating: FeedbackRating
    feedbackMessage: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    @model_validator(mode="after")
    def message_required_for_negative(self) -> "Feedback":
        if self.rating in REQUIRES_MESSAGE and not self.feedbackMessage:
            raise ValueError("feedbackMessage is required for 😐, 🙁 or 😞 rating")
        return self

    model_config = {"from_attributes": True}