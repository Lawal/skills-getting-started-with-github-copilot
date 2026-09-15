from fastapi.testclient import TestClient

from app import app, activities


client = TestClient(app)


def reset_activity_state():
    """Reset the in-memory data store before each test."""
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
    activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]


def test_get_activities_returns_activity_data():
    # Arrange
    reset_activity_state()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"]
    assert len(data["Chess Club"]["participants"]) == 2


def test_signup_adds_student_for_activity():
    # Arrange
    reset_activity_state()
    email = "newstudent@mergington.edu"
    if email in activities["Chess Club"]["participants"]:
        activities["Chess Club"]["participants"].remove(email)

    # Act
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_registration():
    # Arrange
    reset_activity_state()
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_unregister_removes_student_from_activity():
    # Arrange
    reset_activity_state()
    email = "daniel@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unknown_activity_returns_404():
    # Arrange
    reset_activity_state()

    # Act
    response = client.post("/activities/Unknown Club/signup?email=test@example.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
