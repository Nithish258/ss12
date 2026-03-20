from typing import Optional, Literal
from datetime import datetime
from uuid import UUID
import uuid
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class RegisterRequest(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Must contain uppercase')
        if not re.search(r'[a-z]', v):
            raise ValueError('Must contain lowercase')
        if not re.search(r'\d', v):
            raise ValueError('Must contain a number')
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CreateDecisionRequest(BaseModel):
    title: str = Field(min_length=1)
    context_prompt: Optional[str] = None
    deadline: Optional[datetime] = None

class UpdateDecisionRequest(BaseModel):
    title: Optional[str] = None
    context_prompt: Optional[str] = None
    deadline: Optional[datetime] = None

class InviteParticipantRequest(BaseModel):
    email: EmailStr
    role: Literal['owner', 'contributor', 'observer']

class ParticipantResponse(BaseModel):
    user_id: UUID
    role: str
    has_submitted: bool

    model_config = {"from_attributes": True}

class UpsertSubmissionRequest(BaseModel):
    raw_reasoning: str = Field(min_length=1)
    confidence_score: int

    @field_validator('confidence_score')
    @classmethod
    def validate_confidence(cls, v: int) -> int:
        if v < 1 or v > 10:
            raise ValueError('confidence_score must be between 1 and 10')
        return v

class StateTransitionResponse(BaseModel):
    decision_id: str
    old_state: str
    new_state: str

class SubmissionResponse(BaseModel):
    id: uuid.UUID
    decision_id: uuid.UUID
    user_id: uuid.UUID
    raw_reasoning: str
    confidence_score: int
    is_locked: bool
    submitted_at: datetime

    model_config = {"from_attributes": True}
