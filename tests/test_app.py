# tests/test_app.py
import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities data after each test to ensure test isolation."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities(client):
    """Test GET /activities returns all activities."""
    # Arrange - No special setup needed
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # We have 9 activities
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]


def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate(client):
    """Test signup fails when student is already signed up."""
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})  # First signup
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]


def test_signup_activity_not_found(client):
    """Test signup fails for non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    invalid_activity = "Nonexistent Activity"
    
    # Act
    response = client.post(f"/activities/{invalid_activity}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_delete_success(client):
    """Test successful unregistration from an activity."""
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})  # Sign up first
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    assert email not in activities[activity_name]["participants"]


def test_delete_not_signed_up(client):
    """Test delete fails when student is not signed up."""
    # Arrange
    email = "notsigned@mergington.edu"
    activity_name = "Chess Club"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]


def test_delete_activity_not_found(client):
    """Test delete fails for non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    invalid_activity = "Nonexistent Activity"
    
    # Act
    response = client.delete(f"/activities/{invalid_activity}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_root_redirect(client):
    """Test root path redirects to static index."""
    # Arrange - No special setup needed
    
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 200  # Follows redirect to static file
    
