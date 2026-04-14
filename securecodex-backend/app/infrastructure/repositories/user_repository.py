from sqlalchemy.orm import Session
from app.domain.entities.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User:
        """Fetch a user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> User:
        """Fetch a user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_in: UserCreate) -> User:
        """Create a new user in the database."""
        db_user = User(
            email=user_in.email,
            hashed_password=hash_password(user_in.password)
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
