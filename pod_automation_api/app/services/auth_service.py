from typing import Optional
import uuid
from datetime import datetime

from app.schemas.user import User, UserCreate, UserInDB
from app.core.security import get_password_hash, verify_password

# This is a placeholder for a database connection
# In a real implementation, you would use Supabase or another database
users_db = {}


async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """
    Get a user by email
    """
    # In a real implementation, you would query the database
    for user_id, user in users_db.items():
        if user.email == email:
            return user
    return None


async def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get a user by ID
    """
    # In a real implementation, you would query the database
    if user_id in users_db:
        user = users_db[user_id]
        return User(
            id=user.id,
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            created_at=user.created_at
        )
    
    # For development, return a mock user
    return User(
        id=uuid.UUID(user_id),
        email="user@example.com",
        name="Test User",
        avatar_url=None,
        created_at=datetime.utcnow()
    )


async def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate a user
    """
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return User(
        id=user.id,
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        created_at=user.created_at
    )


async def create_user(user_in: UserCreate) -> User:
    """
    Create a new user
    """
    # Check if user with this email already exists
    existing_user = await get_user_by_email(user_in.email)
    if existing_user:
        raise ValueError("Email already registered")
    
    # Create new user
    user_id = str(uuid.uuid4())
    created_at = datetime.utcnow()
    
    # In a real implementation, you would store this in the database
    users_db[user_id] = UserInDB(
        id=uuid.UUID(user_id),
        email=user_in.email,
        name=user_in.name,
        avatar_url=user_in.avatar_url,
        created_at=created_at,
        hashed_password=get_password_hash(user_in.password)
    )
    
    return User(
        id=uuid.UUID(user_id),
        email=user_in.email,
        name=user_in.name,
        avatar_url=user_in.avatar_url,
        created_at=created_at
    )


# Helper functions for password hashing
def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    # In a real implementation, you would use a proper password hashing library
    return f"hashed_{password}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    """
    # In a real implementation, you would use a proper password hashing library
    return hashed_password == f"hashed_{plain_password}"
