# This file defines the database models for the application using SQLModel.
# SQLModel provides a convenient way to define data models that are
# also ready to be used as database tables.

from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import date, datetime

# --- Link Models for Many-to-Many Relationships ---
# These are "association tables" used to handle many-to-many relationships
# without needing a separate model for the link itself.

class StudentPlacementLink(SQLModel, table=True):
    """
    Association table to connect Students and Placements.
    A student can have many placements, and a placement can have many students.
    """
    student_id: Optional[int] = Field(default=None, foreign_key="student.id", primary_key=True)
    placement_id: Optional[int] = Field(default=None, foreign_key="placement.id", primary_key=True)

class MentorStudentLink(SQLModel, table=True):
    """
    Association table to connect Mentors and Students.
    A mentor can mentor many students, and a student can have many mentors.
    """
    mentor_id: Optional[int] = Field(default=None, foreign_key="mentor.id", primary_key=True)
    student_id: Optional[int] = Field(default=None, foreign_key="student.id", primary_key=True)

# --- Main Data Models ---

class Student(SQLModel, table=True):
    """
    Represents a student in the system.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    email: str = Field(unique=True, index=True) # Email must be unique and is indexed for faster lookups.
    major: str
    hashed_password: str

    # Define relationships with other models.
    # The 'Relationship' class creates the links between tables.
    placements: List["Placement"] = Relationship(back_populates="students", link_model=StudentPlacementLink)
    mentors: List["Mentor"] = Relationship(back_populates="students", link_model=MentorStudentLink)
    
    # Relationships for evaluations given and received by students.
    # The 'sa_relationship_kwargs' are used here to distinguish between two
    # different relationships with the same table (Evaluation).
    evaluations_given: List["Evaluation"] = Relationship(
        back_populates="student_evaluator",
        sa_relationship_kwargs={"foreign_keys": "Evaluation.student_evaluator_id"}
    )
    evaluations_received: List["Evaluation"] = Relationship(
        back_populates="subject",
        sa_relationship_kwargs={"foreign_keys": "Evaluation.subject_id"}
    )

class Mentor(SQLModel, table=True):
    """
    Represents a mentor in the system.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    email: str = Field(unique=True, index=True)
    field: str
    hashed_password: str

    # Define relationships.
    students: List["Student"] = Relationship(back_populates="mentors", link_model=MentorStudentLink)
    placements: List["Placement"] = Relationship(back_populates="mentor")
    evaluations_given: List["Evaluation"] = Relationship(
        back_populates="mentor_evaluator",
        sa_relationship_kwargs={"foreign_keys": "Evaluation.mentor_evaluator_id"}
    )

class Employer(SQLModel, table=True):
    """
    Represents an employer or company.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    company_name: str
    email: str = Field(unique=True, index=True)
    contact_person: str
    industry: str
    hashed_password: str

    # Define relationships.
    placements: List["Placement"] = Relationship(back_populates="employer")
    evaluations_given: List["Evaluation"] = Relationship(
        back_populates="employer_evaluator",
        sa_relationship_kwargs={"foreign_keys": "Evaluation.employer_evaluator_id"}
    )

class Placement(SQLModel, table=True):
    """
    Represents an internship or job placement.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    start_date: date
    end_date: date
    status: str

    # Define foreign keys to link to other tables.
    employer_id: Optional[int] = Field(default=None, foreign_key="employer.id")
    mentor_id: Optional[int] = Field(default=None, foreign_key="mentor.id")

    # Define relationships.
    employer: Optional["Employer"] = Relationship(back_populates="placements")
    mentor: Optional["Mentor"] = Relationship(back_populates="placements")
    students: List["Student"] = Relationship(back_populates="placements", link_model=StudentPlacementLink)
    evaluations: List["Evaluation"] = Relationship(back_populates="placement")

class Evaluation(SQLModel, table=True):
    """
    Represents an evaluation or feedback form.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    feedback: str
    rating: int
    created_at: datetime = Field(default_factory=datetime.utcnow) # Automatically sets the creation time.

    # Define foreign keys. A single evaluation can link to multiple types of users
    # (subject of evaluation, mentor who evaluated, etc.)
    placement_id: Optional[int] = Field(default=None, foreign_key="placement.id")
    subject_id: Optional[int] = Field(default=None, foreign_key="student.id")
    mentor_evaluator_id: Optional[int] = Field(default=None, foreign_key="mentor.id")
    employer_evaluator_id: Optional[int] = Field(default=None, foreign_key="employer.id")
    student_evaluator_id: Optional[int] = Field(default=None, foreign_key="student.id")

    # Define relationships to access linked objects.
    placement: Optional["Placement"] = Relationship(back_populates="evaluations")
    subject: Optional["Student"] = Relationship(
        back_populates="evaluations_received",
        sa_relationship_kwargs={"foreign_keys": "Evaluation.subject_id"}
    )
    mentor_evaluator: Optional["Mentor"] = Relationship(
        back_populates="evaluations_given",
        sa_relationship_kwargs={"foreign_keys": "Evaluation.mentor_evaluator_id"}
    )
    employer_evaluator: Optional["Employer"] = Relationship(
        back_populates="evaluations_given",
        sa_relationship_kwargs={"foreign_keys": "Evaluation.employer_evaluator_id"}
    )
    student_evaluator: Optional["Student"] = Relationship(
        back_populates="evaluations_given",
        sa_relationship_kwargs={"foreign_keys": "Evaluation.student_evaluator_id"}
    )
