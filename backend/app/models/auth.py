"""
Authentication Models
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from .user import Base
import secrets

class AuthToken(Base):
    """Authentication tokens model"""
    __tablename__ = "auth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Token data
    access_token = Column(Text, unique=True, index=True, nullable=False)
    refresh_token = Column(Text, unique=True, index=True, nullable=False)
    token_type = Column(String(50), default="bearer")
    
    # Expiration
    access_token_expires_at = Column(DateTime(timezone=True), nullable=False)
    refresh_token_expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Security
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(String(500))
    device_id = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime(timezone=True))
    revoked_reason = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<AuthToken user_id={self.user_id}>"
    
    def is_expired(self, token_type: str = "access") -> bool:
        """Check if token is expired"""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        if token_type == "access":
            return now > self.access_token_expires_at
        elif token_type == "refresh":
            return now > self.refresh_token_expires_at
        
        return True
    
    def revoke(self, reason: str = None):
        """Revoke the token"""
        from datetime import datetime, timezone
        self.is_active = False
        self.revoked_at = datetime.now(timezone.utc)
        self.revoked_reason = reason or "Manual revocation"

class PasswordReset(Base):
    """Password reset tokens model"""
    __tablename__ = "password_resets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Token
    token = Column(String(255), unique=True, index=True, nullable=False)
    
    # Status
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime(timezone=True))
    
    # Security
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PasswordReset user_id={self.user_id}>"
    
    @staticmethod
    def generate_token() -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    def is_expired(self) -> bool:
        """Check if reset token is expired"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at
    
    def mark_as_used(self):
        """Mark token as used"""
        from datetime import datetime, timezone
        self.is_used = True
        self.used_at = datetime.now(timezone.utc)