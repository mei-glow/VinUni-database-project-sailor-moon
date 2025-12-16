import streamlit as st
from passlib.context import CryptContext
from sqlalchemy import text
from config.session import get_db_connection
from utils.auth import logout

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def show():
    """Display settings page"""
    
    st.markdown("""
        <div class="main-header">
            <h1>⚙️ Settings</h1>
            <p>Manage your account and system preferences</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔐 Security", "ℹ️ About"])
    
    with tab1:
        show_profile()
    
    with tab2:
        show_security()
    
    with tab3:
        show_about()

def show_profile():
    """Display user profile settings"""
    st.markdown("### 👤 User Profile")
    
    user = st.session_state.user
    
    # Display current info
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Current Information")
        st.info(f"""
        **User ID:** {user['user_id']}  
        **Username:** {user['username']}  
        **Email:** {user['email']}  
        **Roles:** {', '.join(user['roles'])}  
        **Status:** {'✅ Active' if user['is_active'] else '❌ Inactive'}
        """)
    
    with col2:
        st.markdown("#### Update Email")
        
        with st.form("update_email_form"):
            new_email = st.text_input("📧 New Email", value=user['email'])
            
            if st.form_submit_button("💾 Update Email", use_container_width=True):
                if not new_email or "@" not in new_email:
                    st.error("❌ Please enter a valid email")
                else:
                    db = get_db_connection()
                    try:
                        update_query = text("""
                            UPDATE users
                            SET email = :email
                            WHERE user_id = :uid
                        """)
                        
                        db.execute(update_query, {
                            "email": new_email,
                            "uid": user['user_id']
                        })
                        db.commit()
                        
                        # Update session
                        st.session_state.user['email'] = new_email
                        
                        st.success("✅ Email updated successfully!")
                        st.rerun()
                    
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error updating email: {str(e)}")
                    
                    finally:
                        db.close()

def show_security():
    """Display security settings"""
    st.markdown("### 🔐 Security Settings")
    
    # Change password
    st.markdown("#### Change Password")
    
    with st.form("change_password_form"):
        current_password = st.text_input("🔑 Current Password", type="password")
        new_password = st.text_input("🔑 New Password", type="password")
        confirm_password = st.text_input("🔑 Confirm New Password", type="password")
        
        if st.form_submit_button("🔒 Change Password", use_container_width=True):
            # Validation
            errors = []
            
            if not current_password:
                errors.append("Current password is required")
            
            if not new_password or len(new_password) < 6:
                errors.append("New password must be at least 6 characters")
            
            if new_password != confirm_password:
                errors.append("New passwords do not match")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                db = get_db_connection()
                try:
                    # Verify current password
                    user = st.session_state.user
                    check_query = text("""
                        SELECT password_hash
                        FROM users
                        WHERE user_id = :uid
                    """)
                    
                    result = db.execute(check_query, {"uid": user['user_id']}).fetchone()
                    
                    if not result or not pwd_context.verify(current_password, result.password_hash):
                        st.error("❌ Current password is incorrect")
                    else:
                        # Update password
                        new_hash = pwd_context.hash(new_password)
                        
                        update_query = text("""
                            UPDATE users
                            SET password_hash = :hash
                            WHERE user_id = :uid
                        """)
                        
                        db.execute(update_query, {
                            "hash": new_hash,
                            "uid": user['user_id']
                        })
                        db.commit()
                        
                        st.success("✅ Password changed successfully! Please login again.")
                        
                        # Logout after password change
                        if st.button("🚪 Logout Now"):
                            logout()
                
                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Error changing password: {str(e)}")
                
                finally:
                    db.close()
    
    st.markdown("---")
    
    # Session info
    st.markdown("#### 🔐 Session Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Logged in as:** {st.session_state.user['username']}  
        **User ID:** {st.session_state.user['user_id']}  
        **Active Permissions:** {len(st.session_state.get('permissions', []))}
        """)
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            logout()

def show_about():
    """Display about information"""
    st.markdown("### ℹ️ About VinRetail Management System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🏪 System Information
        
        **Application:** VinRetail Management System  
        **Version:** 1.0.0  
        **Technology:** Streamlit + MySQL  
        **Database:** VinRetail Database
        
        #### 📚 Features
        
        - 👥 User Management with RBAC
        - 👨‍💼 Employee Management
        - 📍 Location Management
        - 📦 Product & Inventory Management
        - 📊 Advanced Analytics & Reports
        - 🚚 Delivery Tracking
        - 💰 Financial Reports
        """)
    
    with col2:
        st.markdown("""
        #### 🎭 Available Roles
        
        - **ADMIN** - Full system access
        - **SALES** - Sales operations
        - **WAREHOUSE** - Inventory management
        - **DELIVERY** - Delivery operations
        - **HR** - Human resources
        - **MANAGER** - Store management
        - **ANALYST** - Business analytics
        
        #### 🔐 Security Features
        
        - ✅ Argon2 password hashing
        - ✅ Role-based access control
        - ✅ Permission-based operations
        - ✅ Secure session management
        """)
    
    st.markdown("---")
    
    # Database statistics
    st.markdown("### 📊 System Statistics")
    
    db = get_db_connection()
    
    try:
        stats_query = text("""
            SELECT 
                (SELECT COUNT(*) FROM users) as total_users,
                (SELECT COUNT(*) FROM employees) as total_employees,
                (SELECT COUNT(*) FROM products) as total_products,
                (SELECT COUNT(*) FROM locations) as total_locations,
                (SELECT COUNT(*) FROM sales WHERE sale_type = 'INVOICE') as total_sales,
                (SELECT COUNT(*) FROM customers) as total_customers
        """)
        
        stats = db.execute(stats_query).fetchone()
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("Users", stats.total_users)
        with col2:
            st.metric("Employees", stats.total_employees)
        with col3:
            st.metric("Products", stats.total_products)
        with col4:
            st.metric("Locations", stats.total_locations)
        with col5:
            st.metric("Sales", stats.total_sales)
        with col6:
            st.metric("Customers", stats.total_customers)
    
    except Exception as e:
        st.error(f"❌ Error loading statistics: {str(e)}")
    
    finally:
        db.close()
    
    st.markdown("---")
    
    # Support information
    st.markdown("""
    #### 💬 Support & Help
    
    For technical support or questions:
    - 📧 Email: support@vinretail.com
    - 📱 Phone: +84 xxx xxx xxx
    - 🌐 Website: www.vinretail.com
    
    ---
    
    <div style="text-align: center; color: #6c757d;">
        <p>© 2024 VinRetail Management System. All rights reserved.</p>
        <p>Made with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)
