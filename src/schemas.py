# Objective:
# This file defines the data schemas for the entire application using Pydantic and SQLModel.
# These schemas serve multiple purposes:
# 1. Data Validation: They ensure that all incoming API requests have the correct data structure and types.
# 2. API Documentation: They automatically generate clear and interactive API documentation.
# 3. Code Organization: They provide a consistent way to represent data across different parts of the application,
#    from the database models to the API endpoints.

from datetime import date, datetime
from typing import List, Optional
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

# --- Student Schemas ---

class StudentBase(SQLModel):
    """Base schema for a student, containing core attributes."""
    full_name: str
    email: str
    major: str

class StudentCreate(StudentBase):
    """Schema for creating a new student, includes the password field."""
    password: str

class StudentLogin(SQLModel):
    """Schema for student login validation, only requires email and password."""
    email: str
    password: str

class StudentUpdate(SQLModel):
    """Schema for updating an existing student, with all fields being optional."""
    full_name: Optional[str] = None
    major: Optional[str] = None
    password: Optional[str] = None

class StudentResponse(StudentBase):
    """Schema for an API response, includes the database-generated ID."""
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Mentor Schemas ---

class MentorBase(SQLModel):
    """Base schema for a mentor."""
    full_name: str
    email: str
    field: str

class MentorCreate(MentorBase):
    """Schema for creating a new mentor, includes the password field."""
    password: str

class MentorUpdate(SQLModel):
    """Schema for updating an existing mentor."""
    full_name: Optional[str] = None
    field: Optional[str] = None
    password: Optional[str] = None

class MentorResponse(MentorBase):
    """Schema for a mentor API response, includes the database-generated ID."""
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Employer Schemas ---

class EmployerBase(SQLModel):
    """Base schema for an employer."""
    company_name: str
    contact_person: str
    email: str
    industry: str

class EmployerCreate(EmployerBase):
    """Schema for creating a new employer, includes the password field."""
    password: str

class EmployerUpdate(SQLModel):
    """Schema for updating an existing employer."""
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    industry: Optional[str] = None
    password: Optional[str] = None

class EmployerResponse(EmployerBase):
    """Schema for an employer API response, includes the database-generated ID."""
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Placement Schemas ---

class PlacementBase(SQLModel):
    """Base schema for a placement, defining core attributes and foreign keys."""
    title: str
    description: str
    start_date: date
    end_date: date
    status: str
    employer_id: int = Field(foreign_key="employer.id")
    mentor_id: int = Field(foreign_key="mentor.id")

class PlacementCreate(PlacementBase):
    """Schema for creating a new placement, including a list of associated students."""
    student_ids: List[int]

class PlacementUpdate(SQLModel):
    """Schema for updating a placement, with all fields being optional."""
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    student_ids: Optional[List[int]] = None

class PlacementResponse(PlacementBase):
    """Schema for a placement API response, includes the database ID and student IDs."""
    id: int
    student_ids: List[int]
    model_config = ConfigDict(from_attributes=True)

# --- Evaluation Schemas ---

class EvaluationBase(SQLModel):
    """Base schema for a placement evaluation, with foreign keys to all user types."""
    feedback: str
    rating: int
    placement_id: int = Field(foreign_key="placement.id")
    subject_id: int
    mentor_evaluator_id: Optional[int] = Field(None, foreign_key="mentor.id")
    employer_evaluator_id: Optional[int] = Field(None, foreign_key="employer.id")
    student_evaluator_id: Optional[int] = Field(None, foreign_key="student.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EvaluationCreate(EvaluationBase):
    """Schema for creating a new evaluation."""
    pass

class EvaluationUpdate(SQLModel):
    """Schema for updating an existing evaluation."""
    feedback: Optional[str] = None
    rating: Optional[int] = None

class EvaluationResponse(EvaluationBase):
    """Schema for an evaluation API response, includes the database ID."""
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Authentication Schemas ---

class Token(SQLModel):
    """Schema for the access token returned on a successful login."""
    access_token: str
    token_type: str

class TokenData(SQLModel):
    """Schema to hold the payload of the JWT token, typically the user's email."""
    email: Optional[str] = None
