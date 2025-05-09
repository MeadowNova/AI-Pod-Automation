from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.adapters.auth_adapter import auth_service
from app.schemas.token import RefreshRequest
from app.schemas.user import UserCreate, UserLogin, AuthResponse, User
from app.core.security import get_current_user

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
async def login(form_data: UserLogin) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        auth_response = await auth_service.authenticate_user(
            email=form_data.email,
            password=form_data.password
        )

        if not auth_response:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return auth_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate) -> Any:
    """
    Create new user
    """
    try:
        auth_response = await auth_service.create_user(user_in)
        return auth_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(refresh_request: RefreshRequest) -> Any:
    """
    Refresh access token
    """
    # This would validate the refresh token and get the user ID
    # In a real implementation, you would verify this is a valid refresh token
    # For now, we'll just return a 501 Not Implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not implemented yet",
    )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user_id: str = Depends(get_current_user)) -> Any:
    """
    Get current user info
    """
    try:
        user = await auth_service.get_user_by_id(current_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
