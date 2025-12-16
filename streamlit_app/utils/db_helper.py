"""
Database Helper Utilities
Safe context managers for database connections
"""

from contextlib import contextmanager
from config.session import get_db_connection

@contextmanager
def get_db_context():
    """
    Context manager for safe database connection handling
    Automatically closes connection even if exception occurs
    
    Usage:
        from utils.db_helper import get_db_context
        
        with get_db_context() as db:
            result = db.execute(text("SELECT * FROM users"))
            data = result.fetchall()
        # Connection automatically closed here
    
    This is THE RECOMMENDED WAY to use database in Streamlit pages
    """
    db = get_db_connection()
    try:
        yield db
    except Exception as e:
        # Rollback on error
        try:
            db.rollback()
        except:
            pass
        raise e
    finally:
        # ALWAYS close connection
        try:
            db.close()
        except:
            pass