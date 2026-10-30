from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings
from app.core.logging import logger

# Convert postgres:// or asyncpg if needed, default to psycopg2 or standard sync engine
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine_kwargs = {}
if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(db_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db_schema():
    """Helper to initialize tables and pgvector extension if not exists"""
    try:
        from app.db.base import Base
        import app.models  # load models
        with engine.connect() as conn:
            if not db_url.startswith("sqlite"):
                from sqlalchemy import text
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema checked/initialized successfully.")
    except Exception as e:
        logger.warning(f"Could not auto-create database tables on startup: {e}")
