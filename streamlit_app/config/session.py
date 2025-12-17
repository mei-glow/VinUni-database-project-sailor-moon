"""
Database Session Management - STREAMLIT SAFE
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import atexit

from config.config import DATABASE_URL, ensure_database_exists

# Ensure DB exists
ensure_database_exists()

# Engine (NO POOLING)
engine = create_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    connect_args={
        "connect_timeout": 5,
        "charset": "utf8mb4",
        "autocommit": False,
    }
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_connection():
    return SessionLocal()

def dispose_all_connections():
    try:
        engine.dispose()
        print("✅ DB connections disposed")
    except Exception as e:
        print(f"⚠️ Dispose error: {e}")

atexit.register(dispose_all_connections)

print("✅ Streamlit DB session initialized (NullPool)")
