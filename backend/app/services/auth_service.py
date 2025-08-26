"""
Authentication Service
Handles user authentication, JWT tokens, and authorization
"""

import os
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import re
from email_validator import validate_email, EmailNotValidError

from app.models.user import User, UserRole, UserPlan
from app.models.auth import AuthToken, PasswordReset
from app.database import get_session

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
PASSWORD_RESET_EXPIRE_HOURS = int(os.getenv("PASSWORD_RESET_EXPIRE_HOURS", "24"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """
    Service for handling authentication and authorization
    """
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expire = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        self.password_reset_expire = timedelta(hours=PASSWORD_RESET_EXPIRE_HOURS)
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + self.access_token_expire
        
        to_encode.update({
            "exp": expire,
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT refresh token
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time
            
        Returns:
            Encoded JWT refresh token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + self.refresh_token_expire
        
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and verify a JWT token
        
        Args:
            token: JWT token to decode
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"JWT decode error: {str(e)}")
            return None
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"
        
        return True, ""
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """
        Validate email address
        
        Args:
            email: Email to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            validation = validate_email(email)
            return True, ""
        except EmailNotValidError as e:
            return False, str(e)
    
    def validate_cpf(self, cpf: str) -> bool:
        """
        Validate Brazilian CPF
        
        Args:
            cpf: CPF to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Remove non-numeric characters
        cpf = re.sub(r'\D', '', cpf)
        
        if len(cpf) != 11:
            return False
        
        # Check if all digits are the same
        if cpf == cpf[0] * 11:
            return False
        
        # Validate first digit
        sum_digits = sum(int(cpf[i]) * (10 - i) for i in range(9))
        first_digit = (sum_digits * 10) % 11
        if first_digit == 10:
            first_digit = 0
        
        if first_digit != int(cpf[9]):
            return False
        
        # Validate second digit
        sum_digits = sum(int(cpf[i]) * (11 - i) for i in range(10))
        second_digit = (sum_digits * 10) % 11
        if second_digit == 10:
            second_digit = 0
        
        if second_digit != int(cpf[10]):
            return False
        
        return True
    
    def validate_cnpj(self, cnpj: str) -> bool:
        """
        Validate Brazilian CNPJ
        
        Args:
            cnpj: CNPJ to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Remove non-numeric characters
        cnpj = re.sub(r'\D', '', cnpj)
        
        if len(cnpj) != 14:
            return False
        
        # Check if all digits are the same
        if cnpj == cnpj[0] * 14:
            return False
        
        # Validate first digit
        multipliers = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum_digits = sum(int(cnpj[i]) * multipliers[i] for i in range(12))
        first_digit = sum_digits % 11
        if first_digit < 2:
            first_digit = 0
        else:
            first_digit = 11 - first_digit
        
        if first_digit != int(cnpj[12]):
            return False
        
        # Validate second digit
        multipliers = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum_digits = sum(int(cnpj[i]) * multipliers[i] for i in range(13))
        second_digit = sum_digits % 11
        if second_digit < 2:
            second_digit = 0
        else:
            second_digit = 11 - second_digit
        
        if second_digit != int(cnpj[13]):
            return False
        
        return True
    
    async def register_user(
        self,
        db: Session,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        company_name: Optional[str] = None,
        cpf: Optional[str] = None,
        cnpj: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Tuple[Optional[User], str]:
        """
        Register a new user
        
        Args:
            db: Database session
            email: User email
            username: Username
            password: Plain text password
            full_name: Full name
            company_name: Company name
            cpf: Brazilian CPF
            cnpj: Brazilian CNPJ
            phone: Phone number
            
        Returns:
            Tuple of (User object or None, error message)
        """
        # Validate email
        is_valid, error = self.validate_email(email)
        if not is_valid:
            return None, f"Invalid email: {error}"
        
        # Validate password
        is_valid, error = self.validate_password(password)
        if not is_valid:
            return None, error
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            if existing_user.email == email:
                return None, "Email already registered"
            else:
                return None, "Username already taken"
        
        # Validate CPF if provided
        if cpf and not self.validate_cpf(cpf):
            return None, "Invalid CPF"
        
        # Validate CNPJ if provided
        if cnpj and not self.validate_cnpj(cnpj):
            return None, "Invalid CNPJ"
        
        # Create new user
        try:
            user = User(
                email=email,
                username=username,
                hashed_password=self.hash_password(password),
                full_name=full_name,
                company_name=company_name,
                cpf=cpf,
                cnpj=cnpj,
                phone=phone,
                role=UserRole.USER,
                plan=UserPlan.FREE,
                ai_credits=10  # Initial free credits
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"New user registered: {username} ({email})")
            return user, ""
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error registering user: {str(e)}")
            return None, "Registration failed. Please try again."
    
    async def authenticate_user(
        self,
        db: Session,
        username_or_email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Authenticate a user and create tokens
        
        Args:
            db: Database session
            username_or_email: Username or email
            password: Plain text password
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Tuple of (tokens dict or None, error message)
        """
        # Find user by username or email
        user = db.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user:
            return None, "Invalid username or password"
        
        # Check if account is locked
        if user.locked_until and datetime.now(timezone.utc) < user.locked_until:
            return None, "Account is temporarily locked due to too many failed attempts"
        
        # Verify password
        if not self.verify_password(password, user.hashed_password):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
                db.commit()
                return None, "Account locked due to too many failed attempts. Try again in 30 minutes."
            
            db.commit()
            return None, "Invalid username or password"
        
        # Check if account is active
        if not user.is_active:
            return None, "Account is deactivated. Please contact support."
        
        # Reset failed login attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)
        
        # Create tokens
        access_token = self.create_access_token(
            data={
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role.value
            }
        )
        
        refresh_token = self.create_refresh_token(
            data={
                "sub": str(user.id),
                "username": user.username
            }
        )
        
        # Store tokens in database
        auth_token = AuthToken(
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_at=datetime.now(timezone.utc) + self.access_token_expire,
            refresh_token_expires_at=datetime.now(timezone.utc) + self.refresh_token_expire,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(auth_token)
        db.commit()
        
        logger.info(f"User authenticated: {user.username}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user.to_dict()
        }, ""
    
    async def refresh_access_token(
        self,
        db: Session,
        refresh_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Refresh access token using refresh token
        
        Args:
            db: Database session
            refresh_token: Refresh token
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Tuple of (new tokens dict or None, error message)
        """
        # Decode refresh token
        payload = self.decode_token(refresh_token)
        if not payload:
            return None, "Invalid refresh token"
        
        if payload.get("type") != "refresh":
            return None, "Invalid token type"
        
        # Find token in database
        auth_token = db.query(AuthToken).filter(
            AuthToken.refresh_token == refresh_token
        ).first()
        
        if not auth_token:
            return None, "Token not found"
        
        if not auth_token.is_active:
            return None, "Token has been revoked"
        
        if auth_token.is_expired("refresh"):
            return None, "Refresh token has expired"
        
        # Get user
        user = db.query(User).filter(User.id == auth_token.user_id).first()
        if not user or not user.is_active:
            return None, "User not found or inactive"
        
        # Create new access token
        new_access_token = self.create_access_token(
            data={
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role.value
            }
        )
        
        # Update token in database
        auth_token.access_token = new_access_token
        auth_token.access_token_expires_at = datetime.now(timezone.utc) + self.access_token_expire
        auth_token.last_used_at = datetime.now(timezone.utc)
        auth_token.ip_address = ip_address or auth_token.ip_address
        auth_token.user_agent = user_agent or auth_token.user_agent
        
        db.commit()
        
        logger.info(f"Access token refreshed for user: {user.username}")
        
        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }, ""
    
    async def logout(self, db: Session, access_token: str) -> bool:
        """
        Logout user by revoking token
        
        Args:
            db: Database session
            access_token: Access token to revoke
            
        Returns:
            True if successful, False otherwise
        """
        auth_token = db.query(AuthToken).filter(
            AuthToken.access_token == access_token
        ).first()
        
        if auth_token:
            auth_token.revoke("User logout")
            db.commit()
            logger.info(f"User logged out: user_id={auth_token.user_id}")
            return True
        
        return False
    
    async def get_current_user(
        self,
        db: Session,
        token: str
    ) -> Optional[User]:
        """
        Get current user from token
        
        Args:
            db: Database session
            token: Access token
            
        Returns:
            User object or None
        """
        payload = self.decode_token(token)
        if not payload:
            return None
        
        if payload.get("type") != "access":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if user and user.is_active:
            return user
        
        return None
    
    async def create_password_reset_token(
        self,
        db: Session,
        email: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[Optional[str], str]:
        """
        Create password reset token
        
        Args:
            db: Database session
            email: User email
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Tuple of (reset token or None, error message)
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists
            return None, "If the email exists, a reset link will be sent"
        
        # Create reset token
        reset_token = PasswordReset(
            user_id=user.id,
            token=PasswordReset.generate_token(),
            expires_at=datetime.now(timezone.utc) + self.password_reset_expire,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(reset_token)
        db.commit()
        
        logger.info(f"Password reset token created for user: {user.username}")
        
        return reset_token.token, ""
    
    async def reset_password(
        self,
        db: Session,
        token: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Reset user password using reset token
        
        Args:
            db: Database session
            token: Reset token
            new_password: New password
            
        Returns:
            Tuple of (success, error message)
        """
        # Validate new password
        is_valid, error = self.validate_password(new_password)
        if not is_valid:
            return False, error
        
        # Find reset token
        reset_token = db.query(PasswordReset).filter(
            PasswordReset.token == token
        ).first()
        
        if not reset_token:
            return False, "Invalid or expired reset token"
        
        if reset_token.is_used:
            return False, "Reset token has already been used"
        
        if reset_token.is_expired():
            return False, "Reset token has expired"
        
        # Get user
        user = db.query(User).filter(User.id == reset_token.user_id).first()
        if not user:
            return False, "User not found"
        
        # Update password
        user.hashed_password = self.hash_password(new_password)
        reset_token.mark_as_used()
        
        # Revoke all existing tokens for security
        db.query(AuthToken).filter(
            AuthToken.user_id == user.id
        ).update({"is_active": False, "revoked_reason": "Password reset"})
        
        db.commit()
        
        logger.info(f"Password reset for user: {user.username}")
        
        return True, ""
    
    async def change_password(
        self,
        db: Session,
        user: User,
        current_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Change user password
        
        Args:
            db: Database session
            user: User object
            current_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success, error message)
        """
        # Verify current password
        if not self.verify_password(current_password, user.hashed_password):
            return False, "Current password is incorrect"
        
        # Validate new password
        is_valid, error = self.validate_password(new_password)
        if not is_valid:
            return False, error
        
        # Update password
        user.hashed_password = self.hash_password(new_password)
        db.commit()
        
        logger.info(f"Password changed for user: {user.username}")
        
        return True, ""

# Create singleton instance
auth_service = AuthService()