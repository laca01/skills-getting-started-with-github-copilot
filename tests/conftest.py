"""
Shared test configuration and fixtures for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Reset activities to initial state before each test.
    This ensures test isolation and prevents test interdependencies.
    """
    # Store original state
    original_state = {
        name: {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": activity["participants"].copy(),
        }
        for name, activity in activities.items()
    }
    
    yield
    
    # Restore original state after test
    for name, activity in activities.items():
        activity["participants"] = original_state[name]["participants"].copy()


@pytest.fixture
def sample_activity():
    """
    Provide a sample activity name for use in tests.
    """
    return "Chess Club"


@pytest.fixture
def sample_email():
    """
    Provide a sample email for use in tests.
    """
    return "test@mergington.edu"


@pytest.fixture
def new_student_email():
    """
    Provide a new student email not already in any activity.
    """
    return "newstudent@mergington.edu"
