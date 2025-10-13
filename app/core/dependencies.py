from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
from db.session import get_db
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Extract user ID from JWT token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        int: User ID from token

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_pagination_params(
    page: int = 1,
    size: int = settings.DEFAULT_PAGE_SIZE
) -> dict:
    """
    Get pagination parameters with validation.

    Args:
        page: Page number (1-based)
        size: Page size

    Returns:
        dict: Pagination parameters with skip and limit

    Raises:
        HTTPException: If parameters are invalid
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be greater than 0"
        )

    if size < 1 or size > settings.MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Page size must be between 1 and {settings.MAX_PAGE_SIZE}"
        )

    skip = (page - 1) * size
    return {"skip": skip, "limit": size, "page": page, "size": size}
