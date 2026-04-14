from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.application.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import Token
from app.api.dependencies.auth import get_current_user
from app.domain.entities.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    auth_service = AuthService(db)
    return auth_service.signup(user_in)

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token."""
    auth_service = AuthService(db)
    return auth_service.login(user_in)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user
