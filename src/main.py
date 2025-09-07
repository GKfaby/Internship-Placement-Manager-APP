# Objective: This file is the main entry point for the FastAPI application.
# It sets up the app, defines its metadata, connects to the database,
# and includes all the different API routers.

from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv

# Load environment variables from the .env file.
# This ensures that sensitive information like database credentials are not
# hardcoded directly in your application.
load_dotenv()

# Import the database engine and the function to create tables.
from .database import engine, create_db_and_tables

# Import all the routers, which contain the specific API endpoints for
# each part of your application (e.g., students, mentors, etc.).
from .routers import auth, students, mentors, employers, placements, evaluations

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This function manages the application's startup and shutdown events.
    It's an asynchronous context manager that ensures the database tables
    are created before the application begins serving requests.
    """
    print("Application startup...")
    # This call creates all the database tables defined in your models.
    # It will only run once when the application first starts.
    create_db_and_tables()
    yield
    # Any code after 'yield' will be executed on application shutdown.
    print("Application shutdown.")

# Create the main FastAPI application instance.
# We're providing a title, description, and version for the auto-generated
# API documentation (available at /docs).
app = FastAPI(
    title="Internship Placement Manager API",
    description="API for managing student internships, mentors, and employers.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def read_root():
    """
    This is a simple root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the Internship Placement Manager API. Visit /docs for API documentation."}

# Include all the routers into the main application.
# The 'prefix' adds a base path to all endpoints in that router (e.g., /api/v1/students).
# The 'tags' are used to group related endpoints in the API documentation.
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(students.router, prefix="/api/v1/students", tags=["Students"])
app.include_router(mentors.router, prefix="/api/v1/mentors", tags=["Mentors"])
app.include_router(employers.router, prefix="/api/v1/employers", tags=["Employers"])
app.include_router(placements.router, prefix="/api/v1/placements", tags=["Placements"])
app.include_router(evaluations.router, prefix="/api/v1/evaluations", tags=["Evaluations"])

# This block allows you to run the application directly from this file using Uvicorn.
# It's useful for local development and testing.
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
