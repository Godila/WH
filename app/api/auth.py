from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserResponse
from app.services.auth import AuthService
from app.core.security import create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest, 
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Login endpoint.
    
    Validates email and password, returns JWT token on success.
    
    Args:
        request: LoginRequest with email and password
        db: Async database session
        
    Returns:
        Token with access_token and token_type
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    user = await AuthService.authenticate_user(db, request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current user endpoint.
    
    Returns the authenticated user's information.
    
    Args:
        current_user: The authenticated user (from JWT token)
        
    Returns:
        UserResponse with user details
    """
    return current_user
