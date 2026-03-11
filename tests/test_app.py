from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_root_redirects_to_static():
    # disable automatic redirect following so we can inspect the response
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 302)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_dict():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # should contain at least one known activity from the seed data
    assert "Chess Club" in data


def test_signup_successful(tmp_path, monkeypatch):
    # make sure the activity has no prior participant to keep test idempotent
    activities["Chess Club"]["participants"] = []
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate():
    # sign up once, then try again
    activities["Chess Club"]["participants"] = ["duplicate@mergington.edu"]
    email = "duplicate@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_nonexistent_activity():
    response = client.post("/activities/NotAnActivity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
