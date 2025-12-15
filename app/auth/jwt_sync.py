# app/auth/jwt_sync.py
"""
Synchronous versions of JWT functions for testing purposes.
These functions provide the same JWT functionality without asyncio complexity.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union, Callable
from jose import jwt, JWTError
from fastapi import HTTPException, status
from uuid import UUID
import secrets

from app.core.config import get_settings
from app.schemas.token import TokenType

settings = get_settings()

def decode_token_sync(
    token: str,
    token_type: TokenType,
    verify_exp: bool = True,
    blacklist_checker: Optional[Callable[[str], bool]] = None
) -> dict[str, Any]:
    """
    Synchronous version of decode_token for testing.
    
    Args:
        token: JWT token to decode
        token_type: Expected token type  
        verify_exp: Whether to verify expiration
        blacklist_checker: Optional sync function to check blacklist
    """
    try:
        secret = (
            settings.JWT_SECRET_KEY 
            if token_type == TokenType.ACCESS 
            else settings.JWT_REFRESH_SECRET_KEY
        )
        
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": verify_exp}
        )
        
        if payload.get("type") != token_type.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Use optional blacklist checker (for testing we can pass None or mock function)
        if blacklist_checker and blacklist_checker(payload["jti"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user_sync(
    token: str,
    db_session,
    blacklist_checker: Optional[Callable[[str], bool]] = None
):
    """
    Synchronous version of get_current_user for testing.
    """
    try:
        from app.models.user import User
        
        payload = decode_token_sync(token, TokenType.ACCESS, blacklist_checker=blacklist_checker)
        user_id = payload["sub"]
        
        user = db_session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
            
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )