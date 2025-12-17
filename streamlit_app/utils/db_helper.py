"""
Database Helper Functions
Provides safe database access patterns with guaranteed cleanup
"""

from contextlib import contextmanager
from config.session import get_db_connection, dispose_all_connections, get_connection_stats
import streamlit as st

@contextmanager
def get_db_context():
    """
    Context manager for database connections - ALWAYS use this!
    Guarantees connection is closed even if exception occurs
    
    Usage:
        with get_db_context() as db:
            result = db.execute(query)
            # Connection automatically closed
    
    This is MUCH better than:
        db = get_db_connection()
        try:
            ...
        finally:
            db.close()
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
        # Always close
        try:
            db.close()
        except Exception as e:
            print(f"⚠️ Error closing connection: {e}")

def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """
    Execute query with automatic connection management
    
    Args:
        query: SQL query (text object)
        params: Query parameters (dict)
        fetch_one: Return single row
        fetch_all: Return all rows
    
    Returns:
        Query results or None
    
    Usage:
        result = execute_query(text("SELECT * FROM users WHERE id = :id"), {"id": 123})
    """
    with get_db_context() as db:
        result = db.execute(query, params or {})
        
        if fetch_one:
            return result.fetchone()
        elif fetch_all:
            return result.fetchall()
        else:
            return result

def execute_transaction(func):
    """
    Execute function within a transaction with automatic rollback
    
    Usage:
        def my_updates(db):
            db.execute(query1)
            db.execute(query2)
            db.commit()
        
        execute_transaction(my_updates)
    """
    with get_db_context() as db:
        try:
            func(db)
            return True
        except Exception as e:
            db.rollback()
            raise e

@st.cache_data(ttl=60)  # Cache for 60 seconds
def cached_query(query_str, params_tuple=()):
    """
    Execute query with caching (for read-only queries)
    
    Args:
        query_str: SQL query string (must be hashable)
        params_tuple: Parameters as tuple (must be hashable)
    
    Returns:
        List of results
    
    Usage:
        results = cached_query(
            "SELECT * FROM products WHERE status = %s",
            ("ACTIVE",)
        )
    """
    from sqlalchemy import text
    with get_db_context() as db:
        result = db.execute(text(query_str), dict(enumerate(params_tuple)))
        return result.fetchall()

def show_connection_stats():
    """
    Display current connection pool stats (for debugging)
    Use in Streamlit sidebar
    """
    stats = get_connection_stats()
    
    if 'error' in stats:
        st.sidebar.error(f"❌ Pool stats error: {stats['error']}")
    else:
        with st.sidebar.expander("🔌 DB Connection Stats"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total", stats.get('total', 0))
                st.metric("Checked Out", stats.get('checked_out', 0))
            with col2:
                st.metric("Checked In", stats.get('checked_in', 0))
                st.metric("Overflow", stats.get('overflow', 0))
            
            if stats.get('checked_out', 0) > 0:
                st.warning("⚠️ Active connections detected")

def cleanup_on_rerun():
    """
    Call this at the start of main app to ensure cleanup
    """
    # Check if this is a rerun
    if 'cleanup_done' not in st.session_state:
        st.session_state.cleanup_done = True
    
def force_connection_cleanup():
    """
    Button to manually force connection cleanup
    Useful for debugging
    """
    if st.sidebar.button("🔄 Force Close Connections"):
        dispose_all_connections()
        st.sidebar.success("✅ Connections disposed")
        st.rerun()

# Example usage patterns
"""
GOOD PATTERNS:
--------------

1. Context Manager (BEST):
    with get_db_context() as db:
        result = db.execute(query)

2. Helper Function:
    result = execute_query(text("SELECT * FROM users"))

3. Cached Query:
    result = cached_query("SELECT * FROM products WHERE status = %s", ("ACTIVE",))


BAD PATTERNS (AVOID):
--------------------

1. Manual connection without finally:
    db = get_db_connection()
    result = db.execute(query)
    db.close()  # ❌ If exception occurs, this won't run!

2. Forgetting to close:
    db = get_db_connection()
    result = db.execute(query)
    # ❌ No close() - connection leak!

3. Multiple connections in loop:
    for item in items:
        db = get_db_connection()  # ❌ Creates many connections!
        db.execute(...)
        db.close()
"""