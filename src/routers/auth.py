# Objectives:
# This file defines the API routes specifically for user authentication.
# Its main goal is to provide a single endpoint for users (students, mentors, and employers)
# to log in and obtain a JWT access token. This token will then be used to authenticate
# future requests to protected API endpoints.

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

# Import necessary schemas and data models from our application
from .. import schemas, data_models
# Import database session dependency
from ..database import get_db
# Import password verification and token creation functions from our auth utilities
from ..auth import verify_password, create_access_token

# Initialize a FastAPI router with a tag for grouping related endpoints in the documentation
router = APIRouter(tags=["Authentication"])

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Handles user login by validating credentials and returning a JWT access token.
    This endpoint is designed to be used with standard OAuth2 password flow.

    Args:
        form_data: The username (email) and password submitted by the user.
        db: The database session dependency.

    Returns:
        A dictionary containing the access token and token type on successful login.

    Raises:
        HTTPException: If the username or password is incorrect.
    """
    # Attempt to find the user in the database by their email across multiple tables
    # First, check for a Student
    user = db.exec(
        select(data_models.Student).where(data_models.Student.email == form_data.username)
    ).first()

    # If not a student, check for a Mentor
    if not user:
        user = db.exec(
            select(data_models.Mentor).where(data_models.Mentor.email == form_data.username)
        ).first()

    # If not a mentor, check for an Employer
    if not user:
        user = db.exec(
            select(data_models.Employer).where(data_models.Employer.email == form_data.username)
        ).first()

    # If no user is found or the password doesn't match the stored hash, raise an authentication error
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # If authentication is successful, create a new JWT access token
    # The 'sub' (subject) of the token is the user's email
    access_token = create_access_token(data={"sub": user.email})
    
    # Return the token to the client
    return {"access_token": access_token, "token_type": "bearer"}
