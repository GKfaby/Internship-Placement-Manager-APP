# filename: db_init.py

import time
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
# We're importing Base from the data models file. This file will be created later.
# Base contains the metadata for all your SQLModel tables.
from src.data_models import Base
from src.database import DATABASE_URL, engine

# This script will wait for the database to be available and then
# create all the tables defined in data_models.py.

# Set up a session factory, which is a class for creating new Session objects.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Returns a new, active database session.
    This is not used in this script but is a common pattern for API routers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def wait_for_postgres(url: str, retries: int = 5, delay: int = 5):
    """
    Waits for the PostgreSQL service to be ready by attempting to connect.
    This function connects as the 'postgres' superuser to check for service availability.
    """
    # Replace the application user and database with the default 'postgres' user and database
    # to test the connection to the server itself, not a specific database.
    postgres_url = url.replace('youruser', 'postgres').replace('yourdbname', 'postgres')
    for i in range(retries):
        try:
            print("Attempting to connect to PostgreSQL...")
            temp_engine = create_engine(postgres_url)
            # Try to connect. If this works, the server is ready.
            with temp_engine.connect():
                print("PostgreSQL connection successful!")
            return True
        except Exception as e:
            print(f"PostgreSQL connection failed. Retrying in {delay} seconds...")
            print(f"Error: {e}")
            time.sleep(delay)
    return False

def create_user_and_database(url: str):
    """
    Connects as the 'postgres' superuser and creates the application user and database.
    """
    # Use the default 'postgres' user and database for this administrative task.
    postgres_url = url.replace('youruser', 'postgres').replace('yourdbname', 'postgres')
    temp_engine = create_engine(postgres_url)
    try:
        with temp_engine.connect() as conn:
            # The 'AUTOCOMMIT' isolation level is necessary for DDL statements like CREATE USER.
            conn.execution_options(isolation_level="AUTOCOMMIT").execute(
                text("CREATE USER youruser WITH PASSWORD 'yourpassword';")
            )
            print("Created user 'youruser'.")
            conn.execution_options(isolation_level="AUTOCOMMIT").execute(
                text("CREATE DATABASE yourdbname OWNER youruser;")
            )
            print("Created database 'yourdbname' owned by 'youruser'.")
    except Exception as e:
        # User or database may already exist. This is expected and fine.
        print(f"Could not create user or database, likely because they already exist. Error: {e}")

if __name__ == "__main__":
    # Wait for the PostgreSQL service to be responsive.
    if not wait_for_postgres(DATABASE_URL):
        print("Failed to connect to the PostgreSQL service after multiple retries. Exiting.")
        sys.exit(1)

    # Create the user and database for our application.
    create_user_and_database(DATABASE_URL)
    
    # Now that the user and database exist, check if our application database has been created.
    if not database_exists(engine.url):
        create_database(engine.url)
        print("Database did not exist, created new one.")
    else:
        print("Database already exists.")
    
    # Create all tables defined in Base. This is the main goal of the script.
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
