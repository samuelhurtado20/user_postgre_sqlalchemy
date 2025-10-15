from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from services.user_service import UserService
from schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserList,
    UserLogin, UserToken, UserPasswordChange
)
from core.dependencies import get_pagination_params, get_current_user_id
from core.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user.

    Args:
        user_data: User creation data
        db: Database session

    Returns:
        UserResponse: Created user information
    """
    logger.info(f"Creating user: {user_data.username}")
    user_service = UserService(db)
    user = user_service.create_user(user_data)
    return UserResponse.model_validate(user)


@router.get("/", response_model=UserList)
def get_users(
    pagination: dict = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    """
    Get all users with pagination.

    Args:
        pagination: Pagination parameters
        db: Database session

    Returns:
        UserList: Paginated list of users
    """
    logger.info(f"Getting users with pagination: {pagination}")
    user_service = UserService(db)
    result = user_service.get_all_users(
        skip=pagination["skip"],
        limit=pagination["limit"]
    )

    # Convert users to response models
    user_responses = [UserResponse.model_validate(
        user) for user in result["users"]]

    return UserList(
        users=user_responses,
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user by ID.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        UserResponse: User information

    Raises:
        HTTPException: If user not found
    """
    logger.info(f"Getting user by ID: {user_id}")
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)

    if not user:
        logger.warning(f"User {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user information.

    Args:
        user_id: User ID to update
        user_data: Updated user data
        db: Database session

    Returns:
        UserResponse: Updated user information
    """
    logger.info(f"Updating user: {user_id}")
    user_service = UserService(db)
    user = user_service.update_user(user_id, user_data)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete user (soft delete).

    Args:
        user_id: User ID to delete
        db: Database session
    """
    logger.info(f"Deleting user: {user_id}")
    user_service = UserService(db)
    user_service.delete_user(user_id)


@router.post("/login", response_model=UserToken)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token.

    Args:
        login_data: Login credentials
        db: Database session

    Returns:
        UserToken: Access token information

    Raises:
        HTTPException: If authentication fails
    """
    logger.info(f"User login attempt: {login_data.username}")
    user_service = UserService(db)
    user = user_service.authenticate_user(
        login_data.username, login_data.password)

    if not user:
        logger.warning(f"Failed login attempt for: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    token_data = user_service.create_access_token(user.id)
    logger.info(f"User {user.username} logged in successfully")

    return UserToken(**token_data)


@router.get("/me", response_model=UserResponse)
def get_current_user(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information.

    Args:
        current_user_id: Current user ID from token
        db: Database session

    Returns:
        UserResponse: Current user information
    """
    logger.info(f"Getting current user info: {current_user_id}")
    user_service = UserService(db)
    user = user_service.get_user_by_id(current_user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)
