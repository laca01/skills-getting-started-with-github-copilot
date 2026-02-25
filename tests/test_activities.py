"""
Tests for the GET /activities endpoint.
"""

import pytest


class TestGetActivities:
    """Test suite for retrieving the list of activities."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
    
    def test_get_activities_returns_correct_structure(self, client):
        """Test that each activity has the required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())
    
    def test_get_activities_contains_known_activity(self, client, sample_activity):
        """Test that a known activity (Chess Club) is in the response."""
        response = client.get("/activities")
        activities = response.json()
        
        assert sample_activity in activities
        chess_club = activities[sample_activity]
        assert "description" in chess_club
        assert "schedule" in chess_club
    
    def test_get_activities_participants_are_list(self, client):
        """Test that participants field is a list of strings."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
    
    def test_get_activities_max_participants_is_positive_integer(self, client):
        """Test that max_participants is a positive integer."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0
    
    def test_get_activities_multiple_calls_same_result(self, client):
        """Test that multiple calls to GET /activities return consistent data."""
        response1 = client.get("/activities")
        response2 = client.get("/activities")
        
        assert response1.json() == response2.json()
