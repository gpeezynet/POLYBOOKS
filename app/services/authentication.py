from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import os

from app.models.user import User, Role
from app.schemas.user import UserCreate, UserUpdate, TokenData
from app.repositories.user import UserRepository, RoleRepository

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.user_repository = UserRepository(User)
        self.role_repository = RoleRepository()
    
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password):
        return pwd_context.hash(password)
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        user = self.user_repository.get_by_username(db, username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_user(self, db: Session, user_in: UserCreate) -> Optional[User]:
        # Check if user already exists
        db_user = self.user_repository.get_by_username(db, user_in.username)
        if db_user:
            return None
        
        # Check if email already exists
        db_user = self.user_repository.get_by_email(db, user_in.email)
        if db_user:
            return None
        
        # Create user with hashed password
        hashed_password = self.get_password_hash(user_in.password)
        user_data = user_in.dict(exclude={"password", "roles"})
        user_data["hashed_password"] = hashed_password
        
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Add roles if provided
        if user_in.roles:
            for role_name in user_in.roles:
                role = self.role_repository.get_by_name(db, role_name)
                if not role:
                    role = self.role_repository.create_role(db, role_name)
                db_user.roles.append(role)
            db.commit()
            db.refresh(db_user)
        
        return db_user
    
    def update_last_login(self, db: Session, user_id: int) -> None:
        user = self.user_repository.get(db, user_id)
        if user:
            user.last_login = datetime.utcnow()
            db.add(user)
            db.commit()