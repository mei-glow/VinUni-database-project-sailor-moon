import streamlit as st
from passlib.context import CryptContext
from sqlalchemy import text
from config.session import get_db_connection

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    """Authenticate user and return user data"""
    db = get_db_connection()
    try:
        # Get user with roles
        query = text("""
            SELECT 
                u.user_id,
                u.username,
                u.email,
                u.password_hash,
                u.is_active,
                GROUP_CONCAT(r.role_name) as roles
            FROM users u
            LEFT JOIN user_roles ur ON u.user_id = ur.user_id
            LEFT JOIN roles r ON ur.role_id = r.role_id
            WHERE u.username = :username
            GROUP BY u.user_id
        """)
        
        result = db.execute(query, {"username": username}).fetchone()
        
        if not result:
            return None
        
        if not result.is_active:
            return None
        
        if not verify_password(password, result.password_hash):
            return None
        
        return {
            "user_id": result.user_id,
            "username": result.username,
            "email": result.email,
            "roles": result.roles.split(",") if result.roles else [],
            "is_active": result.is_active
        }
    finally:
        db.close()

def get_user_permissions(user_id: int):
    """Get all permissions for a user"""
    db = get_db_connection()
    try:
        query = text("""
            SELECT DISTINCT p.permission_code
            FROM user_roles ur
            JOIN role_permissions rp ON ur.role_id = rp.role_id
            JOIN permissions p ON rp.permission_id = p.permission_id
            WHERE ur.user_id = :user_id
        """)
        
        results = db.execute(query, {"user_id": user_id}).fetchall()
        return [row.permission_code for row in results]
    finally:
        db.close()

def check_permission(permission_code: str):
    """Check if current user has permission"""
    if "user" not in st.session_state:
        return False
    
    if "permissions" not in st.session_state:
        st.session_state.permissions = get_user_permissions(st.session_state.user["user_id"])
    
    return permission_code in st.session_state.permissions

def require_permission(permission_code: str):
    """Decorator to require permission for a function"""
    if not check_permission(permission_code):
        st.error(f"⛔ You don't have permission: {permission_code}")
        st.stop()

def is_authenticated():
    """Check if user is authenticated"""
    return "user" in st.session_state and st.session_state.user is not None

def logout():
    """Logout user"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()