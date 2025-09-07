# Objectives:
# This file defines all the API endpoints for managing employer resources.
# It provides a full set of RESTful routes for:
# - Creating a new employer account.
# - Retrieving a list of all employers.
# - Getting a single employer by their ID.
# - Updating an existing employer's details.
# - Deleting an employer account.
# Note: Unlike cohorts, these endpoints do not require authentication for most operations
# to allow for public sign-up, but you may add authentication with `Depends(get_current_user)`
# if you want to restrict who can manage this data.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

# Import our Pydantic schemas for data validation and API response models
from .. import schemas, data_models
# Import the database session dependency
from ..database import get_db
# Import the password hashing utility from our auth module
from ..auth import get_password_hash

# Initialize a new APIRouter with a tag for grouping these endpoints in the API documentation
router = APIRouter(tags=["Employers"])

@router.post("/", response_model=schemas.EmployerResponse, status_code=status.HTTP_201_CREATED)
def create_employer(
    employer: schemas.EmployerCreate,
    db: Session = Depends(get_db)
):
    """
    Creates a new employer account.
    The user provides a Pydantic `EmployerCreate` object in the request body,
    which includes the password to be hashed.
    """
    # Check if an employer with the same email already exists in the database
    existing_employer = db.exec(
        select(data_models.Employer).where(data_models.Employer.email == employer.email)
    ).first()
    if existing_employer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Use a try-except block to handle potential database errors during the creation process
    try:
        # Hash the password before saving it to the database for security
        hashed_password = get_password_hash(employer.password)
        # Create a new `Employer` data model instance from the validated input
        db_employer = data_models.Employer(
            company_name=employer.company_name,
            email=employer.email,
            contact_person=employer.contact_person,
            industry=employer.industry,
            hashed_password=hashed_password
        )
        # Add, commit, and refresh the new object to get its ID from the database
        db.add(db_employer)
        db.commit()
        db.refresh(db_employer)
        return db_employer
    except Exception as e:
        # Rollback the transaction in case of an error to prevent partial commits
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the employer: {e}"
        )

@router.get("/", response_model=List[schemas.EmployerResponse])
def get_all_employers(db: Session = Depends(get_db)):
    """
    Retrieves a list of all employers from the database.
    """
    employers = db.exec(select(data_models.Employer)).all()
    return employers

@router.get("/{employer_id}", response_model=schemas.EmployerResponse)
def get_employer_by_id(employer_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single employer by their unique ID.
    """
    employer = db.get(data_models.Employer, employer_id)
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employer not found"
        )
    return employer

@router.patch("/{employer_id}", response_model=schemas.EmployerResponse)
def update_employer(
    employer_id: int,
    employer_update: schemas.EmployerUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates an existing employer's details.
    This is a PATCH endpoint, so it only updates the fields provided in the request body.
    """
    employer = db.get(data_models.Employer, employer_id)
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employer not found"
        )
    
    # Get the data from the Pydantic update model, excluding any unset fields
    employer_data = employer_update.model_dump(exclude_unset=True)
    for key, value in employer_data.items():
        # Special handling for password: hash it before updating the `hashed_password` attribute
        if key == "password":
            setattr(employer, "hashed_password", get_password_hash(value))
        else:
            setattr(employer, key, value)
    
    db.add(employer)
    db.commit()
    db.refresh(employer)
    return employer

@router.delete("/{employer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employer(employer_id: int, db: Session = Depends(get_db)):
    """
    Deletes an employer account by their ID.
    """
    employer = db.get(data_models.Employer, employer_id)
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employer not found"
        )
    
    db.delete(employer)
    db.commit()
    return {"message": "Employer deleted"}
