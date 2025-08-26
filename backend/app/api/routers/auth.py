"""
Authentication API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from app.database import get_db
from app.services.auth_service import auth_service
from app.models.user import User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Request/Response models
class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    confirm_password: str
    full_name: Optional[str] = Field(None, max_length=255)
    company_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    cpf: Optional[str] = Field(None, max_length=14)
    cnpj: Optional[str] = Field(None, max_length=18)
    accept_terms: bool
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('accept_terms')
    def terms_accepted(cls, v):
        if not v:
            raise ValueError('You must accept the terms and conditions')
        return v

class LoginRequest(BaseModel):
    """User login request"""
    username_or_email: str
    password: str
    remember_me: bool = False

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str

class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserResponse(BaseModel):
    """User response model"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    company_name: Optional[str]
    role: str
    plan: str
    is_verified: bool
    ai_credits: int
    created_at: datetime

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

# Dependency to get current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    user = await auth_service.get_current_user(db, token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Dependency to require admin role
async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin role
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.has_permission("all"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user

@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    req: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    Creates a new user account and returns authentication tokens
    """
    # Get client info
    client_ip = req.client.host if req.client else None
    user_agent = req.headers.get("User-Agent")
    
    # Register user
    user, error = await auth_service.register_user(
        db=db,
        email=request.email,
        username=request.username,
        password=request.password,
        full_name=request.full_name,
        company_name=request.company_name,
        cpf=request.cpf,
        cnpj=request.cnpj,
        phone=request.phone
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Auto-login after registration
    tokens, error = await auth_service.authenticate_user(
        db=db,
        username_or_email=request.username,
        password=request.password,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration successful but login failed"
        )
    
    # TODO: Send welcome email in background
    # background_tasks.add_task(send_welcome_email, user.email, user.full_name)
    
    logger.info(f"New user registered: {user.username}")
    
    return TokenResponse(**tokens)

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    req: Request = None,
    db: Session = Depends(get_db)
):
    """
    Login user
    
    Authenticates user credentials and returns tokens
    """
    # Get client info
    client_ip = req.client.host if req and req.client else None
    user_agent = req.headers.get("User-Agent") if req else None
    
    # Authenticate user
    tokens, error = await auth_service.authenticate_user(
        db=db,
        username_or_email=form_data.username,
        password=form_data.password,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return TokenResponse(**tokens)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """
    Refresh access token
    
    Uses refresh token to get a new access token
    """
    # Get client info
    client_ip = req.client.host if req.client else None
    user_agent = req.headers.get("User-Agent")
    
    # Refresh token
    tokens, error = await auth_service.refresh_access_token(
        db=db,
        refresh_token=request.refresh_token,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )
    
    return TokenResponse(**tokens)

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Logout user
    
    Revokes the current access token
    """
    success = await auth_service.logout(db, token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )
    
    logger.info(f"User logged out: {current_user.username}")
    
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    
    Returns the authenticated user's profile
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        company_name=current_user.company_name,
        role=current_user.role.value,
        plan=current_user.plan.value,
        is_verified=current_user.is_verified,
        ai_credits=current_user.ai_credits,
        created_at=current_user.created_at
    )

@router.put("/me")
async def update_profile(
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile
    
    Updates the authenticated user's profile information
    """
    # Fields that can be updated
    allowed_fields = [
        "full_name", "company_name", "phone", "whatsapp",
        "address", "city", "state", "zip_code",
        "preferred_language", "timezone", "notification_settings"
    ]
    
    # Update only allowed fields
    for field, value in update_data.items():
        if field in allowed_fields and hasattr(current_user, field):
            setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Profile updated for user: {current_user.username}")
    
    return {"message": "Profile updated successfully"}

@router.post("/password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    req: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset
    
    Sends a password reset email to the user
    """
    # Get client info
    client_ip = req.client.host if req.client else None
    user_agent = req.headers.get("User-Agent")
    
    # Create reset token
    token, error = await auth_service.create_password_reset_token(
        db=db,
        email=request.email,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    if token:
        # TODO: Send reset email in background
        # background_tasks.add_task(send_reset_email, request.email, token)
        logger.info(f"Password reset requested for: {request.email}")
    
    # Always return success to prevent email enumeration
    return {
        "message": "If the email exists, a password reset link has been sent"
    }

@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset
    
    Resets the password using the reset token
    """
    success, error = await auth_service.reset_password(
        db=db,
        token=request.token,
        new_password=request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return {"message": "Password has been reset successfully"}

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password
    
    Changes the authenticated user's password
    """
    success, error = await auth_service.change_password(
        db=db,
        user=current_user,
        current_password=request.current_password,
        new_password=request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(f"Password changed for user: {current_user.username}")
    
    return {"message": "Password changed successfully"}

@router.get("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    """
    Verify token validity
    
    Checks if the current token is valid
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username
    }

@router.delete("/me")
async def delete_account(
    password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account
    
    Permanently deletes the user's account
    """
    # Verify password
    if not auth_service.verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Mark account as deleted (soft delete)
    current_user.is_active = False
    current_user.updated_at = datetime.utcnow()
    
    # Revoke all tokens
    from app.models.auth import AuthToken
    db.query(AuthToken).filter(
        AuthToken.user_id == current_user.id
    ).update({"is_active": False, "revoked_reason": "Account deleted"})
    
    db.commit()
    
    logger.info(f"Account deleted: {current_user.username}")
    
    return {"message": "Account deleted successfully"}

# Admin endpoints
@router.get("/users", dependencies=[Depends(require_admin)])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all users (Admin only)
    
    Returns a list of all registered users
    """
    users = db.query(User).offset(skip).limit(limit).all()
    
    return {
        "users": [user.to_dict() for user in users],
        "total": db.query(User).count()
    }

@router.put("/users/{user_id}/status", dependencies=[Depends(require_admin)])
async def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db)
):
    """
    Update user status (Admin only)
    
    Activates or deactivates a user account
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = is_active
    user.updated_at = datetime.utcnow()
    db.commit()
    
    action = "activated" if is_active else "deactivated"
    logger.info(f"User {user.username} {action} by admin")
    
    return {"message": f"User {action} successfully"}

# Export router
__all__ = ['router']