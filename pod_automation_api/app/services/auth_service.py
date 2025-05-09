from typing import Optional
import uuid
from datetime import datetime
import logging
from supabase import create_client, Client

from app.core.config import settings
from app.schemas.user import User, UserCreate, UserInDB

logger = logging.getLogger(__name__)

# Initialize Supabase client
try:
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    logger.info("Connected to Supabase")
except Exception as e:
    logger.error(f"Failed to connect to Supabase: {str(e)}")
    supabase = None


async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """
    Get a user by email
    """
    if not supabase:
        logger.error("Supabase client not initialized")
        return None

    try:
        response = supabase.table("users").select("*").eq("email", email).execute()
        users = response.data

        if not users:
            return None

        user_data = users[0]
        return UserInDB(
            id=uuid.UUID(user_data["id"]),
            email=user_data["email"],
            name=user_data.get("name"),
            avatar_url=user_data.get("avatar_url"),
            created_at=datetime.fromisoformat(user_data["created_at"].replace("Z", "+00:00")),
            hashed_password=user_data["password"]
        )
    except Exception as e:
        logger.error(f"Error getting user by email: {str(e)}")
        return None


async def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get a user by ID
    """
    if not supabase:
        logger.error("Supabase client not initialized")
        return None

    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        users = response.data

        if not users:
            return None

        user_data = users[0]
        return User(
            id=uuid.UUID(user_data["id"]),
            email=user_data["email"],
            name=user_data.get("name"),
            avatar_url=user_data.get("avatar_url"),
            created_at=datetime.fromisoformat(user_data["created_at"].replace("Z", "+00:00"))
        )
    except Exception as e:
        logger.error(f"Error getting user by ID: {str(e)}")
        return None


async def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate a user using Supabase Auth
    """
    if not supabase:
        logger.error("Supabase client not initialized")
        return None

    try:
        # Use Supabase Auth to sign in
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user_data = response.user

        if not user_data:
            return None

        return User(
            id=uuid.UUID(user_data.id),
            email=user_data.email,
            name=user_data.user_metadata.get("name"),
            avatar_url=user_data.user_metadata.get("avatar_url"),
            created_at=datetime.fromisoformat(user_data.created_at.replace("Z", "+00:00"))
        )
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        return None


async def create_user(user_in: UserCreate) -> User:
    """
    Create a new user using Supabase Auth
    """
    if not supabase:
        logger.error("Supabase client not initialized")
        raise ValueError("Supabase client not initialized")

    try:
        # Check if user already exists
        existing_user = await get_user_by_email(user_in.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Create user with Supabase Auth
        response = supabase.auth.sign_up({
            "email": user_in.email,
            "password": user_in.password,
            "options": {
                "data": {
                    "name": user_in.name,
                    "avatar_url": user_in.avatar_url
                }
            }
        })

        user_data = response.user

        if not user_data:
            raise ValueError("Failed to create user")

        return User(
            id=uuid.UUID(user_data.id),
            email=user_data.email,
            name=user_data.user_metadata.get("name"),
            avatar_url=user_data.user_metadata.get("avatar_url"),
            created_at=datetime.fromisoformat(user_data.created_at.replace("Z", "+00:00"))
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise ValueError(f"Error creating user: {str(e)}")
