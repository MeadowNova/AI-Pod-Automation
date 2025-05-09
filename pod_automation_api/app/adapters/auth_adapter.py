"""
Adapter for authentication services.

This module provides an adapter for connecting the FastAPI BFF layer to the existing
authentication services in the pod_automation system.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.schemas.user import User, UserCreate, UserInDB, AuthResponse

logger = logging.getLogger(__name__)

class AuthServiceAdapter:
    """Adapter for authentication services."""
    
    def __init__(self):
        """Initialize the authentication service adapter."""
        try:
            # Import Supabase client
            from supabase import create_client, Client
            
            # Initialize Supabase client
            self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            self.initialized = True
            logger.info("Auth service adapter initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import Supabase client: {str(e)}")
            self.initialized = False
        except Exception as e:
            logger.error(f"Failed to initialize Auth service adapter: {str(e)}")
            self.initialized = False
    
    async def authenticate_user(self, email: str, password: str) -> Optional[AuthResponse]:
        """
        Authenticate a user and return tokens.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Optional[AuthResponse]: Authentication response with tokens and user data
        """
        if not self.initialized:
            logger.error("Auth service adapter not initialized")
            raise RuntimeError("Auth service not available")
        
        try:
            # Authenticate with Supabase
            response = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
            user_data = response.user
            
            if not user_data:
                return None
            
            # Create user object
            user = User(
                id=uuid.UUID(user_data.id),
                email=user_data.email,
                name=user_data.user_metadata.get("name"),
                avatar_url=user_data.user_metadata.get("avatar_url"),
                created_at=datetime.fromisoformat(user_data.created_at.replace("Z", "+00:00"))
            )
            
            # Create tokens
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            
            access_token = create_access_token(
                subject=str(user.id), expires_delta=access_token_expires
            )
            refresh_token = create_refresh_token(
                subject=str(user.id), expires_delta=refresh_token_expires
            )
            
            # Return authentication response
            return AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user=user
            )
        
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None
    
    async def create_user(self, user_in: UserCreate) -> AuthResponse:
        """
        Create a new user and return tokens.
        
        Args:
            user_in: User creation data
            
        Returns:
            AuthResponse: Authentication response with tokens and user data
        """
        if not self.initialized:
            logger.error("Auth service adapter not initialized")
            raise RuntimeError("Auth service not available")
        
        try:
            # Create user with Supabase
            response = self.supabase.auth.sign_up({
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
            
            # Create user object
            user = User(
                id=uuid.UUID(user_data.id),
                email=user_data.email,
                name=user_data.user_metadata.get("name"),
                avatar_url=user_data.user_metadata.get("avatar_url"),
                created_at=datetime.fromisoformat(user_data.created_at.replace("Z", "+00:00"))
            )
            
            # Create tokens
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            
            access_token = create_access_token(
                subject=str(user.id), expires_delta=access_token_expires
            )
            refresh_token = create_refresh_token(
                subject=str(user.id), expires_delta=refresh_token_expires
            )
            
            # Return authentication response
            return AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user=user
            )
        
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise ValueError(f"Error creating user: {str(e)}")
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[User]: User data or None if not found
        """
        if not self.initialized:
            logger.error("Auth service adapter not initialized")
            raise RuntimeError("Auth service not available")
        
        try:
            # Get user from Supabase
            response = self.supabase.table("users").select("*").eq("id", user_id).execute()
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


# Create a singleton instance
auth_service = AuthServiceAdapter()
