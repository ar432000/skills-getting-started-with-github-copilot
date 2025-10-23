# Test Configuration

This directory contains comprehensive tests for the Mergington High School Activities API.

## Test Structure

### test_api.py
Complete integration tests for the FastAPI endpoints:
- **TestRootEndpoint**: Tests for the root redirect endpoint
- **TestActivitiesEndpoint**: Tests for getting all activities
- **TestSignupEndpoint**: Tests for signing up students to activities
- **TestRemoveParticipantEndpoint**: Tests for removing participants from activities
- **TestEndToEndWorkflow**: End-to-end workflow tests
- **TestURLEncoding**: Tests for proper URL encoding handling
- **TestDataIntegrity**: Tests for data structure integrity

### test_unit.py
Unit tests for individual components and logic:
- **TestActivitiesData**: Tests for the activities data structure
- **TestValidationLogic**: Tests for validation helper functions
- **TestErrorHandling**: Tests for error handling scenarios
- **TestUtilityFunctions**: Tests for utility functions

## Running Tests

### Run all tests:
```bash
pytest tests/
```

### Run tests with verbose output:
```bash
pytest tests/ -v
```

### Run tests with coverage:
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Run specific test file:
```bash
pytest tests/test_api.py
```

### Run specific test class:
```bash
pytest tests/test_api.py::TestSignupEndpoint
```

### Run specific test method:
```bash
pytest tests/test_api.py::TestSignupEndpoint::test_signup_successful
```

## Test Features

- **Fixtures**: Reset activities data between tests to ensure isolation
- **Comprehensive Coverage**: 100% code coverage of the FastAPI application
- **Error Testing**: Tests for all error conditions and edge cases
- **End-to-End Testing**: Complete workflow testing from signup to removal
- **Data Validation**: Tests for data structure integrity and validation
- **URL Encoding**: Tests for proper handling of URLs with special characters

## Test Data

Tests use isolated test data that doesn't affect the main application data:
- Test activities with known participants
- Empty activities for testing first signups
- Various email formats for validation testing