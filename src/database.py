# Objective: This file manages the database connection and ensures all necessary tables exist.
# It's set up to work for both a testing environment and the main production database.

import time
from typing import Generator
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.engine import URL
from decouple import config

# Check if the application is running in a testing environment.
# This setting is defined in your .env file.
TESTING = config('TESTING', default=False, cast=bool)

# Define the database connection engine based on the environment.
if TESTING:
    # For testing, a simple, in-memory SQLite database.
    # This is fast and doesn't require a separate database server.
    sqlite_file_name = "test.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    # The 'echo=True' flag will print all SQL statements to the console, which is
    # useful for debugging in development.
    engine = create_engine(sqlite_url, echo=True)
else:
    # For the live application, the PostgreSQL database.
    # The `host='db'` is important for Docker, as it connects to the database service.
    engine = create_engine(URL.create(
        drivername="postgresql+psycopg2",
        username=config('POSTGRES_USER'),
        password=config('POSTGRES_PASSWORD'),
        host=config('POSTGRES_HOST', default='db'),
        port=config('POSTGRES_PORT', default=5432, cast=int),
        database=config('POSTGRES_DB')
    ), echo=True)

def create_db_and_tables():
    """
    Connects to the database and creates all tables based on the data models.
    Includes a retry mechanism to handle cases where the database might not be ready yet,
    which is common in containerized environments like Docker.
    """
    if TESTING:
        # skipping the retry logic for the test database since it's in-memory.
        print("Skipping database connection for testing environment.")
        SQLModel.metadata.create_all(engine)
        print("Tables created for in-memory SQLite.")
        return

    # For the live application, connect a few times.
    retries = 10
    while retries > 0:
        try:
            # Try to establish a connection. If it works, we can proceed.
            with engine.connect() as connection:
                print("Database connection successful!")
                break
        except Exception as e:
            # If the connection fails, wait and try again.
            print(f"Attempt {11 - retries}/10: Could not connect to database. Retrying in 5 seconds...")
            print(f"Error: {e}")
            retries -= 1
            time.sleep(5)
    else:
        # If all retries fail, something is wrong, and we raise an error.
        raise Exception("Failed to connect to the database after multiple retries.")
    
    # Now that we're connected, we can create the tables.
    print("Creating tables...")
    # This command uses the metadata from all the SQLModel classes to create the tables.
    SQLModel.metadata.create_all(engine)
    print("Tables created.")

def get_db() -> Generator[Session, None, None]:
    """
    Returns a new, active database session for an API request.
    This function is designed to be used as a dependency in FastAPI route functions.
    It automatically handles closing the session after the request is complete.
    """
    with Session(engine) as session:
        yield session
