import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from typing import Generator
import os
import tempfile
import uuid

from src.auth import create_access_token
from src.main import app
from src.data_models import Student, Mentor, Employer, Placement, Evaluation, StudentPlacementLink, MentorStudentLink

# --- Test Data ---
STUDENT_DATA_1 = {
    "full_name": "Naruto Uzumaki",
    "email": "", 
    "major": "Ninjutsu",
    "password": "rasengan"
}

MENTOR_DATA_1 = {
    "full_name": "Kakashi Hatake",
    "email": "",
    "field": "Ninjutsu Division",
    "is_admin": False, # <-- ADDED THIS FIELD
    "password": "sharingan"
}

EMPLOYER_DATA_1 = {
    "company_name": "Capsule Corp",
    "email": "",
    "contact_person": "Bulma",
    "industry": "Technology",
    "password": "goku"
}

@pytest.fixture(name="db_engine_and_file", scope="session")
def db_engine_and_file_fixture() -> Generator[tuple[any, str], None, None]:
    """
    Creates and yields a SQLAlchemy engine and the path to a temporary database file.
    The file is cleaned up after the session ends.
    """
    # Create a temporary file to use as our database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db_path = tmp.name
    
    sqlite_url = f"sqlite:///{temp_db_path}"
    # Use check_same_thread=False for SQLite in testing
    engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})
    
    SQLModel.metadata.create_all(engine)
    
    yield engine, temp_db_path
    
    # Teardown: close the engine and remove the temporary file
    engine.dispose()
    os.remove(temp_db_path)

@pytest.fixture(name="client", scope="session")
def client_fixture(db_engine_and_file: tuple[any, str]) -> Generator[TestClient, None, None]:
    """Provides a test client with a mocked database dependency."""
    engine, _ = db_engine_and_file
    
    def get_session_override():
        with Session(engine) as session:
            yield session
    
    app.dependency_overrides["get_db"] = get_session_override
    
    with TestClient(app) as client:
        yield client
        
    app.dependency_overrides.clear()
    
@pytest.fixture(name="auth_headers_and_ids", scope="function")
def auth_headers_and_ids_fixture(client: TestClient):
    """
    Fixture to create test accounts and return their IDs and auth headers.
    This fixture is scoped to the 'function', meaning it runs for each test.
    """
    # Create test student with a unique email
    unique_student_email = f"naruto+{uuid.uuid4()}@konoha.com"
    student_data = STUDENT_DATA_1.copy()
    student_data["email"] = unique_student_email
    
    response_student = client.post("/api/v1/students/", json=student_data)
    assert response_student.status_code == 201
    student_id = response_student.json()["id"]
    student_token = create_access_token(data={"sub": unique_student_email})
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    # Create test mentor with a unique email
    unique_mentor_email = f"kakashi+{uuid.uuid4()}@konoha.com"
    mentor_data = MENTOR_DATA_1.copy()
    mentor_data["email"] = unique_mentor_email
    
    response_mentor = client.post("/api/v1/mentors/", json=mentor_data)
    assert response_mentor.status_code == 201
    mentor_id = response_mentor.json()["id"]

    # Create test employer with a unique email
    unique_employer_email = f"bulma+{uuid.uuid4()}@capsule.com"
    employer_data = EMPLOYER_DATA_1.copy()
    employer_data["email"] = unique_employer_email

    response_employer = client.post("/api/v1/employers/", json=employer_data)
    assert response_employer.status_code == 201
    employer_id = response_employer.json()["id"]

    return {
        "student_id": student_id,
        "student_headers": student_headers,
        "mentor_id": mentor_id,
        "employer_id": employer_id
    }
