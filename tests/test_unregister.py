"""
Tests for the DELETE /activities/{activity_name}/unregister endpoint.
"""

import pytest


class TestUnregisterFromActivity:
    """Test suite for unregistering a student from an activity."""
    
    def test_unregister_success(self, client, sample_activity, new_student_email):
        """Test successful unregistration of a student."""
        # First signup
        client.post(f"/activities/{sample_activity}/signup?email={new_student_email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/{sample_activity}/unregister?email={new_student_email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_student_email in data["message"]
    
    def test_unregister_removes_participant(self, client, sample_activity, new_student_email):
        """Test that unregister actually removes the participant."""
        # Signup
        client.post(f"/activities/{sample_activity}/signup?email={new_student_email}")
        
        # Verify signup worked
        response = client.get("/activities")
        activities = response.json()
        assert new_student_email in activities[sample_activity]["participants"]
        
        # Unregister
        client.delete(f"/activities/{sample_activity}/unregister?email={new_student_email}")
        
        # Verify removal
        response = client.get("/activities")
        activities = response.json()
        assert new_student_email not in activities[sample_activity]["participants"]
    
    def test_unregister_activity_not_found(self, client, new_student_email):
        """Test unregister fails with 404 when activity doesn't exist."""
        response = client.delete(
            f"/activities/NonexistentActivity/unregister?email={new_student_email}"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_student_not_registered(self, client, sample_activity, new_student_email):
        """Test unregister fails with 400 when student is not registered."""
        response = client.delete(
            f"/activities/{sample_activity}/unregister?email={new_student_email}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert ("not registered" in data["detail"].lower() or 
                "not found" in data["detail"].lower())
    
    def test_unregister_cannot_unregister_twice(self, client, sample_activity, new_student_email):
        """Test that unregistering twice fails the second time."""
        # Signup and then unregister
        client.post(f"/activities/{sample_activity}/signup?email={new_student_email}")
        response1 = client.delete(
            f"/activities/{sample_activity}/unregister?email={new_student_email}"
        )
        assert response1.status_code == 200
        
        # Try to unregister again
        response2 = client.delete(
            f"/activities/{sample_activity}/unregister?email={new_student_email}"
        )
        assert response2.status_code == 400
    
    def test_unregister_response_contains_message(self, client, sample_activity, new_student_email):
        """Test that unregister response contains a success message."""
        # Signup first
        client.post(f"/activities/{sample_activity}/signup?email={new_student_email}")
        
        response = client.delete(
            f"/activities/{sample_activity}/unregister?email={new_student_email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0
    
    def test_unregister_one_student_doesnt_affect_others(self, client, sample_activity):
        """Test that unregistering one student doesn't affect others."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Signup both
        client.post(f"/activities/{sample_activity}/signup?email={email1}")
        client.post(f"/activities/{sample_activity}/signup?email={email2}")
        
        # Unregister first student
        client.delete(f"/activities/{sample_activity}/unregister?email={email1}")
        
        # Verify only second student remains
        response = client.get("/activities")
        activities = response.json()
        assert email1 not in activities[sample_activity]["participants"]
        assert email2 in activities[sample_activity]["participants"]
    
    def test_unregister_from_activity_with_multiple_participants(self, client):
        """Test unregistering from an activity that already has participants."""
        activities_resp = client.get("/activities")
        activities = activities_resp.json()
        
        # Find an activity with participants
        activity_with_participants = None
        for name, activity in activities.items():
            if activity["participants"]:
                activity_with_participants = name
                original_count = len(activity["participants"])
                break
        
        if activity_with_participants:
            existing_participant = activities[activity_with_participants]["participants"][0]
            
            # Unregister existing participant
            response = client.delete(
                f"/activities/{activity_with_participants}/unregister?email={existing_participant}"
            )
            
            assert response.status_code == 200
            
            # Verify count decreased
            verify_resp = client.get("/activities")
            verify_activities = verify_resp.json()
            new_count = len(verify_activities[activity_with_participants]["participants"])
            assert new_count == original_count - 1
