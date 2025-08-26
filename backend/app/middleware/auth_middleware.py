"""
Authentication Middleware
"""

from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
from typing import Optional

from app.services.auth_service import auth_service
from app.database import get_session

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling authentication across the application
    """
    
    def __init__(self, app, excluded_paths: Optional[list] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/api/auth/register",
            "/api/auth/login",
            "/api/auth/password-reset",
            "/api/auth/password-reset/confirm",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and check authentication
        """
        # Skip authentication for excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Get authorization header
        authorization = request.headers.get("Authorization")
        
        # Check if it's an API endpoint that requires authentication
        if request.url.path.startswith("/api/") and not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing authentication credentials"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validate token if present
        if authorization:
            scheme, token = get_authorization_scheme_param(authorization)
            
            if scheme.lower() != "bearer":
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid authentication scheme"},
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Verify token
            db = get_session()
            try:
                user = await auth_service.get_current_user(db, token)
                if user:
                    # Attach user to request state
                    request.state.user = user
                    request.state.user_id = user.id
                    request.state.username = user.username
                else:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid or expired token"},
                        headers={"WWW-Authenticate": "Bearer"}
                    )
            except Exception as e:
                logger.error(f"Authentication error: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication failed"},
                    headers={"WWW-Authenticate": "Bearer"}
                )
            finally:
                db.close()
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
    
    def _is_excluded_path(self, path: str) -> bool:
        """
        Check if path is excluded from authentication
        """
        for excluded in self.excluded_paths:
            if path == excluded or path.startswith(excluded):
                return True
        return False

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting API requests
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}  # Simple in-memory storage
    
    async def dispatch(self, request: Request, call_next):
        """
        Check rate limits
        """
        import time
        
        # Get client identifier (IP or user ID)
        client_id = request.client.host if request.client else "unknown"
        if hasattr(request.state, "user_id"):
            client_id = f"user_{request.state.user_id}"
        
        # Get current minute
        current_minute = int(time.time() / 60)
        
        # Initialize or reset counter
        if client_id not in self.request_counts:
            self.request_counts[client_id] = {"minute": current_minute, "count": 0}
        elif self.request_counts[client_id]["minute"] != current_minute:
            self.request_counts[client_id] = {"minute": current_minute, "count": 0}
        
        # Check rate limit
        if self.request_counts[client_id]["count"] >= self.requests_per_minute:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please try again later."},
                headers={"Retry-After": "60"}
            )
        
        # Increment counter
        self.request_counts[client_id]["count"] += 1
        
        # Clean old entries (simple cleanup)
        if len(self.request_counts) > 10000:
            # Keep only entries from current minute
            self.request_counts = {
                k: v for k, v in self.request_counts.items()
                if v["minute"] == current_minute
            }
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - self.request_counts[client_id]["count"]
        )
        response.headers["X-RateLimit-Reset"] = str((current_minute + 1) * 60)
        
        return response

class CORSMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling CORS
    """
    
    def __init__(
        self,
        app,
        allow_origins: list = ["*"],
        allow_methods: list = ["*"],
        allow_headers: list = ["*"],
        allow_credentials: bool = True
    ):
        super().__init__(app)
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.allow_credentials = allow_credentials
    
    async def dispatch(self, request: Request, call_next):
        """
        Handle CORS headers
        """
        # Handle preflight requests
        if request.method == "OPTIONS":
            return JSONResponse(
                status_code=200,
                headers=self._get_cors_headers(request)
            )
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers
        for key, value in self._get_cors_headers(request).items():
            response.headers[key] = value
        
        return response
    
    def _get_cors_headers(self, request: Request) -> dict:
        """
        Get CORS headers based on request origin
        """
        headers = {}
        origin = request.headers.get("origin")
        
        # Check if origin is allowed
        if "*" in self.allow_origins:
            headers["Access-Control-Allow-Origin"] = "*"
        elif origin in self.allow_origins:
            headers["Access-Control-Allow-Origin"] = origin
        elif origin:
            # Check for wildcard subdomains
            for allowed in self.allow_origins:
                if allowed.startswith("*.") and origin.endswith(allowed[1:]):
                    headers["Access-Control-Allow-Origin"] = origin
                    break
        
        # Add other CORS headers
        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"
        
        headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
        headers["Access-Control-Max-Age"] = "3600"
        
        return headers

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and responses
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Log request and response details
        """
        import time
        import uuid
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response {request_id}: {response.status_code} "
            f"in {process_time:.3f}s"
        )
        
        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response