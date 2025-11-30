from fastapi.testclient import TestClient
import copy
import pytest

from src import app as application_module

client = TestClient(application_module.app)
activities = application_module.activities


@pytest.fixture(autouse=True)
def reset_activities():
    # snapshot the in-memory activities and restore after each test
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow():
    email = "pytest_user@example.com"

    # Sign up
    r = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert r.status_code == 200
    assert email in activities["Chess Club"]["participants"]

    # Duplicate signup should return 400
    r2 = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert r2.status_code == 400

    # Unregister
    r3 = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert r3.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_nonexistent_activity_or_user():
    # Non-existent activity
    r = client.delete("/activities/NoSuchActivity/participants?email=noone@example.com")
    assert r.status_code == 404

    # Existing activity but non-registered user
    r2 = client.delete("/activities/Chess%20Club/participants?email=not_registered@example.com")
    assert r2.status_code == 404
