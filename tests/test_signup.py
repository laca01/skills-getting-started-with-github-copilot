"""
Tests for the POST /activities/{activity_name}/signup endpoint.
"""

import pytest


class TestSignupForActivity:
    """Test suite for signing up a student for an activity."""
    
    def test_signup_success(self, client, sample_activity, new_student_email):
        """Test successful signup of a new student."""
        response = client.post(
            f"/activities/{sample_activity}/signup?email={new_student_email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_student_email in data["message"]
        assert sample_activity in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, sample_activity, new_student_email):
        """Test that signup actually adds the participant to the activity."""
        # Signup
        client.post(f"/activities/{sample_activity}/signup?email={new_student_email}")
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert new_student_email in activities[sample_activity]["participants"]
    
    def test_signup_activity_not_found(self, client, new_student_email):
        """Test signup fails with 404 when activity doesn't exist."""
        response = client.post(
            f"/activities/NonexistentActivity/signup?email={new_student_email}"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_duplicate_registration(self, client, sample_activity):
        """Test signup fails with 400 when student already signed up."""
        # Get an existing participant
        response = client.get("/activities")
        activities = response.json()
        existing_participant = activities[sample_activity]["participants"][0]
        
        # Try to signup again
        response = client.post(
            f"/activities/{sample_activity}/signup?email={existing_participant}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already" in data["detail"].lower() or "signed up" in data["detail"].lower()
    
    def test_signup_with_valid_email_formats(self, client, sample_activity):
        """Test signup with various valid email formats."""
        test_emails = [
            "student@mergington.edu",
            "john.doe@mergington.edu",
            "jane_smith@mergington.edu",
            "user+tag@mergington.edu",
        ]
        
        for email in test_emails:
            response = client.post(
                f"/activities/{sample_activity}/signup?email={email}"
            )
            assert response.status_code == 200
            # Clean up by unregistering
            client.delete(f"/activities/{sample_activity}/unregister?email={email}")
    
    def test_signup_response_contains_message(self, client, sample_activity, new_student_email):
        """Test that signup response contains a success message."""
        response = client.post(
            f"/activities/{sample_activity}/signup?email={new_student_email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0
    
    def test_signup_multiple_students_different_activities(self, client):
        """Test that multiple students can signup for different activities."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Get activities
        activities_resp = client.get("/activities")
        activities = activities_resp.json()
        activity_names = list(activities.keys())
        
        if len(activity_names) >= 2:
            # Signup for different activities
            response1 = client.post(f"/activities/{activity_names[0]}/signup?email={email1}")
            response2 = client.post(f"/activities/{activity_names[1]}/signup?email={email2}")
            
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            # Verify both signups were recorded
            verify_resp = client.get("/activities")
            verify_activities = verify_resp.json()
            assert email1 in verify_activities[activity_names[0]]["participants"]
            assert email2 in verify_activities[activity_names[1]]["participants"]
