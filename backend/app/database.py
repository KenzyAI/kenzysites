"""
Database Configuration and Session Management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://kenzysites:kenzysites123@localhost/kenzysites"
)

# For SQLite (development)
if os.getenv("USE_SQLITE", "false").lower() == "true":
    DATABASE_URL = "sqlite:///./kenzysites.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Get database session
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database tables
    """
    from app.models import user, site, auth  # Import all models
    
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def drop_db():
    """
    Drop all database tables (use with caution!)
    """
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Database tables dropped")

def get_session() -> Session:
    """
    Get a new database session
    
    Returns:
        Database session
    """
    return SessionLocal()

class DatabaseManager:
    """
    Database manager for handling database operations
    """
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def create_tables(self):
        """Create all tables"""
        init_db()
    
    def drop_tables(self):
        """Drop all tables"""
        drop_db()
    
    def get_session(self) -> Session:
        """Get a new session"""
        return SessionLocal()
    
    def execute_raw(self, query: str):
        """Execute raw SQL query"""
        with engine.connect() as conn:
            result = conn.execute(query)
            return result
    
    def backup_database(self, backup_path: str = None):
        """
        Backup database to file
        
        Args:
            backup_path: Path to backup file
        """
        import datetime
        
        if not backup_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_kenzysites_{timestamp}.sql"
        
        if "sqlite" in DATABASE_URL:
            import shutil
            db_path = DATABASE_URL.replace("sqlite:///", "")
            shutil.copy2(db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
        else:
            # For PostgreSQL
            import subprocess
            
            # Parse connection details from DATABASE_URL
            # Format: postgresql://user:password@host/database
            parts = DATABASE_URL.replace("postgresql://", "").split("@")
            user_pass = parts[0].split(":")
            host_db = parts[1].split("/")
            
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            host = host_db[0].split(":")[0]
            database = host_db[1]
            
            cmd = [
                "pg_dump",
                f"--host={host}",
                f"--username={user}",
                f"--dbname={database}",
                f"--file={backup_path}",
                "--no-password"
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = password
            
            subprocess.run(cmd, env=env, check=True)
            logger.info(f"Database backed up to {backup_path}")
    
    def restore_database(self, backup_path: str):
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        if "sqlite" in DATABASE_URL:
            import shutil
            db_path = DATABASE_URL.replace("sqlite:///", "")
            shutil.copy2(backup_path, db_path)
            logger.info(f"Database restored from {backup_path}")
        else:
            # For PostgreSQL
            import subprocess
            
            # Parse connection details
            parts = DATABASE_URL.replace("postgresql://", "").split("@")
            user_pass = parts[0].split(":")
            host_db = parts[1].split("/")
            
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            host = host_db[0].split(":")[0]
            database = host_db[1]
            
            cmd = [
                "psql",
                f"--host={host}",
                f"--username={user}",
                f"--dbname={database}",
                f"--file={backup_path}",
                "--no-password"
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = password
            
            subprocess.run(cmd, env=env, check=True)
            logger.info(f"Database restored from {backup_path}")

# Create singleton instance
db_manager = DatabaseManager()