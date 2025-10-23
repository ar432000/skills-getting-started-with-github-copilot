"""
Pytest configuration and shared fixtures
"""

import pytest
import sys
from pathlib import Path

# Add the src directory to the Python path so we can import the app module
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


# Configure pytest
def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )


# Global pytest fixtures can be added here if needed
@pytest.fixture(scope="session")
def test_data_dir():
    """Return the path to test data directory"""
    return Path(__file__).parent / "data"