import sys
import os
import getpass

# Add the parent directory to the path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.services.authentication import AuthService
from app.schemas.user import UserCreate

def create_admin_user():
    print("Creating admin user...")
    
    # Get user input
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    full_name = input("Enter admin full name: ")
    password = getpass.getpass("Enter admin password: ")
    confirm_password = getpass.getpass("Confirm admin password: ")
    
    # Validate password
    if password != confirm_password:
        print("Passwords do not match!")
        return
    
    # Create user object
    user = UserCreate(
        username=username,
        email=email,
        full_name=full_name,
        password=password,
        roles=["admin"]
    )
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create user
        auth_service = AuthService()
        user = auth_service.create_user(db, user)
        
        if user:
            print(f"Admin user '{username}' created successfully.")
        else:
            print("Failed to create admin user. Username or email may already be in use.")
    
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()