import pytest
from fastapi.testclient import TestClient

# --- Test Functions ---
# NOTE: The fixtures (client, auth_headers_and_ids) are now defined in conftest.py
# and are automatically discovered by pytest.

def test_root(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Internship Placement Manager API. Visit /docs for API documentation."}

def test_students_crud(client: TestClient):
    """Tests the POST, GET, PATCH, and DELETE functions for the students endpoint."""
    # Using unique data for this test to avoid conflicts.
    STUDENT_DATA_2 = {
        "full_name": "Jane Smith",
        "email": "jane.smith@example.com",
        "major": "Physics",
        "password": "testpassword"
    }

    # POST to create a new student
    response = client.post("/api/v1/students/", json=STUDENT_DATA_2)
    assert response.status_code == 201
    student_id = response.json()["id"]

    # GET student by ID
    response = client.get(f"/api/v1/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["full_name"] == "Jane Smith"

    # PATCH to update student
    update_data = {"major": "Astrophysics"}
    response = client.patch(f"/api/v1/students/{student_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["major"] == "Astrophysics"

    # DELETE student
    response = client.delete(f"/api/v1/students/{student_id}")
    assert response.status_code == 204

def test_mentors_crud(client: TestClient):
    """Tests the POST, GET, PATCH, and DELETE functions for the mentors endpoint."""
    # Using unique data for this test to avoid conflicts.
    MENTOR_DATA_2 = {
        "full_name": "Gai Sensei",
        "email": "gai@konoha.com",
        "field": "Taijutsu Division",
        "password": "thepowerofyouth"
    }
    # POST to create a new mentor
    response = client.post("/api/v1/mentors/", json=MENTOR_DATA_2)
    assert response.status_code == 201
    mentor_id = response.json()["id"]
    
    # GET mentor by ID
    response = client.get(f"/api/v1/mentors/{mentor_id}")
    assert response.status_code == 200
    assert response.json()["full_name"] == "Gai Sensei"

    # PATCH to update mentor
    update_data = {"field": "Hidden Leaf Village Jounin"}
    response = client.patch(f"/api/v1/mentors/{mentor_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["field"] == "Hidden Leaf Village Jounin"

    # DELETE mentor
    response = client.delete(f"/api/v1/mentors/{mentor_id}")
    assert response.status_code == 204

def test_employers_crud(client: TestClient):
    """Tests the POST, GET, PATCH, and DELETE functions for the employers endpoint."""
    # Using unique data for this test to avoid conflicts.
    EMPLOYER_DATA_2 = {
        "company_name": "Stark Industries",
        "email": "pepper.potts@starkindustries.com",
        "contact_person": "Pepper Potts",
        "industry": "Technology",
        "password": "ironman"
    }
    # POST to create a new employer
    response = client.post("/api/v1/employers/", json=EMPLOYER_DATA_2)
    assert response.status_code == 201
    employer_id = response.json()["id"]
    
    # GET employer by ID
    response = client.get(f"/api/v1/employers/{employer_id}")
    assert response.status_code == 200
    assert response.json()["company_name"] == "Stark Industries"

    # PATCH to update employer
    update_data = {"contact_person": "Tony Stark"}
    response = client.patch(f"/api/v1/employers/{employer_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["contact_person"] == "Tony Stark"

    # DELETE employer
    response = client.delete(f"/api/v1/employers/{employer_id}")
    assert response.status_code == 204

def test_placement_and_evaluation_crud(client: TestClient, auth_headers_and_ids: dict):
    """
    Test the CRUD operations for placements and evaluations using the fixture.
    """
    student_id = auth_headers_and_ids["student_id"]
    mentor_id = auth_headers_and_ids["mentor_id"]
    employer_id = auth_headers_and_ids["employer_id"]
    
    # POST placement
    placement_payload = {
        "title": "Summer Internship",
        "description": "A great learning experience.",
        "start_date": "2024-06-01",
        "end_date": "2024-08-31",
        "status": "active",
        "employer_id": employer_id,
        "mentor_id": mentor_id,
        "student_ids": [student_id]
    }
    response = client.post("/api/v1/placements/", json=placement_payload)
    assert response.status_code == 201
    placement_id = response.json()["id"]
    
    # POST evaluation
    evaluation_payload = {
        "feedback": "Excellent work.",
        "rating": 5,
        "placement_id": placement_id,
        "subject_id": student_id,
        "mentor_evaluator_id": mentor_id
    }
    response = client.post("/api/v1/evaluations/", json=evaluation_payload)
    assert response.status_code == 201
    evaluation_id = response.json()["id"]

    # GET placement by ID
    response = client.get(f"/api/v1/placements/{placement_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Summer Internship"
    
    # GET evaluation by ID
    response = client.get(f"/api/v1/evaluations/{evaluation_id}")
    assert response.status_code == 200
    assert response.json()["feedback"] == "Excellent work."
    
    # PATCH placement
    update_payload = {"status": "Completed"}
    response = client.patch(f"/api/v1/placements/{placement_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "Completed"
    
    # PATCH evaluation
    update_payload = {"rating": 4}
    response = client.patch(f"/api/v1/evaluations/{evaluation_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["rating"] == 4
    
    # DELETE evaluation
    response = client.delete(f"/api/v1/evaluations/{evaluation_id}")
    assert response.status_code == 204
    
    # DELETE placement
    response = client.delete(f"/api/v1/placements/{placement_id}")
    assert response.status_code == 204
