# Objectives:
# This file contains API endpoints for generating reports and aggregating data.
# The primary goal is to provide insights by combining data from different tables.
#
# - A GET endpoint is defined to count the number of placements for each employer.
# - This endpoint requires authentication using the `get_current_user` dependency.

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
# Import the database session dependency
from ..database import get_db
# Import data models for querying
from ..data_models import Employer, Placement
# Import the Pydantic schema for the report's response
from ..schemas import PlacementsPerEmployer
# Import the authentication dependency
from ..auth import get_current_user

# Initialize a new APIRouter with a prefix and tags for documentation
router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)

@router.get("/placements_per_employer", response_model=List[PlacementsPerEmployer])
def get_placements_per_employer(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """
    Retrieves the number of placements for each employer.
    
    This query uses a database `JOIN` to connect `Employers` and `Placements`,
    then uses `GROUP BY` and a `func.count` aggregation to get the total placements
    for each employer.
    """
    # Use SQLModel's select to build the query.
    # `func.count(Placement.id)` counts the number of placements.
    # `.label("placement_count")` gives the counted column a name for the response model.
    statement = select(
        Employer.company_name,
        func.count(Placement.id).label("placement_count")
    ).join(Placement).group_by(Employer.company_name)
    
    # Execute the statement to get the results as a list of tuples
    results = db.exec(statement).all()
    
    if not results:
        # Raise an HTTPException if no results are found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No placements found to generate report."
        )
    
    # Convert the list of tuples into the Pydantic `PlacementsPerEmployer` schema
    return [
        PlacementsPerEmployer(company_name=company, placement_count=count)
        for company, count in results
    ]
