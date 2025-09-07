# Objectives:
# This file defines all API endpoints for managing evaluations.
# It provides a complete set of RESTful routes for:
# - Creating a new evaluation with validation to ensure only one type of evaluator is specified.
# - Retrieving a list of all evaluations.
# - Fetching a single evaluation by its ID.
# - Updating an existing evaluation.
# - Deleting an evaluation.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

# Import our Pydantic schemas for data validation and response models
from .. import schemas, data_models
# Import the database session dependency
from ..database import get_db

# Initialize a new APIRouter with a tag for grouping these endpoints in the API documentation
router = APIRouter(tags=["Evaluations"])

@router.post("/", response_model=schemas.EvaluationResponse, status_code=status.HTTP_201_CREATED)
def create_evaluation(
    evaluation: schemas.EvaluationCreate,
    db: Session = Depends(get_db)
):
    """
    Creates a new evaluation in the database.
    
    This function includes a critical validation step to ensure that only one of the
    three evaluator types (mentor, employer, or student) is provided in the request.
    If none or more than one are provided, it raises an HTTP error.
    """
    # Create a list of tuples containing the evaluator ID name and its value
    evaluator_ids = [
        ("mentor_evaluator_id", evaluation.mentor_evaluator_id),
        ("employer_evaluator_id", evaluation.employer_evaluator_id),
        ("student_evaluator_id", evaluation.student_evaluator_id)
    ]
    
    # Filter the list to find which evaluator IDs were actually provided (are not None)
    provided_evaluators = [name for name, id_val in evaluator_ids if id_val is not None]

    # Raise an error if no evaluator ID was provided
    if not provided_evaluators:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one evaluator ID must be provided."
        )
    # Raise an error if more than one evaluator ID was provided
    if len(provided_evaluators) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only one type of evaluator can be provided at a time."
        )

    # Create the `Evaluation` data model instance from the validated input
    db_evaluation = data_models.Evaluation(
        feedback=evaluation.feedback,
        rating=evaluation.rating,
        placement_id=evaluation.placement_id,
        subject_id=evaluation.subject_id,
        mentor_evaluator_id=evaluation.mentor_evaluator_id,
        employer_evaluator_id=evaluation.employer_evaluator_id,
        student_evaluator_id=evaluation.student_evaluator_id
    )

    # Use a try-except block to handle potential database errors during the creation process
    try:
        db.add(db_evaluation)
        db.commit()
        db.refresh(db_evaluation)
        return db_evaluation
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the evaluation: {e}"
        )

@router.get("/", response_model=List[schemas.EvaluationResponse])
def get_all_evaluations(db: Session = Depends(get_db)):
    """
    Retrieves a list of all evaluations from the database.
    """
    evaluations = db.exec(select(data_models.Evaluation)).all()
    return evaluations

@router.get("/{evaluation_id}", response_model=schemas.EvaluationResponse)
def get_evaluation_by_id(evaluation_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single evaluation by its unique ID.
    """
    evaluation = db.get(data_models.Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    return evaluation

@router.patch("/{evaluation_id}", response_model=schemas.EvaluationResponse)
def update_evaluation(
    evaluation_id: int,
    evaluation_update: schemas.EvaluationUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates an existing evaluation.
    This is a PATCH endpoint, so it only updates the fields provided in the request body.
    """
    evaluation = db.get(data_models.Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    
    # Get the data from the Pydantic update model, excluding any unset fields
    evaluation_data = evaluation_update.model_dump(exclude_unset=True)
    # Loop through the update data and apply it to the database object
    for key, value in evaluation_data.items():
        setattr(evaluation, key, value)
    
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation

@router.delete("/{evaluation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    """
    Deletes an evaluation by its ID.
    """
    evaluation = db.get(data_models.Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    
    db.delete(evaluation)
    db.commit()
    return None
