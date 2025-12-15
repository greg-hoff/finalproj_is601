"""
Unit tests for JWT authentication functions.

This module tests the core JWT functionality including:
- Password hashing and verification
- Token creation and validation
- Token decoding and payload extraction
- Error handling for invalid tokens
"""

import pytest
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException

from app.auth.jwt import (
    verify_password,
    get_password_hash,
    create_token
)
from app.auth.jwt_sync import (
    decode_token_sync,
    get_current_user_sync
)
from app.schemas.token import TokenType
from app.core.config import get_settings


# ------------------------------------------------------------------------------
# Password Hashing Tests
# ------------------------------------------------------------------------------

def test_password_hashing():
    """Test password hash and verify functions."""
    password = "test_password_123"
    
    # Test hashing
    hashed = get_password_hash(password)
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    assert hashed != password  # Should be different from plain text
    
    # Test verification
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False
    assert verify_password("", hashed) is False


def test_password_hashing_different_passwords():
    """Test that different passwords produce different hashes."""
    password1 = "password1"
    password2 = "password2"
    
    hash1 = get_password_hash(password1)
    hash2 = get_password_hash(password2)
    
    assert hash1 != hash2
    assert verify_password(password1, hash1)
    assert verify_password(password2, hash2)
    assert not verify_password(password1, hash2)
    assert not verify_password(password2, hash1)


# ------------------------------------------------------------------------------
# Token Creation Tests
# ------------------------------------------------------------------------------

def test_create_access_token():
    """Test creating an access token."""
    user_id = str(uuid.uuid4())
    
    token = create_token(user_id, TokenType.ACCESS)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode token to verify contents (without signature verification for testing)
    settings = get_settings()
    payload = jwt.decode(
        token, 
        settings.JWT_SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    
    assert payload["sub"] == user_id
    assert payload["type"] == TokenType.ACCESS.value
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload


def test_create_refresh_token():
    """Test creating a refresh token."""
    user_id = str(uuid.uuid4())
    
    token = create_token(user_id, TokenType.REFRESH)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode token to verify contents
    settings = get_settings()
    payload = jwt.decode(
        token, 
        settings.JWT_REFRESH_SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    
    assert payload["sub"] == user_id
    assert payload["type"] == TokenType.REFRESH.value


def test_create_token_with_uuid():
    """Test creating token with UUID user_id."""
    user_id = uuid.uuid4()
    
    token = create_token(user_id, TokenType.ACCESS)
    
    assert isinstance(token, str)
    
    # Verify UUID was converted to string
    settings = get_settings()
    payload = jwt.decode(
        token, 
        settings.JWT_SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    
    assert payload["sub"] == str(user_id)


def test_create_token_with_custom_expiry():
    """Test creating token with custom expiration."""
    user_id = str(uuid.uuid4())
    expires_delta = timedelta(minutes=30)
    
    token = create_token(user_id, TokenType.ACCESS, expires_delta)
    
    assert isinstance(token, str)
    
    settings = get_settings()
    payload = jwt.decode(
        token, 
        settings.JWT_SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    
    # Check expiration is roughly 30 minutes from now
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    expected_exp = datetime.now(timezone.utc) + expires_delta
    
    # Allow 1 minute tolerance for test execution time
    assert abs((exp_time - expected_exp).total_seconds()) < 60


# ------------------------------------------------------------------------------
# Token Decoding Tests
# ------------------------------------------------------------------------------

def test_decode_valid_token():
    """Test decoding a valid token."""
    user_id = str(uuid.uuid4())
    
    # Create token
    token = create_token(user_id, TokenType.ACCESS)
    
    # Use sync version with no blacklist checker (equivalent to returning False)
    payload = decode_token_sync(token, TokenType.ACCESS, blacklist_checker=None)
    
    assert payload["sub"] == user_id
    assert payload["type"] == TokenType.ACCESS.value
    assert "exp" in payload
    assert "jti" in payload


def test_decode_token_wrong_type():
    """Test decoding token with wrong token type."""
    user_id = str(uuid.uuid4())
    
    # Create access token but try to decode as refresh
    token = create_token(user_id, TokenType.ACCESS)
    
    # Use sync version - no asyncio needed
    with pytest.raises(HTTPException) as exc_info:
        decode_token_sync(token, TokenType.REFRESH, blacklist_checker=None)
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail


def test_decode_blacklisted_token():
    """Test decoding a blacklisted token."""
    user_id = str(uuid.uuid4())
    token = create_token(user_id, TokenType.ACCESS)
    
    # Mock blacklisted token with sync function that returns True
    def mock_blacklist_check(jti):
        return True
    
    with pytest.raises(HTTPException) as exc_info:
        decode_token_sync(token, TokenType.ACCESS, blacklist_checker=mock_blacklist_check)
    
    assert exc_info.value.status_code == 401
    assert "Token has been revoked" in exc_info.value.detail


def test_decode_expired_token():
    """Test decoding an expired token."""
    user_id = str(uuid.uuid4())
    
    # Create token that expires immediately
    expires_delta = timedelta(seconds=-1)  # Already expired
    token = create_token(user_id, TokenType.ACCESS, expires_delta)
    
    # Use sync version
    with pytest.raises(HTTPException) as exc_info:
        decode_token_sync(token, TokenType.ACCESS, blacklist_checker=None)
    
    assert exc_info.value.status_code == 401
    assert "Token has expired" in exc_info.value.detail


def test_decode_invalid_token():
    """Test decoding an invalid token."""
    invalid_token = "invalid.jwt.token"
    
    # Use sync version
    with pytest.raises(HTTPException) as exc_info:
        decode_token_sync(invalid_token, TokenType.ACCESS, blacklist_checker=None)
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail


def test_decode_token_skip_expiry():
    """Test decoding token with expiry verification disabled."""
    user_id = str(uuid.uuid4())
    
    # Create expired token
    expires_delta = timedelta(seconds=-1)
    token = create_token(user_id, TokenType.ACCESS, expires_delta)
    
    # Should work when verify_exp=False
    payload = decode_token_sync(token, TokenType.ACCESS, verify_exp=False, blacklist_checker=None)
    
    assert payload["sub"] == user_id


# ------------------------------------------------------------------------------
# Get Current User Tests
# ------------------------------------------------------------------------------

def test_get_current_user_success():
    """Test successful user retrieval from token."""
    user_id = str(uuid.uuid4())
    token = create_token(user_id, TokenType.ACCESS)
    
    # Mock user from database
    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.is_active = True
    
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Use sync version
    user = get_current_user_sync(token, mock_db, blacklist_checker=None)
    
    assert user == mock_user
    mock_db.query.assert_called_once()


def test_get_current_user_not_found():
    """Test user not found in database."""
    user_id = str(uuid.uuid4())
    token = create_token(user_id, TokenType.ACCESS)
    
    # Mock user not found
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Use sync version - sync version has same exception wrapping as async version
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_sync(token, mock_db, blacklist_checker=None)
    
    assert exc_info.value.status_code == 401
    assert "404: User not found" in exc_info.value.detail


def test_get_current_user_inactive():
    """Test inactive user."""
    user_id = str(uuid.uuid4())
    token = create_token(user_id, TokenType.ACCESS)
    
    # Mock inactive user
    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.is_active = False
    
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Use sync version - sync version has same exception wrapping as async version
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_sync(token, mock_db, blacklist_checker=None)
    
    assert exc_info.value.status_code == 401
    assert "400: Inactive user" in exc_info.value.detail


def test_get_current_user_invalid_token():
    """Test get current user with invalid token."""
    invalid_token = "invalid.token"
    mock_db = MagicMock()
    
    # Use sync version
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_sync(invalid_token, mock_db, blacklist_checker=None)
    
    assert exc_info.value.status_code == 401


# ------------------------------------------------------------------------------
# Error Handling Tests
# ------------------------------------------------------------------------------

def test_create_token_encoding_error():
    """Test token creation with encoding error."""
    user_id = str(uuid.uuid4())
    
    # Mock jwt.encode to raise exception
    with patch('app.auth.jwt.jwt.encode', side_effect=Exception("Encoding failed")):
        with pytest.raises(HTTPException) as exc_info:
            create_token(user_id, TokenType.ACCESS)
    
    assert exc_info.value.status_code == 500
    assert "Could not create token" in exc_info.value.detail


def test_unique_token_identifiers():
    """Test that tokens have unique JTIs."""
    user_id = str(uuid.uuid4())
    
    token1 = create_token(user_id, TokenType.ACCESS)
    token2 = create_token(user_id, TokenType.ACCESS)
    
    settings = get_settings()
    payload1 = jwt.decode(token1, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    payload2 = jwt.decode(token2, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    assert payload1["jti"] != payload2["jti"]  # Should have different JTIs
    assert payload1["sub"] == payload2["sub"]  # But same subject