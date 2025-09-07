# Objectives:
# This file provides essential utility functions for security and authentication.
# Its primary goals are:
# 1. Secure Password Management: To safely hash and verify user passwords using bcrypt.
# 2. JWT (JSON Web Token) Handling: To create, encode, and decode access tokens for stateless authentication.
# 3. Dependency Injection: To define a FastAPI dependency that automatically extracts and validates a JWT from incoming requests,
#    making it easy to protect API endpoints.

from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve security-related variables from environment settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# This context is used for securely hashing and verifying passwords.
# bcrypt is a strong, industry-standard hashing algorithm.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This is the authentication scheme that FastAPI uses to extract the token
# from the "Authorization: Bearer <token>" header in a request.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class TokenData(BaseModel):
    """
    A Pydantic model to represent the data stored within our JWT token payload.
    """
    user_id: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a password using the configured `pwd_context`."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.
    The payload is encoded with a subject (`sub`) and an expiration (`exp`).
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    This is a FastAPI dependency function.
    It takes the JWT token from the request, decodes it, and validates it.
    If the token is invalid or expired, it raises an HTTP exception.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token to get the payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    # Return the user ID from the token payload
    return token_data.user_id
