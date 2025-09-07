# Objectives:
# This file defines the API endpoints for managing Cohort resources.
# It provides a complete set of RESTful routes for:
# - Creating a new cohort.
# - Retrieving a list of all cohorts.
# - Fetching a single cohort by its ID.
# - Updating an existing cohort.
# - Deleting a cohort.
# All routes are protected and require a valid JWT token for access.

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime

# Import database session dependency
from ..database import get_db
# Import the data model for cohorts
from ..data_models import Cohort
# Import the Pydantic schemas for request and response validation
from ..schemas import Cohort as CohortSchema, CohortCreate, CohortUpdate
# Import the dependency to get the current authenticated user
from ..auth import get_current_user

# Initialize a new APIRouter with a common prefix and tag for all cohort-related routes
router = APIRouter(prefix="/cohorts", tags=["cohorts"])

@router.post("/", response_model=CohortSchema, status_code=status.HTTP_201_CREATED, summary="Create a new cohort")
def create_cohort(*, session: Session = Depends(get_db), cohort: CohortCreate, user=Depends(get_current_user)):
    """
    Creates a new cohort in the database.
    This endpoint requires a valid JWT token, as indicated by the `user=Depends(get_current_user)` dependency.

    Args:
        session: The database session.
        cohort: A Pydantic model containing the new cohort's data (name and optional description).
    
    Returns:
        The newly created cohort object, including its database-generated ID.
    """
    db_cohort = Cohort.model_validate(cohort)
    session.add(db_cohort)
    session.commit()
    session.refresh(db_cohort)
    return db_cohort

@router.get("/", response_model=List[CohortSchema], summary="Get all cohorts")
def get_all_cohorts(*, session: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Retrieves a list of all cohorts from the database.
    """
    cohorts = session.exec(select(Cohort)).all()
    return cohorts

@router.get("/{cohort_id}", response_model=CohortSchema, summary="Get a single cohort by ID")
def get_cohort(*, session: Session = Depends(get_db), cohort_id: int, user=Depends(get_current_user)):
    """
    Retrieves a single cohort by its unique ID.

    Args:
        session: The database session.
        cohort_id: The ID of the cohort to retrieve.

    Returns:
        The cohort object matching the provided ID.

    Raises:
        HTTPException: If no cohort is found with the given ID.
    """
    cohort = session.get(Cohort, cohort_id)
    if not cohort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cohort not found"
        )
    return cohort

@router.patch("/{cohort_id}", response_model=CohortSchema, summary="Update an existing cohort")
def update_cohort(*, session: Session = Depends(get_db), cohort_id: int, cohort: CohortUpdate, user=Depends(get_current_user)):
    """
    Updates an existing cohort in the database.
    This is a PATCH endpoint, meaning only the fields provided in the request body will be updated.

    Args:
        session: The database session.
        cohort_id: The ID of the cohort to update.
        cohort: A Pydantic model with the fields to be updated.
    
    Returns:
        The updated cohort object.

    Raises:
        HTTPException: If no cohort is found with the given ID.
    """
    db_cohort = session.get(Cohort, cohort_id)
    if not db_cohort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cohort not found"
        )
    # Get the provided update data, ignoring any fields that were not set
    cohort_data = cohort.model_dump(exclude_unset=True)
    # Loop through the update data and apply it to the database object
    for key, value in cohort_data.items():
        setattr(db_cohort, key, value)
    
    # Update the `updated_at` timestamp
    db_cohort.updated_at = datetime.utcnow()
    
    session.add(db_cohort)
    session.commit()
    session.refresh(db_cohort)
    return db_cohort

@router.delete("/{cohort_id}", summary="Delete a cohort", status_code=status.HTTP_204_NO_CONTENT)
def delete_cohort(*, session: Session = Depends(get_db), cohort_id: int, user=Depends(get_current_user)):
    """
    Deletes a cohort from the database.

    Args:
        session: The database session.
        cohort_id: The ID of the cohort to delete.

    Raises:
        HTTPException: If no cohort is found with the given ID.
    """
    cohort = session.get(Cohort, cohort_id)
    if not cohort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cohort not found"
        )
    session.delete(cohort)
    session.commit()
    return {"ok": True}
