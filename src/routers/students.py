# Objectives:
# This file defines the API endpoints for managing student accounts.
# It provides a complete set of RESTful routes for:
# - Creating a new student account with password hashing.
# - Retrieving a list of all students.
# - Getting a single student by their ID.
# - Updating a student's information, including handling password updates securely.
# - Deleting a student account.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

# Import Pydantic schemas, data models, and authentication utilities
from .. import schemas, data_models, auth
# Import the database session dependency
from ..database import get_db

# Initialize a new APIRouter with a tag for grouping these endpoints in the API documentation
router = APIRouter(tags=["Students"])

@router.post("/", response_model=schemas.StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db)
):
    """
    Creates a new student account, ensuring the email is unique and the password is
    securely hashed before being stored in the database.
    """
    # Check for an existing student with the same email to prevent duplicates
    existing_student = db.exec(
        select(data_models.Student).where(data_models.Student.email == student.email)
    ).first()
    if existing_student:
        # Raise a 409 Conflict error if the email already exists
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student with this email already exists"
        )
    
    # Use the utility function from the auth module to hash the plaintext password
    hashed_password = auth.get_password_hash(student.password)
    
    # Create the data model object for the student, using the hashed password
    db_student = data_models.Student(
        full_name=student.full_name,
        email=student.email,
        major=student.major,
        hashed_password=hashed_password
    )
    
    try:
        # Add the new student to the session, commit, and refresh to get the ID
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    except Exception as e:
        # Rollback the transaction on any error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the student: {e}"
        )

@router.get("/", response_model=List[schemas.StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    """
    Retrieves a list of all students.
    """
    students = db.exec(select(data_models.Student)).all()
    return students

@router.get("/{student_id}", response_model=schemas.StudentResponse)
def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single student by their ID.
    """
    student = db.get(data_models.Student, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return student

@router.patch("/{student_id}", response_model=schemas.StudentResponse)
def update_student(
    student_id: int,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates an existing student by their ID.
    This handles partial updates and ensures the password is re-hashed if updated.
    """
    student = db.get(data_models.Student, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Use Pydantic's `model_dump` with `exclude_unset=True` to get a dictionary of only
    # the fields that were provided in the request body.
    student_data = student_update.model_dump(exclude_unset=True)
    
    # Check if a new password was provided
    if "password" in student_data:
        # Hash the new password and add it to the data dictionary
        student_data["hashed_password"] = auth.get_password_hash(student_data["password"])
        # Remove the plaintext password to prevent it from being stored
        del student_data["password"]

    # Iterate through the provided data and update the student object
    for key, value in student_data.items():
        setattr(student, key, value)
    
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """
    Deletes a student by their ID.
    """
    student = db.get(data_models.Student, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    db.delete(student)
    db.commit()
    return {"message": "Student deleted"}
