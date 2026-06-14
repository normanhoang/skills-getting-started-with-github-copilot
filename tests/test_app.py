import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self):
        """Test that all activities are returned"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert len(data) > 0
        for activity in expected_activities:
            assert activity in data


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in data["message"]
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        # Arrange
        activity_name = "NonExistentClub"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_student(self):
        """Test that a student cannot sign up twice for the same activity"""
        # Arrange
        activity_name = "Programming Class"
        email = "duplicate.test@mergington.edu"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Act - Attempt duplicate signup
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data2 = response2.json()
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400
        assert "already signed up" in data2["detail"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        # Arrange
        activity_name = "Gym Class"
        email = "tounregister@mergington.edu"
        
        # Act - First signup
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act - Then unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in data["message"]
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_unregister_activity_not_found(self):
        """Test unregister from non-existent activity"""
        # Arrange
        activity_name = "FakeClub"
        email = "test@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert data["detail"] == "Activity not found"
    
    def test_unregister_not_registered_student(self):
        """Test unregister for a student not registered in the activity"""
        # Arrange
        activity_name = "Soccer Team"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in data["detail"]


class TestActivityParticipantCounts:
    """Tests for activity participant data integrity"""
    
    def test_participants_list_structure(self):
        """Test that participant lists have correct structure"""
        # Arrange
        expected_fields = ["participants", "max_participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            for field in expected_fields:
                assert field in activity_data, f"Missing {field} in {activity_name}"
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_signup_increases_participant_count(self):
        """Test that signup increases the participant list"""
        # Arrange
        activity_name = "Art Club"
        email = "artlover@mergington.edu"
        
        # Act - Get initial count
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity_name]["participants"])
        
        # Act - Signup
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act - Get updated count
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity_name]["participants"])
        
        # Assert
        assert count_after == count_before + 1
        assert email in response_after.json()[activity_name]["participants"]
