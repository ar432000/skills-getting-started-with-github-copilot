"""
Unit tests for individual functions and components
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from src.app import activities


class TestActivitiesData:
    """Tests for the activities data structure"""
    
    def test_activities_data_structure(self):
        """Test that activities data has the expected structure"""
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            
            required_fields = ["description", "schedule", "max_participants", "participants"]
            for field in required_fields:
                assert field in activity_data, f"Missing field {field} in {activity_name}"
            
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            assert activity_data["max_participants"] > 0
            assert len(activity_data["participants"]) <= activity_data["max_participants"]
    
    def test_all_activities_have_valid_emails(self):
        """Test that all participant emails follow a basic email format"""
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        for activity_name, activity_data in activities.items():
            for email in activity_data["participants"]:
                assert email_pattern.match(email), f"Invalid email {email} in {activity_name}"
    
    def test_no_duplicate_participants_in_activities(self):
        """Test that there are no duplicate participants within each activity"""
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            assert len(participants) == len(set(participants)), f"Duplicate participants in {activity_name}"


class TestValidationLogic:
    """Tests for validation logic that would be in helper functions"""
    
    def test_email_validation_logic(self):
        """Test email validation logic"""
        import re
        
        def is_valid_email(email):
            pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            return bool(pattern.match(email))
        
        # Valid emails
        valid_emails = [
            "student@mergington.edu",
            "test.email@domain.com",
            "user+tag@example.org",
            "user123@test-domain.co.uk"
        ]
        
        for email in valid_emails:
            assert is_valid_email(email), f"Should be valid: {email}"
        
        # Invalid emails
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            "user space@domain.com",
            ""
        ]
        
        for email in invalid_emails:
            assert not is_valid_email(email), f"Should be invalid: {email}"
    
    def test_activity_capacity_logic(self):
        """Test activity capacity checking logic"""
        
        def can_add_participant(activity_data):
            return len(activity_data["participants"]) < activity_data["max_participants"]
        
        def get_spots_remaining(activity_data):
            return activity_data["max_participants"] - len(activity_data["participants"])
        
        # Test with sample data
        test_activity = {
            "max_participants": 5,
            "participants": ["user1@test.com", "user2@test.com"]
        }
        
        assert can_add_participant(test_activity)
        assert get_spots_remaining(test_activity) == 3
        
        # Test when full
        full_activity = {
            "max_participants": 2,
            "participants": ["user1@test.com", "user2@test.com"]
        }
        
        assert not can_add_participant(full_activity)
        assert get_spots_remaining(full_activity) == 0


@pytest.mark.unit
class TestErrorHandling:
    """Tests for error handling scenarios"""
    
    def test_http_exception_details(self):
        """Test that HTTPExceptions have proper details"""
        
        # Test 404 exception
        with pytest.raises(HTTPException) as exc_info:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Activity not found"
        
        # Test 400 exception
        with pytest.raises(HTTPException) as exc_info:
            raise HTTPException(status_code=400, detail="Student already signed up for this activity")
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Student already signed up for this activity"


class TestUtilityFunctions:
    """Tests for utility functions (if any exist or should exist)"""
    
    def test_url_encoding_handling(self):
        """Test URL encoding/decoding logic"""
        from urllib.parse import quote, unquote
        
        # Test activity names with spaces
        activity_name = "Chess Club"
        encoded = quote(activity_name)
        assert encoded == "Chess%20Club"
        assert unquote(encoded) == activity_name
        
        # Test emails with special characters
        email = "test+alias@domain.com"
        encoded_email = quote(email)
        assert unquote(encoded_email) == email
    
    def test_data_consistency_checks(self):
        """Test data consistency validation"""
        
        def validate_activity_data(activity_data):
            """Validate that activity data is consistent"""
            if not isinstance(activity_data, dict):
                return False
            
            required_fields = ["description", "schedule", "max_participants", "participants"]
            if not all(field in activity_data for field in required_fields):
                return False
            
            if activity_data["max_participants"] <= 0:
                return False
            
            if len(activity_data["participants"]) > activity_data["max_participants"]:
                return False
            
            return True
        
        # Valid data
        valid_data = {
            "description": "Test activity",
            "schedule": "Test schedule",
            "max_participants": 10,
            "participants": ["test@example.com"]
        }
        assert validate_activity_data(valid_data)
        
        # Invalid data - missing field
        invalid_data = {
            "description": "Test activity",
            "schedule": "Test schedule",
            "participants": ["test@example.com"]
        }
        assert not validate_activity_data(invalid_data)
        
        # Invalid data - too many participants
        overfull_data = {
            "description": "Test activity",
            "schedule": "Test schedule",
            "max_participants": 1,
            "participants": ["test1@example.com", "test2@example.com"]
        }
        assert not validate_activity_data(overfull_data)