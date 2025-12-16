import streamlit as st
import os
from pathlib import Path
from utils.auth import authenticate_user, is_authenticated, logout

# ============================================================
# DATABASE INITIALIZATION WITH SMART LOADING SCREEN
# ============================================================
import atexit
from config.session import dispose_all_connections
atexit.register(dispose_all_connections)


# Page config
st.set_page_config(
    page_title="VinRetail Management",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_database_exists():
    """Quick check if database is already initialized"""
    try:
        from config.session import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = DATABASE() AND table_name = 'users'"
            )).scalar()
            return result > 0
    except:
        return False


def show_init_loading_screen():
    """Display full-screen loading overlay during database initialization"""
    st.markdown("""
        <style>
        .init-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .init-logo {
            font-size: 5rem;
            margin-bottom: 1rem;
            animation: bounce 2s infinite;
        }
        .init-title {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .init-subtitle {
            font-size: 1.5rem;
            opacity: 0.9;
            margin-bottom: 3rem;
        }
        .init-spinner {
            border: 8px solid rgba(255, 255, 255, 0.3);
            border-top: 8px solid white;
            border-radius: 50%;
            width: 80px;
            height: 80px;
            animation: spin 1s linear infinite;
            margin-bottom: 2rem;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        .init-message {
            font-size: 1.3rem;
            font-weight: 500;
            margin-bottom: 1rem;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .init-details {
            font-size: 1rem;
            opacity: 0.8;
            max-width: 600px;
            text-align: center;
            line-height: 1.6;
        }
        .init-progress {
            width: 400px;
            height: 4px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 2px;
            margin: 2rem 0;
            overflow: hidden;
        }
        .init-progress-bar {
            height: 100%;
            background: white;
            animation: progress 3s ease-in-out infinite;
        }
        @keyframes progress {
            0% { width: 0%; }
            50% { width: 70%; }
            100% { width: 100%; }
        }
        </style>
        
        <div class="init-overlay">
            <div class="init-logo">🏪</div>
            <div class="init-title">VinRetail</div>
            <div class="init-subtitle">Management System</div>
            <div class="init-spinner"></div>
            <div class="init-message">Initializing Database...</div>
            <div class="init-progress">
                <div class="init-progress-bar"></div>
            </div>
            <div class="init-details">
                Setting up database for the first time.<br>
                This process may take 10-30 seconds.
            </div>
        </div>
    """, unsafe_allow_html=True)


def show_success_screen():
    """Display success screen after initialization"""
    st.markdown("""
        <style>
        .success-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #4ade80 0%, #10b981 100%);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            animation: fadeIn 0.5s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .success-icon {
            font-size: 6rem;
            margin-bottom: 2rem;
            animation: scaleIn 0.5s;
        }
        @keyframes scaleIn {
            from { transform: scale(0); }
            to { transform: scale(1); }
        }
        .success-title {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        .success-message {
            font-size: 1.5rem;
            opacity: 0.9;
        }
        </style>
        
        <div class="success-overlay">
            <div class="success-icon">✅</div>
            <div class="success-title">Setup Complete!</div>
            <div class="success-message">Redirecting to login page...</div>
        </div>
    """, unsafe_allow_html=True)


def show_error_screen(error_message):
    """Display error screen if initialization fails"""
    st.markdown("""
        <style>
        .error-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            padding: 2rem;
        }
        .error-icon {
            font-size: 6rem;
            margin-bottom: 2rem;
        }
        .error-title {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        .error-message {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 800px;
            text-align: center;
            margin-bottom: 2rem;
        }
        .error-details {
            background: rgba(0, 0, 0, 0.2);
            padding: 1.5rem;
            border-radius: 10px;
            max-width: 800px;
            width: 100%;
            margin-bottom: 2rem;
        }
        .error-code {
            font-family: monospace;
            font-size: 0.9rem;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        </style>
        
        <div class="error-overlay">
            <div class="error-icon">❌</div>
            <div class="error-title">Initialization Failed</div>
            <div class="error-message">
                Unable to initialize the database. Please check the error details below.
            </div>
            <div class="error-details">
                <div class="error-code">""" + error_message + """</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.error("**Troubleshooting Steps:**")
    st.info("""
    1. **Check MySQL is running**
       - Windows: Services → MySQL80 → Start
       - Mac: System Preferences → MySQL → Start
    
    2. **Verify .env file credentials:**
       ```
       DB_HOST=127.0.0.1
       DB_PORT=3306
       DB_USER=root
       DB_PASSWORD=your_password
       ```
    
    3. **Test MySQL connection:**
       ```bash
       mysql -u root -p
       ```
    
    4. **Restart the application**
    """)
    
    if st.button("🔄 Retry Initialization", type="primary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.stop()


def initialize_database():
    """Initialize database with full-screen loading UI"""
    
    from config.init_db import init_db
    if st.session_state.get("db_initializing", False):
        show_init_loading_screen()
        st.stop()

    st.session_state["db_initializing"] = True

    # Show loading screen
    loading_placeholder = st.empty()
    
    with loading_placeholder.container():
        show_init_loading_screen()
    
    # Perform initialization
    try:

        success, msg = init_db()

        if success:
            # Clear loading screen
            loading_placeholder.empty()
            
            # Show success screen
            success_placeholder = st.empty()
            with success_placeholder.container():
                show_success_screen()
            
            # Mark as initialized
            st.session_state.db_initialized = True
            st.session_state.init_success = True
            
            # Show balloons
            st.balloons()
            
            # Wait briefly then reload
            import time
            time.sleep(2)
            
            # Clear success screen and reload
            success_placeholder.empty()
            st.rerun()
            
        else:
            loading_placeholder.empty()
            show_error_screen("Database initialization returned False. Check console logs for details.")
            show_error_screen(msg)
    except Exception as e:
        loading_placeholder.empty()
        error_msg = f"Exception: {str(e)}\n\nType: {type(e).__name__}"
        show_error_screen(error_msg)


# ============================================================
# SMART DATABASE CHECK
# ============================================================

if 'db_initialized' not in st.session_state:
    # Quick check: if database already exists, skip loading screen
    if check_database_exists():
        # Database already exists - skip loading, go straight to login
        st.session_state.db_initialized = True
        st.session_state.db_skip_init = True
    else:
        # Database doesn't exist - show loading screen and initialize
        initialize_database()

# ============================================================
# MAIN APP (Only accessible after database check)
# ============================================================


# Load custom CSS
def load_css():
    css_file = Path(__file__).parent / "assets" / "css" / "style.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

def login_page():
    """Display login page"""
    st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <h1>🏪 VinRetail</h1>
                <p>Management System</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login")
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("Login", use_container_width=True)
            with col_b:
                if st.form_submit_button("Clear", use_container_width=True):
                    st.rerun()
            
            if submit:
                if not username or not password:
                    st.error("⚠️ Please enter both username and password")
                else:
                    with st.spinner("Authenticating..."):
                        user = authenticate_user(username, password)
                        
                        if user:
                            st.session_state.user = user
                            st.success(f"✅ Welcome back, {user['username']}!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials or inactive account")


def main_app():
    """Main application after login"""
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <h2 style="color: white;">🏪 VinRetail</h2>
                <p style="color: rgba(255,255,255,0.8);">Management System</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User info
        user = st.session_state.user
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
                <p style="color: white; margin: 0;"><strong>👤 User:</strong> {user['username']}</p>
                <p style="color: white; margin: 0;"><strong>📧 Email:</strong> {user['email']}</p>
                <p style="color: white; margin: 0;"><strong>🎭 Roles:</strong> {', '.join(user['roles'])}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📑 Navigation")
        
        page = st.radio(
            "Go to",
            [
                "🏠 Dashboard",
                "👥 Users",
                "👨‍💼 Employees",
                "📍 Locations",
                "📦 Products",
                "📊 Reports",
                "⚙️ Settings"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    
    # Main content
    if page == "🏠 Dashboard":
        import pages.dashboard as dashboard
        dashboard.show()
    elif page == "👥 Users":
        import pages.users as users
        users.show()
    elif page == "👨‍💼 Employees":
        import pages.employees as employees
        employees.show()
    elif page == "📍 Locations":
        import pages.locations as locations
        locations.show()
    elif page == "📦 Products":
        import pages.products as products
        products.show()
    elif page == "📊 Reports":
        import pages.reports as reports
        reports.show()
    elif page == "⚙️ Settings":
        import pages.settings as settings
        settings.show()

# Main execution
def main():
    if not is_authenticated():
        login_page()
    else:
        main_app()
if __name__ == "__main__":
    main()