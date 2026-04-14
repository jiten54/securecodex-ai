from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.core.security import verify_password, create_access_token
from app.schemas.token import Token

class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def signup(self, user_in: UserCreate):
        """Handle user registration logic."""
        user = self.user_repo.get_user_by_email(user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        return self.user_repo.create_user(user_in)

    def login(self, user_in: UserLogin) -> Token:
        """Handle user login and token generation."""
        user = self.user_repo.get_user_by_email(user_in.email)
        if not user or not verify_password(user_in.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(subject=user.id)
        return Token(access_token=access_token, token_type="bearer")
