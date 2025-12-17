"""
Database Connection Monitor
Add to sidebar to debug connection issues
"""

import streamlit as st
from config.session import get_connection_stats, dispose_all_connections, force_cleanup
import time

def show_connection_monitor():
    """
    Display real-time connection monitoring in sidebar
    Shows pool stats and provides cleanup buttons
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔌 Database Monitor")
        
        # Get stats
        stats = get_connection_stats()
        
        if 'error' in stats:
            st.error(f"❌ {stats['error']}")
            return
        
        # Display metrics
        col1, col2 = st.columns(2)
        
        with col1:
            total = stats.get('total', 0)
            checked_out = stats.get('checked_out', 0)
            
            st.metric(
                "Active",
                checked_out,
                delta=None,
                help="Connections currently in use"
            )
        
        with col2:
            checked_in = stats.get('checked_in', 0)
            
            st.metric(
                "Idle",
                checked_in,
                delta=None,
                help="Connections waiting in pool"
            )
        
        # Warning if too many connections
        if checked_out > 2:
            st.warning(f"⚠️ {checked_out} active connections!")
        
        # Pool info
        with st.expander("📊 Pool Details"):
            st.write({
                "Pool Size": stats.get('pool_size', 0),
                "Checked In": stats.get('checked_in', 0),
                "Checked Out": stats.get('checked_out', 0),
                "Overflow": stats.get('overflow', 0),
                "Total": stats.get('total', 0)
            })
        
        # Cleanup buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Dispose", use_container_width=True, help="Close idle connections"):
                with st.spinner("Disposing..."):
                    dispose_all_connections()
                    time.sleep(0.5)
                st.success("✅ Disposed")
                st.rerun()
        
        with col2:
            if st.button("💣 Force", use_container_width=True, help="Force kill all"):
                with st.spinner("Force cleanup..."):
                    force_cleanup()
                    time.sleep(0.5)
                st.success("✅ Cleaned")
                st.rerun()
        
        # Auto-refresh
        if st.checkbox("Auto-refresh", value=False, help="Refresh stats every 2s"):
            time.sleep(2)
            st.rerun()

def add_connection_debug_info():
    """
    Add debug info at bottom of page
    Only visible in development
    """
    import os
    
    if os.getenv('STREAMLIT_ENV') != 'production':
        with st.expander("🐛 Connection Debug"):
            stats = get_connection_stats()
            st.json(stats)
            
            if st.button("Test Connection"):
                from config.session import get_db_connection
                try:
                    db = get_db_connection()
                    result = db.execute("SELECT 1")
                    st.success("✅ Connection OK")
                    db.close()
                except Exception as e:
                    st.error(f"❌ {str(e)}")

def log_connection_usage(func):
    """
    Decorator to log connection usage of a function
    Useful for debugging connection leaks
    
    Usage:
        @log_connection_usage
        def my_function():
            db = get_db_connection()
            ...
    """
    def wrapper(*args, **kwargs):
        stats_before = get_connection_stats()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            stats_after = get_connection_stats()
            
            if stats_after.get('checked_out', 0) > stats_before.get('checked_out', 0):
                print(f"⚠️ {func.__name__} leaked connection!")
                print(f"   Before: {stats_before}")
                print(f"   After: {stats_after}")
    
    return wrapper

# Quick check function for troubleshooting
def diagnose_connection_issues():
    """
    Run diagnostics and print recommendations
    """
    stats = get_connection_stats()
    
    if 'error' in stats:
        print("❌ Cannot get pool stats")
        print(f"   Error: {stats['error']}")
        return
    
    print("🔍 Connection Pool Diagnostics")
    print("=" * 50)
    print(f"Pool Size: {stats.get('pool_size', 0)}")
    print(f"Active: {stats.get('checked_out', 0)}")
    print(f"Idle: {stats.get('checked_in', 0)}")
    print(f"Overflow: {stats.get('overflow', 0)}")
    print("=" * 50)
    
    # Recommendations
    checked_out = stats.get('checked_out', 0)
    total = stats.get('total', 0)
    
    if checked_out > 2:
        print("⚠️ WARNING: Too many active connections!")
        print("   → Check if all db.close() are in finally blocks")
        print("   → Use context managers: with get_db_context() as db:")
    
    if total > 5:
        print("⚠️ WARNING: Pool size too large!")
        print("   → Reduce pool_size in session.py")
    
    if stats.get('overflow', 0) > 0:
        print("⚠️ WARNING: Pool overflow detected!")
        print("   → Consider increasing pool_size slightly")
    
    if checked_out == 0 and stats.get('checked_in', 0) > 0:
        print("✅ GOOD: All connections returned to pool")
    
    print("\n💡 Tips for better performance:")
    print("   1. Always use: with get_db_context() as db:")
    print("   2. Close connections in finally blocks")
    print("   3. Use @st.cache_data for read-only queries")
    print("   4. Avoid db operations in loops")
    print("   5. Call dispose_all_connections() on app exit")