from typing import Optional, Literal
from datetime import datetime
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
