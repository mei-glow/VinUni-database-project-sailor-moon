"""
Database Session Management
Optimized for Streamlit with proper connection pooling and cleanup
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from config.config import DATABASE_URL, ensure_database_exists

# ============================================================
# Ensure database exists BEFORE creating engine
# ============================================================
ensure_database_exists()

# ============================================================
# OPTIMIZED ENGINE - Low memory footprint
# ============================================================
engine = create_engine(
    DATABASE_URL,
    
    # ✅ CRITICAL FIXES:
    echo=False,                    # ❌ Was True - don't print SQL (saves RAM!)
    pool_pre_ping=True,            # Check connection health
    pool_recycle=300,              # Recycle after 5 minutes (not forever!)
    pool_size=3,                   # ✅ Only 3 connections (was unlimited!)
    max_overflow=2,                # ✅ Max 2 extra (was unlimited!)
    pool_timeout=20,               # Wait max 20s
    
    # ✅ Remove AUTOCOMMIT and MULTI_STATEMENTS
    # isolation_level="READ COMMITTED",  # Normal transaction level
    
    connect_args={
        'connect_timeout': 10,     # Connection timeout
        'charset': 'utf8mb4',
        # ❌ REMOVED: "client_flag": CLIENT.MULTI_STATEMENTS
    }
)

# ============================================================
# Connection Lifecycle Events - Auto cleanup
# ============================================================
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Configure connection on creation"""
    dbapi_conn.autocommit = False

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Cleanup when connection returned to pool"""
    try:
        dbapi_conn.rollback()  # Clear any pending transactions
    except:
        pass

@event.listens_for(engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Final cleanup on close"""
    pass

# ============================================================
# Session Factory
# ============================================================
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False  # ✅ Don't expire objects after commit
)

def get_db():
    """
    Get database session with auto-cleanup
    Use with context manager or dependency injection
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_connection():
    """
    Get single database connection
    ⚠️  WARNING: Must close manually!
    
    Better practice:
        from utils.db_helper import get_db_context
        with get_db_context() as db:
            ...
    """
    return SessionLocal()

def dispose_all_connections():
    """
    Dispose all connections - call on app shutdown
    """
    try:
        engine.dispose()
        print("✅ All database connections closed")
    except Exception as e:
        print(f"⚠️ Error disposing connections: {e}")