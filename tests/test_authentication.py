import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate
from app.services.authentication import AuthService

def test_create_user(db):
    # Create service
    service = AuthService()
    
    # Create test user
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        password="Password123!",
        roles=["user"]
    )
    
    # Add the user
    db_user = service.create_user(db, user)
    
    # Check the user was created with the correct values
    assert db_user is not None
    assert db_user.username == "testuser"
    assert db_user.email == "test@example.com"
    assert db_user.full_name == "Test User"
    assert hasattr(db_user, "hashed_password")
    assert db_user.hashed_password != "Password123!"  # Password should be hashed

def test_authenticate_user(db):
    # Create service
    service = AuthService()
    
    # Create test user
    user = UserCreate(
        username="authuser",
        email="auth@example.com",
        full_name="Auth User",
        password="Password123!",
        roles=["user"]
    )
    
    # Add the user
    db_user = service.create_user(db, user)
    
    # Test authentication with correct password
    authenticated_user = service.authenticate_user(db, "authuser", "Password123!")
    assert authenticated_user is not None
    assert authenticated_user.id == db_user.id
    
    # Test authentication with incorrect password
    authenticated_user = service.authenticate_user(db, "authuser", "WrongPassword!")
    assert authenticated_user is None
    
    # Test authentication with non-existent user
    authenticated_user = service.authenticate_user(db, "nonexistentuser", "Password123!")
    assert authenticated_user is None