from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import math

from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse, UserList, UserLogin, UserToken
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service class for user-related operations."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(user_id: int) -> Dict[str, Any]:
        """Create JWT access token for user."""
        expire = datetime.now(
            timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_data: User creation data

        Returns:
            User: Created user object

        Raises:
            HTTPException: If username or email already exists
        """
        logger.info(f"Creating new user with username: {user_data.username}")

        # Check if username already exists
        existing_user = self.db.query(User).filter(
            and_(
                User.username == user_data.username.lower(),
                User.is_active == True
            )
        ).first()

        if existing_user:
            logger.warning(f"Username {user_data.username} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check if email already exists
        existing_email = self.db.query(User).filter(
            and_(
                User.email == user_data.email.lower(),
                User.is_active == True
            )
        ).first()

        if existing_email:
            logger.warning(f"Email {user_data.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        hashed_password = self.hash_password(user_data.password)

        # Create user
        db_user = User(
            username=user_data.username.lower(),
            email=user_data.email.lower(),
            password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active=True
        )

        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            logger.info(f"User created successfully with ID: {db_user.id}")
            return db_user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user"
            )

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User: User object or None if not found
        """
        logger.debug(f"Getting user by ID: {user_id}")
        return self.db.query(User).filter(
            and_(User.id == user_id, User.is_active == True)
        ).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User: User object or None if not found
        """
        logger.debug(f"Getting user by email: {email}")
        return self.db.query(User).filter(
            and_(User.email == email.lower(), User.is_active == True)
        ).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: Username

        Returns:
            User: User object or None if not found
        """
        logger.debug(f"Getting user by username: {username}")
        return self.db.query(User).filter(
            and_(User.username == username.lower(), User.is_active == True)
        ).first()

    def get_all_users(self, skip: int = 0, limit: int = 20) -> Dict[str, Any]:
        """
        Get all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Dict: Paginated user list with metadata
        """
        logger.debug(f"Getting users with skip={skip}, limit={limit}")

        # Get total count
        total = self.db.query(User).filter(User.is_active == True).count()

        # Get users
        users = self.db.query(User).filter(
            User.is_active == True
        ).offset(skip).limit(limit).all()

        # Calculate pagination metadata
        pages = math.ceil(total / limit) if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1

        return {
            "users": users,
            "total": total,
            "page": page,
            "size": limit,
            "pages": pages
        }

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        Update user information.

        Args:
            user_id: User ID to update
            user_data: Updated user data

        Returns:
            User: Updated user object

        Raises:
            HTTPException: If user not found or validation fails
        """
        logger.info(f"Updating user with ID: {user_id}")

        # Get existing user
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            logger.warning(f"User with ID {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check for username conflicts
        if user_data.username and user_data.username != db_user.username:
            existing_user = self.db.query(User).filter(
                and_(
                    User.username == user_data.username.lower(),
                    User.is_active == True,
                    User.id != user_id
                )
            ).first()

            if existing_user:
                logger.warning(f"Username {user_data.username} already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Check for email conflicts
        if user_data.email and user_data.email != db_user.email:
            existing_email = self.db.query(User).filter(
                and_(
                    User.email == user_data.email.lower(),
                    User.is_active == True,
                    User.id != user_id
                )
            ).first()

            if existing_email:
                logger.warning(f"Email {user_data.email} already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )

        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_user)
            logger.info(f"User {user_id} updated successfully")
            return db_user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating user"
            )

    def delete_user(self, user_id: int) -> bool:
        """
        Soft delete a user (set is_active to False).

        Args:
            user_id: User ID to delete

        Returns:
            bool: True if user was deleted successfully

        Raises:
            HTTPException: If user not found
        """
        logger.info(f"Deleting user with ID: {user_id}")

        # Get existing user
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            logger.warning(f"User with ID {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        try:
            # Soft delete by setting is_active to False
            db_user.is_active = False
            self.db.commit()
            logger.info(f"User {user_id} deleted successfully")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting user"
            )

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username/email and password.

        Args:
            username: Username or email
            password: Plain text password

        Returns:
            User: Authenticated user object or None if authentication fails
        """
        logger.debug(f"Authenticating user: {username}")

        # Try to find user by username or email
        user = self.db.query(User).filter(
            and_(
                or_(
                    User.username == username.lower(),
                    User.email == username.lower()
                ),
                User.is_active == True
            )
        ).first()

        if not user:
            logger.warning(f"User not found: {username}")
            return None

        if not self.verify_password(password, user.password):
            logger.warning(f"Invalid password for user: {username}")
            return None

        logger.info(f"User authenticated successfully: {username}")
        return user
