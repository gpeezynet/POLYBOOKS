from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.user import User, Role
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

class RoleRepository:
    def get_by_name(self, db: Session, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()
    
    def create_role(self, db: Session, name: str, description: Optional[str] = None) -> Role:
        db_role = Role(name=name, description=description)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    
    def get_roles(self, db: Session) -> List[Role]:
        return db.query(Role).all()