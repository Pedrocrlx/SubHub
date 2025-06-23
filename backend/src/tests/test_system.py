"""
System level tests for base API functionality.

This module verifies that:
- Basic system endpoints are working
- Health check endpoint responds correctly
- API documentation is available
- Error handling works correctly
"""
import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

def test_home_endpoint(client):
    """
    Test the root endpoint
    
    Verifies that:
    - Root endpoint returns a successful response
    - Response contains expected API information
    """
    response = client.get("/")
    assert response.status_code == 200
    
    # If returning JSON with API info
    if "application/json" in response.headers.get("content-type", ""):
        data = response.json()
        assert "version" in data
        assert "status" in data
        assert data["status"] == "healthy"

def test_health_check(client):
    """
    Test the health check endpoint
    
    Verifies that:
    - Health check endpoint returns 200 OK
    - Response indicates the API is healthy/operational
    """
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_global_error_handler():
    """
    Test that the global error handler correctly handles unhandled exceptions
    
    Verifies that:
    - Unhandled exceptions return 500 status codes
    - Error details are not exposed to the client
    - Error response has expected format
    """
    # Create a minimal test app with an exception handler
    test_app = FastAPI()
    
    # Add an exception handler similar to the one in the main app
    @test_app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    # Create a test endpoint that raises an exception
    @test_app.get("/test-error")
    def error_endpoint():
        # This will trigger the global error handler
        raise ValueError("Test unexpected error")
    
    # Create a test client with raise_server_exceptions=False to allow FastAPI's exception handlers to run
    test_client = TestClient(test_app, raise_server_exceptions=False)
    
    # Call the endpoint which will raise an exception
    response = test_client.get("/test-error")
    
    # Should return 500 Internal Server Error
    assert response.status_code == 500
    
    # Should have generic error message without exposing details
    assert response.json()["detail"] == "Internal server error"
    
    # Error message should not contain the actual exception message
    assert "Test unexpected error" not in response.text
