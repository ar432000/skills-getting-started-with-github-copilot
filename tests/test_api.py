"""
Test suite for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import json


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities data before each test"""
    # Store original data
    original_activities = json.loads(json.dumps(activities))
    
    # Reset to known state
    activities.clear()
    activities.update({
        "Test Activity": {
            "description": "A test activity for testing purposes",
            "schedule": "Test schedule",
            "max_participants": 5,
            "participants": ["test1@mergington.edu", "test2@mergington.edu"]
        },
        "Empty Activity": {
            "description": "An activity with no participants",
            "schedule": "Empty schedule",
            "max_participants": 10,
            "participants": []
        }
    })
    
    yield
    
    # Restore original data after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert "Test Activity" in data
        assert "Empty Activity" in data
        assert len(data) == 2
        
        # Check structure of returned activity
        test_activity = data["Test Activity"]
        assert "description" in test_activity
        assert "schedule" in test_activity
        assert "max_participants" in test_activity
        assert "participants" in test_activity
        assert test_activity["max_participants"] == 5
        assert len(test_activity["participants"]) == 2


class TestSignupEndpoint:
    """Tests for the signup functionality"""
    
    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Test%20Activity/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Test Activity" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Test Activity"]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_signed_up(self, client, reset_activities):
        """Test signup when student is already registered"""
        response = client.post(
            "/activities/Test%20Activity/signup?email=test1@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_to_empty_activity(self, client, reset_activities):
        """Test signup to activity with no existing participants"""
        response = client.post(
            "/activities/Empty%20Activity/signup?email=first@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was added to empty activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "first@mergington.edu" in activities_data["Empty Activity"]["participants"]
        assert len(activities_data["Empty Activity"]["participants"]) == 1


class TestRemoveParticipantEndpoint:
    """Tests for removing participants from activities"""
    
    def test_remove_participant_successful(self, client, reset_activities):
        """Test successful removal of a participant"""
        response = client.delete(
            "/activities/Test%20Activity/signup?email=test1@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "test1@mergington.edu" in data["message"]
        assert "Test Activity" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test1@mergington.edu" not in activities_data["Test Activity"]["participants"]
        assert len(activities_data["Test Activity"]["participants"]) == 1
    
    def test_remove_participant_activity_not_found(self, client, reset_activities):
        """Test removal from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_remove_participant_not_signed_up(self, client, reset_activities):
        """Test removal when student is not signed up"""
        response = client.delete(
            "/activities/Test%20Activity/signup?email=notsignedup@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student not signed up for this activity"
    
    def test_remove_from_empty_activity(self, client, reset_activities):
        """Test removal from activity with no participants"""
        response = client.delete(
            "/activities/Empty%20Activity/signup?email=nobody@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student not signed up for this activity"


class TestEndToEndWorkflow:
    """End-to-end tests for complete workflows"""
    
    def test_signup_and_remove_workflow(self, client, reset_activities):
        """Test complete signup and removal workflow"""
        email = "workflow@mergington.edu"
        activity = "Test Activity"
        
        # Initial state check
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup_response = client.get("/activities")
        after_signup_data = after_signup_response.json()
        assert email in after_signup_data[activity]["participants"]
        assert len(after_signup_data[activity]["participants"]) == initial_count + 1
        
        # Remove participant
        remove_response = client.delete(f"/activities/{activity}/signup?email={email}")
        assert remove_response.status_code == 200
        
        # Verify removal
        after_removal_response = client.get("/activities")
        after_removal_data = after_removal_response.json()
        assert email not in after_removal_data[activity]["participants"]
        assert len(after_removal_data[activity]["participants"]) == initial_count
    
    def test_multiple_signups_same_activity(self, client, reset_activities):
        """Test multiple students signing up for the same activity"""
        activity = "Empty Activity"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Sign up multiple students
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all are signed up
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for email in emails:
            assert email in activities_data[activity]["participants"]
        
        assert len(activities_data[activity]["participants"]) == 3


class TestURLEncoding:
    """Tests for proper URL encoding handling"""
    
    def test_activity_name_with_spaces(self, client, reset_activities):
        """Test handling of activity names with spaces"""
        response = client.post(
            "/activities/Test%20Activity/signup?email=space@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_email_with_special_characters(self, client, reset_activities):
        """Test handling of emails with special characters"""
        # Test with + character (common in email aliases)
        email = "test+alias@mergington.edu"
        encoded_email = "test%2Balias@mergington.edu"
        
        response = client.post(
            f"/activities/Test%20Activity/signup?email={encoded_email}"
        )
        assert response.status_code == 200
        
        # Verify participant was added with correct email
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Test Activity"]["participants"]


class TestDataIntegrity:
    """Tests for data integrity and edge cases"""
    
    def test_activities_structure_integrity(self, client, reset_activities):
        """Test that activities maintain proper structure"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        for activity_name, activity_data in data.items():
            # Check required fields
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            
            # Check data types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Check constraints
            assert activity_data["max_participants"] > 0
            assert len(activity_data["participants"]) <= activity_data["max_participants"]