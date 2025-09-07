# Objectives:
# This file handles the registration of all user types (Student, Mentor, Employer).
# It provides three separate POST endpoints to create a new user account for each role.
#
# - It ensures that no two users can register with the same email address.
# - It uses a password hashing utility to securely store user passwords.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
# Import the database session dependency
from ..database import get_db
# Import the data models for each user type
from ..data_models import Student, Mentor, Employer
# Import the Pydantic schemas for data validation
from ..schemas import StudentCreate, MentorCreate, EmployerCreate
# Import the password hashing utility
from ..utils import get_password_hash

# Initialize a new APIRouter with a prefix and tags for documentation
router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/register/student", response_model=StudentCreate, status_code=status.HTTP_201_CREATED)
def create_student_user(student: StudentCreate, db: Session = Depends(get_db)):
    """
    Registers a new student account.
    """
    # Check if a student with the same email already exists in the database
    db_user = db.exec(select(Student).where(Student.email == student.email)).first()
    if db_user:
        # Raise an HTTPException if the email is already registered
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the provided password for secure storage
    hashed_password = get_password_hash(student.password)
    db_student = Student(
        full_name=student.full_name,
        email=student.email,
        major=student.major,
        hashed_password=hashed_password,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.post("/register/mentor", response_model=MentorCreate, status_code=status.HTTP_201_CREATED)
def create_mentor_user(mentor: MentorCreate, db: Session = Depends(get_db)):
    """
    Registers a new mentor account.
    """
    # Check if a mentor with the same email already exists
    db_user = db.exec(select(Mentor).where(Mentor.email == mentor.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(mentor.password)
    db_mentor = Mentor(
        full_name=mentor.full_name,
        email=mentor.email,
        field=mentor.field,
        hashed_password=hashed_password,
    )
    db.add(db_mentor)
    db.commit()
    db.refresh(db_mentor)
    return db_mentor

@router.post("/register/employer", response_model=EmployerCreate, status_code=status.HTTP_201_CREATED)
def create_employer_user(employer: EmployerCreate, db: Session = Depends(get_db)):
    """
    Registers a new employer account.
    """
    # Check if an employer with the same email already exists
    db_user = db.exec(select(Employer).where(Employer.email == employer.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(employer.password)
    db_employer = Employer(
        company_name=employer.company_name,
        email=employer.email,
        industry=employer.industry,
        hashed_password=hashed_password,
    )
    db.add(db_employer)
    db.commit()
    db.refresh(db_employer)
    return db_employer
