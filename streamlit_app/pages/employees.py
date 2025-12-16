import streamlit as st
import pandas as pd
from sqlalchemy import text
from config.session import get_db_connection
from utils.auth import check_permission

def show():
    """Display employees management page"""
    
    st.markdown("""
        <div class="main-header">
            <h1>👨‍💼 Employees Management</h1>
            <p>Manage employee records and information</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check permissions
    if not check_permission("EMPLOYEE_VIEW") and not check_permission("SYSTEM_CONFIG"):
        st.error("⛔ You don't have permission to view employees")
        return
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Employee List", "➕ Create Employee", "🔍 Employee Details"])
    
    with tab1:
        show_employee_list()
    
    with tab2:
        if check_permission("EMPLOYEE_CREATE") or check_permission("SYSTEM_CONFIG"):
            show_create_employee()
        else:
            st.warning("⚠️ You don't have permission to create employees")
    
    with tab3:
        show_employee_details()

def show_employee_list():
    """Display list of employees"""
    st.markdown("### 📋 All Employees")
    
    db = get_db_connection()
    
    try:
        query = text("""
            SELECT 
                e.employee_id,
                e.first_name,
                e.last_name,
                e.email,
                e.gender,
                e.role,
                e.phone,
                e.is_inactive,
                d.department_name,
                CONCAT(s.first_name, ' ', s.last_name) as supervisor_name
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.department_id
            LEFT JOIN employees s ON e.supervisor_id = s.employee_id
            ORDER BY e.employee_id DESC
        """)
        
        result = db.execute(query).fetchall()
        employees_df = pd.DataFrame(result, columns=[
            'employee_id', 'first_name', 'last_name', 'email', 'gender', 
            'role', 'phone', 'is_inactive', 'department_name', 'supervisor_name'
        ])
        
        if not employees_df.empty:
            # Format data
            employees_df['full_name'] = employees_df['first_name'] + ' ' + employees_df['last_name']
            employees_df['status'] = employees_df['is_inactive'].apply(
                lambda x: '❌ Inactive' if x else '✅ Active'
            )
            
            # Filters
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                search = st.text_input("🔍 Search", placeholder="Name or email")
            
            with col2:
                role_filter = st.selectbox("Role", ["All"] + employees_df['role'].unique().tolist())
            
            with col3:
                dept_filter = st.selectbox("Department", ["All"] + employees_df['department_name'].dropna().unique().tolist())
            
            with col4:
                status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])
            
            # Apply filters
            filtered_df = employees_df.copy()
            
            if search:
                filtered_df = filtered_df[
                    filtered_df['full_name'].str.contains(search, case=False, na=False) |
                    filtered_df['email'].str.contains(search, case=False, na=False)
                ]
            
            if role_filter != "All":
                filtered_df = filtered_df[filtered_df['role'] == role_filter]
            
            if dept_filter != "All":
                filtered_df = filtered_df[filtered_df['department_name'] == dept_filter]
            
            if status_filter == "Active":
                filtered_df = filtered_df[filtered_df['is_inactive'] == 0]
            elif status_filter == "Inactive":
                filtered_df = filtered_df[filtered_df['is_inactive'] == 1]
            
            # Display table
            st.dataframe(
                filtered_df[[
                    'employee_id', 'full_name', 'email', 'gender', 
                    'role', 'department_name', 'phone', 'supervisor_name', 'status'
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "employee_id": "ID",
                    "full_name": "Name",
                    "email": "Email",
                    "gender": "Gender",
                    "role": "Role",
                    "department_name": "Department",
                    "phone": "Phone",
                    "supervisor_name": "Supervisor",
                    "status": "Status"
                }
            )
            
            st.info(f"📊 Showing {len(filtered_df)} of {len(employees_df)} employees")
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Employees", len(employees_df))
            with col2:
                st.metric("Active", len(employees_df[employees_df['is_inactive'] == 0]))
            with col3:
                st.metric("Departments", employees_df['department_name'].nunique())
            with col4:
                st.metric("Roles", employees_df['role'].nunique())
        
        else:
            st.info("No employees found")
    
    except Exception as e:
        st.error(f"❌ Error loading employees: {str(e)}")
    
    finally:
        db.close()

def show_create_employee():
    """Create new employee form"""
    st.markdown("### ➕ Create New Employee")
    
    db = get_db_connection()
    
    try:
        # Get departments and supervisors
        dept_query = text("SELECT department_id, department_name FROM departments ORDER BY department_name")
        result = db.execute(dept_query).fetchall()
        departments = pd.DataFrame(result, columns=['department_id', 'department_name'])
        
        supervisor_query = text("""
            SELECT employee_id, CONCAT(first_name, ' ', last_name) as name
            FROM employees
            WHERE is_inactive = 0
            ORDER BY first_name, last_name
        """)
        result = db.execute(supervisor_query).fetchall()
        supervisors = pd.DataFrame(result, columns=['employee_id', 'name'])
        
        with st.form("create_employee_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("👤 First Name *", placeholder="John")
                last_name = st.text_input("👤 Last Name *", placeholder="Doe")
                email = st.text_input("📧 Email *", placeholder="john.doe@vinretail.com")
                phone = st.text_input("📱 Phone", placeholder="+84 xxx xxx xxx")
            
            with col2:
                gender = st.selectbox("⚥ Gender *", ["M", "F", "OTHER"])
                role = st.selectbox("💼 Role *", ["Staff", "Warehouse", "Manager", "Delivery", "Admin"])
                
                department = st.selectbox(
                    "🏢 Department *",
                    options=departments['department_name'].tolist(),
                    help="Select employee department"
                )
                
                supervisor = st.selectbox(
                    "👔 Supervisor",
                    options=["None"] + supervisors['name'].tolist(),
                    help="Select direct supervisor (optional)"
                )
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ Create Employee", use_container_width=True)
            with col2:
                if st.form_submit_button("🔄 Clear", use_container_width=True):
                    st.rerun()
            
            if submit:
                # Validation
                if not all([first_name, last_name, email, department]):
                    st.error("❌ Please fill all required fields")
                else:
                    try:
                        # Get department_id
                        dept_id = departments[departments['department_name'] == department]['department_id'].values[0]
                        
                        # Get supervisor_id if selected
                        supervisor_id = None
                        if supervisor != "None":
                            supervisor_id = supervisors[supervisors['name'] == supervisor]['employee_id'].values[0]
                        
                        # Create employee
                        create_query = text("""
                            INSERT INTO employees (
                                first_name, last_name, email, gender,
                                department_id, role, phone, supervisor_id
                            )
                            VALUES (:fn, :ln, :e, :g, :d, :r, :p, :s)
                        """)
                        
                        db.execute(create_query, {
                            "fn": first_name,
                            "ln": last_name,
                            "e": email,
                            "g": gender,
                            "d": dept_id,
                            "r": role,
                            "p": phone if phone else None,
                            "s": supervisor_id
                        })
                        
                        db.commit()
                        st.success(f"✅ Employee '{first_name} {last_name}' created successfully!")
                        st.balloons()
                    
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error creating employee: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()

def show_employee_details():
    """Show employee details and allow updates"""
    st.markdown("### 🔍 Employee Details & Management")
    
    db = get_db_connection()
    
    try:
        # Get all employees for selection
        emp_query = text("""
            SELECT employee_id, CONCAT(first_name, ' ', last_name) as name, email
            FROM employees
            ORDER BY first_name, last_name
        """)
        result = db.execute(emp_query).fetchall()
        employees = pd.DataFrame(result, columns=['employee_id', 'name', 'email'])
        
        if employees.empty:
            st.info("No employees available")
            return
        
        # Select employee
        selected_emp = st.selectbox(
            "Select Employee",
            options=employees['name'].tolist(),
            format_func=lambda x: f"{x} ({employees[employees['name']==x]['email'].values[0]})"
        )
        
        if selected_emp:
            emp_id = employees[employees['name'] == selected_emp]['employee_id'].values[0]
            
            # Get employee details
            detail_query = text("""
                SELECT 
                    e.*,
                    d.department_name,
                    CONCAT(s.first_name, ' ', s.last_name) as supervisor_name
                FROM employees e
                LEFT JOIN departments d ON e.department_id = d.department_id
                LEFT JOIN employees s ON e.supervisor_id = s.employee_id
                WHERE e.employee_id = :eid
            """)
            
            emp = db.execute(detail_query, {"eid": emp_id}).fetchone()
            
            if emp:
                # Display employee info
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Employee ID", emp.employee_id)
                with col2:
                    st.metric("Role", emp.role)
                with col3:
                    st.metric("Department", emp.department_name)
                with col4:
                    st.metric("Status", "✅ Active" if not emp.is_inactive else "❌ Inactive")
                
                st.markdown("---")
                
                # Update form
                if check_permission("EMPLOYEE_UPDATE") or check_permission("SYSTEM_CONFIG"):
                    with st.form("update_employee_form"):
                        st.markdown("#### Update Employee Information")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_email = st.text_input("📧 Email", value=emp.email)
                            new_phone = st.text_input("📱 Phone", value=emp.phone or "")
                        
                        with col2:
                            new_role = st.selectbox(
                                "💼 Role",
                                ["Staff", "Warehouse", "Manager", "Delivery", "Admin"],
                                index=["Staff", "Warehouse", "Manager", "Delivery", "Admin"].index(emp.role)
                            )
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            update_submit = st.form_submit_button("💾 Update Employee", use_container_width=True)
                        
                        with col2:
                            if check_permission("EMPLOYEE_DISABLE") or check_permission("SYSTEM_CONFIG"):
                                disable_submit = st.form_submit_button(
                                    "🚫 Disable" if not emp.is_inactive else "✅ Enable",
                                    use_container_width=True
                                )
                            else:
                                disable_submit = False
                        
                        if update_submit:
                            try:
                                update_query = text("""
                                    UPDATE employees
                                    SET email = :e, phone = :p, role = :r
                                    WHERE employee_id = :eid
                                """)
                                
                                db.execute(update_query, {
                                    "e": new_email,
                                    "p": new_phone if new_phone else None,
                                    "r": new_role,
                                    "eid": emp_id
                                })
                                
                                db.commit()
                                st.success("✅ Employee updated successfully!")
                                st.rerun()
                            
                            except Exception as e:
                                db.rollback()
                                st.error(f"❌ Error updating employee: {str(e)}")
                        
                        if disable_submit:
                            try:
                                new_status = 1 if not emp.is_inactive else 0
                                status_query = text("""
                                    UPDATE employees
                                    SET is_inactive = :s
                                    WHERE employee_id = :eid
                                """)
                                
                                db.execute(status_query, {"s": new_status, "eid": emp_id})
                                db.commit()
                                
                                st.success(f"✅ Employee {'disabled' if not emp.is_inactive else 'enabled'} successfully!")
                                st.rerun()
                            
                            except Exception as e:
                                db.rollback()
                                st.error(f"❌ Error: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()