# Objectives:
# This file defines all the API endpoints for managing mentor accounts.
# It provides a full set of RESTful routes for:
# - Creating a new mentor account.
# - Retrieving a list of all mentors.
# - Getting a single mentor by their ID.
# - Updating an existing mentor's details.
# - Deleting a mentor account.
# Note: These endpoints are designed for public sign-up and don't require authentication,
# but you can easily add authentication with `Depends(get_current_user)` if you need to.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

# Import our Pydantic schemas for data validation and API response models
from .. import schemas, data_models, auth
# Import the database session dependency
from ..database import get_db

# Initialize a new APIRouter with a tag for grouping these endpoints in the API documentation
router = APIRouter(tags=["Mentors"])

@router.post("/", response_model=schemas.MentorResponse, status_code=status.HTTP_201_CREATED)
def create_mentor(
    mentor: schemas.MentorCreate,
    db: Session = Depends(get_db)
):
    """
    Creates a new mentor account.
    """
    # Check if a mentor with the same email already exists in the database
    existing_mentor = db.exec(
        select(data_models.Mentor).where(data_models.Mentor.email == mentor.email)
    ).first()
    if existing_mentor:
        # Raise an HTTPException with a 409 Conflict status code if the email is already in use
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mentor with this email already exists"
        )
    
    # Hash the provided password before storing it for security
    hashed_password = auth.get_password_hash(mentor.password)
    
    # Create a new `Mentor` data model instance from the validated input
    db_mentor = data_models.Mentor(
        full_name=mentor.full_name,
        email=mentor.email,
        field=mentor.field,
        hashed_password=hashed_password
    )

    # Use a try-except block to handle potential database errors during the creation process
    try:
        # Add the new object to the session, commit, and refresh to get its ID
        db.add(db_mentor)
        db.commit()
        db.refresh(db_mentor)
        return db_mentor
    except Exception as e:
        # Rollback the transaction in case of an error to prevent partial commits
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the mentor: {e}"
        )

@router.get("/", response_model=List[schemas.MentorResponse])
def get_all_mentors(db: Session = Depends(get_db)):
    """
    Retrieves a list of all mentors from the database.
    """
    mentors = db.exec(select(data_models.Mentor)).all()
    return mentors

@router.get("/{mentor_id}", response_model=schemas.MentorResponse)
def get_mentor_by_id(mentor_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single mentor by their unique ID.
    """
    mentor = db.get(data_models.Mentor, mentor_id)
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found"
        )
    return mentor

@router.patch("/{mentor_id}", response_model=schemas.MentorResponse)
def update_mentor(
    mentor_id: int,
    mentor_update: schemas.MentorUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates an existing mentor's details.
    This is a PATCH endpoint, so it only updates the fields provided in the request body.
    """
    mentor = db.get(data_models.Mentor, mentor_id)
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found"
        )
    
    # Use model_dump to get only the fields that were set in the Pydantic update model
    mentor_data = mentor_update.model_dump(exclude_unset=True)
    
    # Check if the `password` is being updated and hash it before storing
    if "password" in mentor_data:
        mentor_data["hashed_password"] = auth.get_password_hash(mentor_data["password"])
        del mentor_data["password"] # Remove the plain-text password from the update dictionary
        
    # Loop through the update data and apply it to the database object
    for key, value in mentor_data.items():
        setattr(mentor, key, value)
    
    db.add(mentor)
    db.commit()
    db.refresh(mentor)
    return mentor

@router.delete("/{mentor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mentor(mentor_id: int, db: Session = Depends(get_db)):
    """
    Deletes a mentor account by their ID.
    """
    mentor = db.get(data_models.Mentor, mentor_id)
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found"
        )
    
    db.delete(mentor)
    db.commit()
    return {"message": "Mentor deleted"}
