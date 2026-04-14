from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session
from typing import Optional
from app.core.config import settings
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.api_key_repository import APIKeyRepository
from app.domain.entities.user import User
from app.schemas.token import TokenData

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    required=False
)

def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
    x_api_key: Optional[str] = Header(None)
) -> User:
    """
    Dependency to get the currently authenticated user.
    Supports both JWT Bearer token and X-API-Key header.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Try API Key Authentication
    if x_api_key:
        api_key_repo = APIKeyRepository(db)
        user_id = api_key_repo.get_user_by_key(x_api_key)
        if user_id:
            user_repo = UserRepository(db)
            user = user_repo.get_user_by_id(user_id)
            if user:
                return user
        raise credentials_exception

    # 2. Try JWT Authentication
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
            token_data = TokenData(user_id=int(user_id))
        except (jwt.JWTError, ValueError):
            raise credentials_exception
        
        user_repo = UserRepository(db)
        user = user_repo.get_user_by_id(user_id=token_data.user_id)
        if user is None:
            raise credentials_exception
        return user

    raise credentials_exception
