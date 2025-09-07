# Objectives:
# This file defines all the API endpoints for managing placements.
# It provides a complete set of RESTful routes for:
# - Creating a new placement and associating it with students.
# - Retrieving a list of all placements.
# - Getting a single placement by its ID.
# - Updating an existing placement's details and student associations.
# - Deleting a placement.
#
# A key feature of this file is handling the many-to-many relationship between Placements and Students
# using the `StudentPlacementLink` model.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

# Import Pydantic schemas for data validation and API response models
from .. import schemas, data_models
# Import the database session dependency
from ..database import get_db

# Initialize a new APIRouter with a tag for grouping these endpoints in the API documentation
router = APIRouter(tags=["Placements"])

@router.post("/", response_model=schemas.PlacementResponse, status_code=status.HTTP_201_CREATED)
def create_placement(
    placement: schemas.PlacementCreate,
    db: Session = Depends(get_db)
):
    """
    Creates a new placement and associates it with a list of students.
    
    This function handles the two-step process of creating the placement itself and
    then creating the necessary `StudentPlacementLink` records for each student.
    """
    # Create the placement data model object from the request body
    db_placement = data_models.Placement(
        title=placement.title,
        description=placement.description,
        start_date=placement.start_date,
        end_date=placement.end_date,
        status=placement.status,
        employer_id=placement.employer_id,
        mentor_id=placement.mentor_id
    )

    try:
        # Step 1: Add and commit the new placement to the database.
        # This is necessary to get its ID, which is a foreign key for the link table.
        db.add(db_placement)
        db.commit()
        db.refresh(db_placement)
        
        # Step 2: Create the many-to-many links for each student ID provided
        for student_id in placement.student_ids:
            # First, verify that the student actually exists. This is crucial for data integrity.
            existing_student = db.get(data_models.Student, student_id)
            if not existing_student:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Student with ID {student_id} not found"
                )

            # Create the link object and add it to the database session
            student_link = data_models.StudentPlacementLink(
                student_id=student_id,
                placement_id=db_placement.id
            )
            db.add(student_link)

        # Commit the new links
        db.commit()
        db.refresh(db_placement) # Refresh again to load the new relationships
        
        # Prepare the response. The `PlacementResponse` schema needs a `student_ids` list,
        # which we can now get from the refreshed `students` relationship.
        student_ids = [s.id for s in db_placement.students]
        # model_dump is used here to get a dictionary of all the placement fields
        response_data = db_placement.model_dump()
        # The `student_ids` list is then manually added to the dictionary
        response_data["student_ids"] = student_ids
        
        return response_data
    except Exception as e:
        # Rollback the entire transaction if any part of the process fails
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the placement: {e}"
        )

@router.get("/", response_model=List[schemas.PlacementResponse])
def get_all_placements(db: Session = Depends(get_db)):
    """
    Retrieves a list of all placements from the database.
    """
    # Execute the query to get all placements
    placements = db.exec(select(data_models.Placement)).all()
    
    # Manually build the list of `PlacementResponse` objects
    response_placements = []
    for placement in placements:
        # Extract the list of student IDs from the `students` relationship
        student_ids = [student.id for student in placement.students]
        response_placements.append(
            schemas.PlacementResponse(
                id=placement.id,
                title=placement.title,
                description=placement.description,
                start_date=placement.start_date,
                end_date=placement.end_date,
                status=placement.status,
                student_ids=student_ids,
                employer_id=placement.employer_id,
                mentor_id=placement.mentor_id
            )
        )
    return response_placements

@router.get("/{placement_id}", response_model=schemas.PlacementResponse)
def get_placement_by_id(placement_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single placement by its unique ID.
    """
    placement = db.get(data_models.Placement, placement_id)
    if not placement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement not found"
        )
    
    # Extract the list of student IDs from the `students` relationship
    student_ids = [student.id for student in placement.students]
    
    # Return the response model with the student IDs included
    return schemas.PlacementResponse(
        id=placement.id,
        title=placement.title,
        description=placement.description,
        start_date=placement.start_date,
        end_date=placement.end_date,
        status=placement.status,
        student_ids=student_ids,
        employer_id=placement.employer_id,
        mentor_id=placement.mentor_id
    )

@router.patch("/{placement_id}", response_model=schemas.PlacementResponse)
def update_placement(
    placement_id: int,
    placement_update: schemas.PlacementUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates an existing placement by its ID.
    This also handles updating the many-to-many relationship with students.
    """
    placement = db.get(data_models.Placement, placement_id)
    if not placement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement not found"
        )
    
    # Handle the many-to-many relationship separately
    if placement_update.student_ids is not None:
        # Get all existing links for this placement and delete them
        existing_links = db.exec(
            select(data_models.StudentPlacementLink).where(
                data_models.StudentPlacementLink.placement_id == placement_id
            )
        ).all()
        for link in existing_links:
            db.delete(link)
        
        # Create a new link for each student ID in the updated list
        for student_id in placement_update.student_ids:
            new_link = data_models.StudentPlacementLink(
                student_id=student_id,
                placement_id=placement_id
            )
            db.add(new_link)

    # Now, update the other fields of the placement
    placement_data = placement_update.model_dump(exclude_unset=True)
    # Remove `student_ids` from the dictionary so it doesn't get set directly on the `Placement` model
    placement_data.pop("student_ids", None)
    for key, value in placement_data.items():
        setattr(placement, key, value)
    
    db.add(placement)
    db.commit()
    db.refresh(placement)
    
    # Manually prepare the response model
    student_ids = [s.id for s in placement.students]
    response_data = placement.model_dump()
    response_data["student_ids"] = student_ids

    return response_data

@router.delete("/{placement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_placement(placement_id: int, db: Session = Depends(get_db)):
    """
    Deletes a placement by its ID.
    """
    placement = db.get(data_models.Placement, placement_id)
    if not placement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement not found"
        )
    
    # Crucially, delete the associated student links first to avoid foreign key errors
    existing_links = db.exec(
        select(data_models.StudentPlacementLink).where(
            data_models.StudentPlacementLink.placement_id == placement_id
        )
    ).all()
    for link in existing_links:
        db.delete(link)

    db.delete(placement)
    db.commit()
    return {"message": "Placement deleted"}
