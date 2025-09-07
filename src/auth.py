# This file manages user authentication, including password hashing, token creation, and token validation.

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Context for securely hashing passwords using a recommended algorithm.
# The 'sha256_crypt' scheme is a strong choice. 'deprecated="auto"' automatically
# switches to a newer scheme if one becomes available in a future library version.
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# SECURITY WARNING: In a production environment, this secret key should be
# stored in a secure environment variable, not hardcoded.
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
# Define the expiration time for access tokens in minutes.
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# This class defines a FastAPI dependency that handles extracting the
# bearer token from the 'Authorization' header in incoming requests.
# The `tokenUrl` points to the endpoint that will issue the token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")

class TokenData(BaseModel):
    """
    Pydantic model for the payload of a JWT.
    It contains the user's email, which is used to identify them.
    """
    email: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed one.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Creates a secure hash of a password for storage.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generates a new JWT access token.
    It includes a subject (`sub`) and an expiration time (`exp`).
    The subject is typically the user's unique identifier (e.g., email).
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    A FastAPI dependency that validates the JWT from the request header.
    It decodes the token, checks for a valid user email, and handles
    potential JWT decoding errors by raising an HTTPException.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Extract the user's email from the payload's 'sub' field
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        # If the token is invalid or expired, raise the authentication exception
        raise credentials_exception
    return token_data
