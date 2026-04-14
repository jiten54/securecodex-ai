import secrets
from sqlalchemy.orm import Session
from app.domain.entities.api_key import APIKey
from typing import Optional

class APIKeyRepository:
    def __init__(self, db: Session):
        self.db = db

    def generate_key(self) -> str:
        """Generate a secure random API key."""
        return f"scx_{secrets.token_urlsafe(32)}"

    def create_api_key(self, user_id: int) -> APIKey:
        """Create a new API key for a user."""
        new_key = self.generate_key()
        db_api_key = APIKey(key=new_key, user_id=user_id)
        self.db.add(db_api_key)
        self.db.commit()
        self.db.refresh(db_api_key)
        return db_api_key

    def get_user_by_key(self, key: str) -> Optional[int]:
        """Get user ID associated with an API key."""
        api_key = self.db.query(APIKey).filter(APIKey.key == key).first()
        return api_key.user_id if api_key else None

    def get_keys_by_user(self, user_id: int):
        """Get all API keys for a user."""
        return self.db.query(APIKey).filter(APIKey.user_id == user_id).all()
