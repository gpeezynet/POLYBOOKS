from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate, Token
from app.services.authentication import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from app.api.dependencies import get_current_active_user, get_admin_user

router = APIRouter(tags=["authentication"])
auth_service = AuthService()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Update last login time
    auth_service.update_last_login(db, user.id)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/", response_model=UserSchema)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_user = auth_service.create_user(db, user)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    return db_user

@router.get("/users/me/", response_model=UserSchema)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    return current_user

@router.put("/users/me/", response_model=UserSchema)
async def update_user_me(
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Update user information
    updated_user = auth_service.update_user(db, current_user.id, user)
    return updated_user