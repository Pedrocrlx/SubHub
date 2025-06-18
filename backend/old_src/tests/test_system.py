"""
Tests for system-level API functionality.
"""
import pytest
from .conftest import client, settings

def test_home_endpoint():
    """
    Test the API root endpoint
    
    Verifies that:
    - The root endpoint returns 200 status code
    - The app name and version are correct
    - The status indicates the service is running
    """
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["app"] == settings.APP_NAME
    assert data["version"] == settings.VERSION
    assert data["status"] == "running"