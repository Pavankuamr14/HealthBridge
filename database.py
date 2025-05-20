from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database"""
    try:
        # Create all tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def test_db_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        logger.info("Successfully connected to the database!")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        return False 