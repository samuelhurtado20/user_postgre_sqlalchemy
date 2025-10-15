from sqlalchemy import Column, Integer, String, Boolean, Index
from sqlalchemy.orm import validates
from db.base import Base, TimestampMixin, SoftDeleteMixin
import re


class User(Base, TimestampMixin, SoftDeleteMixin):
    """User model for storing user information."""

    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # User credentials and identification
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    # Will store hashed password
    password = Column(String(255), nullable=False)

    # Personal information (optional)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    # Indexes for performance
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_username_active', 'username', 'is_active'),
    )

    @validates('email')
    def validate_email(self, key, email):
        """Validate email format."""
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise ValueError("Invalid email format")
        return email.lower() if email else email

    @validates('username')
    def validate_username(self, key, username):
        """Validate username format."""
        if username:
            if len(username) < 3:
                raise ValueError("Username must be at least 3 characters long")
            if len(username) > 50:
                raise ValueError("Username must be less than 50 characters")
            if not re.match(r'^[a-zA-Z0-9_-]+$', username):
                raise ValueError(
                    "Username can only contain letters, numbers, underscores, and hyphens")
        return username.lower() if username else username

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    def __str__(self):
        return f"{self.username} ({self.email})"
