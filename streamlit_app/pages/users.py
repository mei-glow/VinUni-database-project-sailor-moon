import streamlit as st
import pandas as pd
from sqlalchemy import text
from passlib.context import CryptContext
from config.session import get_db_connection
from utils.auth import check_permission

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def show():
    """Display users management page"""
    
    st.markdown("""
        <div class="main-header">
            <h1>👥 Users Management</h1>
            <p>Manage system users and their roles</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check permissions
    if not check_permission("USER_VIEW"):
        st.error("⛔ You don't have permission to view users")
        return
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 User List", "➕ Create User", "🔍 User Details"])
    
    with tab1:
        show_user_list()
    
    with tab2:
        if check_permission("USER_CREATE"):
            show_create_user()
        else:
            st.warning("⚠️ You don't have permission to create users")
    
    with tab3:
        show_user_details()

def show_user_list():
    """Display list of users"""
    st.markdown("### 📋 All Users")
    
    db = get_db_connection()
    
    try:
        query = text("""
            SELECT 
                u.user_id,
                u.username,
                u.email,
                u.is_active,
                u.created_at,
                GROUP_CONCAT(r.role_name) as roles
            FROM users u
            LEFT JOIN user_roles ur ON u.user_id = ur.user_id
            LEFT JOIN roles r ON ur.role_id = r.role_id
            GROUP BY u.user_id
            ORDER BY u.user_id DESC
        """)
        
        result = db.execute(query).fetchall()
        users_df = pd.DataFrame(result, columns=['user_id', 'username', 'email', 'is_active', 'created_at', 'roles'])
        
        if not users_df.empty:
            # Format data
            users_df['status'] = users_df['is_active'].apply(
                lambda x: '✅ Active' if x else '❌ Inactive'
            )
            
            # Search filter
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                search = st.text_input("🔍 Search by username or email", "")
            with col2:
                status_filter = st.selectbox("Filter by status", ["All", "Active", "Inactive"])
            with col3:
                st.write("")
                st.write("")
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
            
            # Apply filters
            filtered_df = users_df.copy()
            
            if search:
                filtered_df = filtered_df[
                    filtered_df['username'].str.contains(search, case=False, na=False) |
                    filtered_df['email'].str.contains(search, case=False, na=False)
                ]
            
            if status_filter == "Active":
                filtered_df = filtered_df[filtered_df['is_active'] == 1]
            elif status_filter == "Inactive":
                filtered_df = filtered_df[filtered_df['is_active'] == 0]
            
            # Display table
            st.dataframe(
                filtered_df[['user_id', 'username', 'email', 'roles', 'status', 'created_at']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "user_id": "ID",
                    "username": "Username",
                    "email": "Email",
                    "roles": "Roles",
                    "status": "Status",
                    "created_at": st.column_config.DatetimeColumn(
                        "Created At",
                        format="DD/MM/YYYY HH:mm"
                    )
                }
            )
            
            st.info(f"📊 Total users: {len(filtered_df)} / {len(users_df)}")
            
        else:
            st.info("No users found in the system")
    
    except Exception as e:
        st.error(f"❌ Error loading users: {str(e)}")
    
    finally:
        db.close()

def show_create_user():
    """Create new user form"""
    st.markdown("### ➕ Create New User")
    
    db = get_db_connection()
    
    try:
        # Get available roles
        roles_query = text("SELECT role_id, role_name, description FROM roles ORDER BY role_name")
        result = db.execute(roles_query).fetchall()
        roles_df = pd.DataFrame(result, columns=['role_id', 'role_name', 'description'])
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("👤 Username *", placeholder="Enter username")
                email = st.text_input("📧 Email *", placeholder="user@example.com")
            
            with col2:
                password = st.text_input("🔑 Password *", type="password", placeholder="Min 6 characters")
                confirm_password = st.text_input("🔑 Confirm Password *", type="password")
            
            role = st.selectbox(
                "🎭 Role *",
                options=roles_df['role_name'].tolist(),
                help="Select user role"
            )
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ Create User", use_container_width=True)
            with col2:
                if st.form_submit_button("🔄 Clear", use_container_width=True):
                    st.rerun()
            
            if submit:
                # Validation
                errors = []
                
                if not username or len(username) < 3:
                    errors.append("Username must be at least 3 characters")
                
                if not email or "@" not in email:
                    errors.append("Valid email is required")
                
                if not password or len(password) < 6:
                    errors.append("Password must be at least 6 characters")
                
                if password != confirm_password:
                    errors.append("Passwords do not match")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    # Check if username exists
                    check_query = text("SELECT 1 FROM users WHERE username = :u")
                    exists = db.execute(check_query, {"u": username}).fetchone()
                    
                    if exists:
                        st.error("❌ Username already exists")
                    else:
                        try:
                            # Hash password
                            hashed = pwd_context.hash(password)
                            
                            # Create user
                            create_query = text("""
                                INSERT INTO users (username, email, password_hash, is_active)
                                VALUES (:u, :e, :p, 1)
                            """)
                            
                            result = db.execute(create_query, {
                                "u": username,
                                "e": email,
                                "p": hashed
                            })
                            
                            user_id = result.lastrowid
                            
                            # Assign role
                            role_query = text("""
                                INSERT INTO user_roles (user_id, role_id)
                                SELECT :uid, role_id FROM roles WHERE role_name = :r
                            """)
                            
                            db.execute(role_query, {"uid": user_id, "r": role})
                            db.commit()
                            
                            st.success(f"✅ User '{username}' created successfully!")
                            st.balloons()
                            
                        except Exception as e:
                            db.rollback()
                            st.error(f"❌ Error creating user: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()

def show_user_details():
    """Show user details and allow updates"""
    st.markdown("### 🔍 User Details & Management")
    
    db = get_db_connection()
    
    try:
        # Get all users for selection
        users_query = text("""
            SELECT user_id, username, email
            FROM users
            ORDER BY username
        """)
        result = db.execute(users_query).fetchall()
        users_df = pd.DataFrame(result, columns=['user_id', 'username', 'email'])
        
        if users_df.empty:
            st.info("No users available")
            return
        
        # Select user
        selected_user = st.selectbox(
            "Select User",
            options=users_df['username'].tolist(),
            format_func=lambda x: f"{x} ({users_df[users_df['username']==x]['email'].values[0]})"
        )
        
        if selected_user:
            user_id = users_df[users_df['username'] == selected_user]['user_id'].values[0]
            
            # Get user details
            detail_query = text("""
                SELECT 
                    u.user_id,
                    u.username,
                    u.email,
                    u.is_active,
                    u.created_at,
                    GROUP_CONCAT(r.role_name) as roles
                FROM users u
                LEFT JOIN user_roles ur ON u.user_id = ur.user_id
                LEFT JOIN roles r ON ur.role_id = r.role_id
                WHERE u.user_id = :uid
                GROUP BY u.user_id
            """)
            
            user = db.execute(detail_query, {"uid": user_id}).fetchone()
            
            if user:
                # Display user info
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("User ID", user.user_id)
                with col2:
                    st.metric("Status", "✅ Active" if user.is_active else "❌ Inactive")
                with col3:
                    st.metric("Roles", user.roles if user.roles else "None")
                
                st.markdown("---")
                
                # Update form
                if check_permission("USER_UPDATE"):
                    with st.form("update_user_form"):
                        st.markdown("#### Update User Information")
                        
                        new_email = st.text_input("📧 Email", value=user.email)
                        
                        # Get available roles
                        roles_query = text("SELECT role_name FROM roles ORDER BY role_name")
                        result = db.execute(roles_query).fetchall()
                        roles_df = pd.DataFrame(result, columns=['role_name'])
                        
                        current_roles = user.roles.split(',') if user.roles else []
                        new_role = st.selectbox("🎭 Role", options=roles_df['role_name'].tolist(), 
                                              index=roles_df['role_name'].tolist().index(current_roles[0]) if current_roles else 0)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            update_submit = st.form_submit_button("💾 Update User", use_container_width=True)
                        
                        with col2:
                            if check_permission("USER_DISABLE"):
                                disable_submit = st.form_submit_button(
                                    "🚫 Disable User" if user.is_active else "✅ Enable User",
                                    use_container_width=True
                                )
                            else:
                                disable_submit = False
                        
                        if update_submit:
                            try:
                                # Update email
                                update_query = text("UPDATE users SET email = :e WHERE user_id = :uid")
                                db.execute(update_query, {"e": new_email, "uid": user_id})
                                
                                # Update role
                                delete_roles = text("DELETE FROM user_roles WHERE user_id = :uid")
                                db.execute(delete_roles, {"uid": user_id})
                                
                                insert_role = text("""
                                    INSERT INTO user_roles (user_id, role_id)
                                    SELECT :uid, role_id FROM roles WHERE role_name = :r
                                """)
                                db.execute(insert_role, {"uid": user_id, "r": new_role})
                                
                                db.commit()
                                st.success("✅ User updated successfully!")
                                st.rerun()
                            
                            except Exception as e:
                                db.rollback()
                                st.error(f"❌ Error updating user: {str(e)}")
                        
                        if disable_submit:
                            try:
                                new_status = 0 if user.is_active else 1
                                status_query = text("UPDATE users SET is_active = :s WHERE user_id = :uid")
                                db.execute(status_query, {"s": new_status, "uid": user_id})
                                db.commit()
                                
                                st.success(f"✅ User {'disabled' if user.is_active else 'enabled'} successfully!")
                                st.rerun()
                            
                            except Exception as e:
                                db.rollback()
                                st.error(f"❌ Error: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()