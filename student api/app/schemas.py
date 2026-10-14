"""Pydantic models: request validation and response shapes."""
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
PHONE_PATTERN = r"^\+?[0-9\s\-()]{7,20}$"


class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    email: Optional[str] = Field(None, pattern=EMAIL_PATTERN)
    phone: Optional[str] = Field(None, pattern=PHONE_PATTERN)
    course: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    enrollment_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be blank")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def dob_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return v


class StudentCreate(StudentBase):
    @model_validator(mode="after")
    def need_contact(self):
        if not self.email and not self.phone:
            raise ValueError("provide at least one of email or phone")
        return self


class StudentUpdate(BaseModel):
    """All fields optional - used for PUT/PATCH partial updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[str] = Field(None, pattern=EMAIL_PATTERN)
    phone: Optional[str] = Field(None, pattern=PHONE_PATTERN)
    course: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    enrollment_date: Optional[date] = None

    @field_validator("date_of_birth")
    @classmethod
    def dob_not_future(cls, v):
        if v is not None and v > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return v


class Student(StudentBase):
    id: int


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)


class AskResponse(BaseModel):
    question: str
    answer: str
    records_used: int
    model: str
