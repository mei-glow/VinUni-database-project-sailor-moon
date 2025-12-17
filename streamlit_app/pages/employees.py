import streamlit as st
import pandas as pd
import io
from datetime import datetime
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
    tabs = st.tabs([
        "📋 Employee List", 
        "➕ Create Employee", 
        "📤 Bulk Upload",
        "🗑️ Bulk Delete"
    ])
    
    with tabs[0]:
        show_employee_list()
    
    with tabs[1]:
        if check_permission("EMPLOYEE_CREATE") or check_permission("SYSTEM_CONFIG"):
            show_create_employee()
        else:
            st.warning("⚠️ You don't have permission to create employees")
    
    with tabs[2]:
        if check_permission("EMPLOYEE_CREATE") or check_permission("SYSTEM_CONFIG"):
            show_bulk_upload()
        else:
            st.warning("⚠️ You don't have permission to upload employees")
    
    with tabs[3]:
        if check_permission("EMPLOYEE_DISABLE") or check_permission("SYSTEM_CONFIG"):
            show_bulk_delete()
        else:
            st.warning("⚠️ You don't have permission to delete employees")


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
                e.phone,
                e.role,
                d.department_name,
                e.job_description,
                e.hire_date,
                e.is_inactive,
                CONCAT(s.first_name, ' ', s.last_name) as supervisor_name
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.department_id
            LEFT JOIN employees s ON e.supervisor_id = s.employee_id
            ORDER BY e.employee_id DESC
        """)
        
        result = db.execute(query).fetchall()
        df = pd.DataFrame(result, columns=[
            'employee_id', 'first_name', 'last_name', 'email', 'gender',
            'phone', 'role', 'department_name', 'job_description', 'hire_date',
            'is_inactive', 'supervisor_name'
        ])
        
        if not df.empty:
            # Format data
            df['status'] = df['is_inactive'].apply(lambda x: '❌ Inactive' if x else '✅ Active')
            df['full_name'] = df['first_name'] + ' ' + df['last_name']
            
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search = st.text_input("🔍 Search", placeholder="Name, email, phone")
            
            with col2:
                role_filter = st.selectbox("Role", ["All"] + sorted(df['role'].dropna().unique().tolist()))
            
            with col3:
                status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])
            
            # Apply filters
            filtered_df = df.copy()
            
            if search:
                filtered_df = filtered_df[
                    filtered_df['full_name'].str.contains(search, case=False, na=False) |
                    filtered_df['email'].str.contains(search, case=False, na=False) |
                    filtered_df['phone'].str.contains(search, case=False, na=False)
                ]
            
            if role_filter != "All":
                filtered_df = filtered_df[filtered_df['role'] == role_filter]
            
            if status_filter == "Active":
                filtered_df = filtered_df[filtered_df['is_inactive'] == 0]
            elif status_filter == "Inactive":
                filtered_df = filtered_df[filtered_df['is_inactive'] == 1]
            
            # Display table
            st.dataframe(
                filtered_df[[
                    'employee_id', 'full_name', 'email', 'phone', 
                    'role', 'department_name', 'supervisor_name', 'hire_date', 'status'
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "employee_id": "ID",
                    "full_name": "Name",
                    "email": "Email",
                    "phone": "Phone",
                    "role": "Role",
                    "department_name": "Department",
                    "supervisor_name": "Supervisor",
                    "hire_date": st.column_config.DateColumn("Hire Date", format="DD/MM/YYYY"),
                    "status": "Status"
                }
            )
            
            st.info(f"📊 Showing {len(filtered_df)} of {len(df)} employees")
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total", len(df))
            with col2:
                st.metric("Active", len(df[df['is_inactive'] == 0]))
            with col3:
                st.metric("Inactive", len(df[df['is_inactive'] == 1]))
            with col4:
                st.metric("Managers", len(df[df['role'] == 'Manager']))
        
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
        # Get departments
        dept_query = text("SELECT department_id, department_name FROM departments ORDER BY department_name")
        depts = db.execute(dept_query).fetchall()
        dept_df = pd.DataFrame(depts, columns=['department_id', 'department_name'])
        
        # Get potential supervisors
        supervisor_query = text("""
            SELECT employee_id, CONCAT(first_name, ' ', last_name) as name
            FROM employees
            WHERE role IN ('Manager', 'Admin') AND is_inactive = 0
            ORDER BY first_name, last_name
        """)
        supervisors = db.execute(supervisor_query).fetchall()
        supervisor_df = pd.DataFrame(supervisors, columns=['employee_id', 'name'])
        
        with st.form("create_employee_form"):
            st.markdown("#### Personal Information")
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name *", placeholder="Nguyen")
                last_name = st.text_input("Last Name *", placeholder="Van A")
                email = st.text_input("Email *", placeholder="employee@company.com")
            
            with col2:
                phone = st.text_input("Phone *", placeholder="0912345678")
                gender = st.selectbox("Gender *", ["M", "F", "OTHER"])
                hire_date = st.date_input("Hire Date", value=datetime.now())
            
            st.markdown("#### Job Information")
            col1, col2 = st.columns(2)
            
            with col1:
                role = st.selectbox("Role *", ["Staff", "Warehouse", "Manager", "Delivery", "Admin"])
                department = st.selectbox("Department", ["None"] + dept_df['department_name'].tolist())
            
            with col2:
                supervisor = st.selectbox("Supervisor", ["None"] + supervisor_df['name'].tolist())
                job_description = st.text_area("Job Description", placeholder="Brief job description...")
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ Create Employee", use_container_width=True)
            with col2:
                if st.form_submit_button("🔄 Clear", use_container_width=True):
                    st.rerun()
            
            if submit:
                if not all([first_name, last_name, email, phone]):
                    st.error("❌ Please fill all required fields")
                else:
                    try:
                        dept_id = None
                        if department != "None":
                            dept_id = dept_df[dept_df['department_name'] == department]['department_id'].values[0]
                        
                        supervisor_id = None
                        if supervisor != "None":
                            supervisor_id = supervisor_df[supervisor_df['name'] == supervisor]['employee_id'].values[0]
                        
                        insert_query = text("""
                            INSERT INTO employees (
                                first_name, last_name, email, phone, gender, 
                                role, department_id, supervisor_id, job_description, hire_date
                            )
                            VALUES (:fn, :ln, :email, :phone, :gender, :role, :dept, :super, :job, :hire)
                        """)
                        
                        db.execute(insert_query, {
                            "fn": first_name.strip(),
                            "ln": last_name.strip(),
                            "email": email.strip(),
                            "phone": phone.strip(),
                            "gender": gender,
                            "role": role,
                            "dept": dept_id,
                            "super": supervisor_id,
                            "job": job_description.strip() if job_description else None,
                            "hire": hire_date
                        })
                        
                        db.commit()
                        st.success(f"✅ Employee '{first_name} {last_name}' created successfully!")
                        st.balloons()
                    
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()


def show_bulk_upload():
    """Bulk upload employees from CSV/Excel"""
    st.markdown("### 📤 Bulk Upload Employees")
    
    st.info("""
    **How to use:**
    1. Download the template file (CSV or Excel)
    2. Fill in employee data
    3. Upload the completed file
    4. Review and confirm
    """)
    
    # Get departments for reference
    db = get_db_connection()
    try:
        dept_query = text("SELECT department_name FROM departments ORDER BY department_name")
        depts = db.execute(dept_query).fetchall()
        dept_list = [d[0] for d in depts]
    except:
        dept_list = []
    finally:
        db.close()
    
    # Template generation
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📥 Download Template")
        
        # Create template DataFrame with CORRECT columns
        template_data = {
            'first_name': ['Nguyen', 'Tran'],
            'last_name': ['Van A', 'Thi B'],
            'email': ['nguyenvana@company.com', 'tranthib@company.com'],
            'phone': ['0912345678', '0987654321'],
            'gender': ['M', 'F'],
            'role': ['Staff', 'Manager'],
            'department_name': [dept_list[0] if dept_list else 'Sales', dept_list[0] if dept_list else 'Sales'],
            'job_description': ['Sales representative', 'Department manager'],
            'hire_date': ['2024-01-15', '2024-02-01']
        }
        
        template_df = pd.DataFrame(template_data)
        
        # Download buttons
        csv_buffer = io.StringIO()
        template_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📄 Download CSV Template",
            data=csv_buffer.getvalue(),
            file_name="employees_template.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            template_df.to_excel(writer, index=False, sheet_name='Employees')
        
        st.download_button(
            label="📊 Download Excel Template",
            data=excel_buffer.getvalue(),
            file_name="employees_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        # Show info
        st.markdown("**📋 Instructions:**")
        st.markdown("""
        - **role**: Must be one of: Staff, Warehouse, Manager, Delivery, Admin
        - **gender**: M, F, or OTHER
        - **hire_date**: Format YYYY-MM-DD (e.g., 2024-01-15)
        - **department_name**: Optional, must match existing department
        """)
        
        if dept_list:
            st.markdown("**Available Departments:**")
            st.code(", ".join(dept_list))
    
    with col2:
        st.markdown("#### 📤 Upload File")
        
        uploaded_file = st.file_uploader(
            "Choose CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload file with employee data"
        )
        
        if uploaded_file:
            try:
                # Read file
                if uploaded_file.name.endswith('.csv'):
                    upload_df = pd.read_csv(uploaded_file)
                else:
                    upload_df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ File loaded: {len(upload_df)} rows")
                
                # Validate columns
                required_cols = ['first_name', 'last_name', 'email', 'phone', 'gender', 'role']
                missing_cols = [col for col in required_cols if col not in upload_df.columns]
                
                if missing_cols:
                    st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                else:
                    # Preview data
                    st.markdown("#### 👀 Data Preview")
                    st.dataframe(upload_df.head(10), use_container_width=True)
                    
                    # Upload button
                    if st.button("✅ Upload Employees", type="primary", use_container_width=True):
                        db = get_db_connection()
                        try:
                            success_count = 0
                            error_count = 0
                            errors = []
                            
                            for idx, row in upload_df.iterrows():
                                try:
                                    # Get department_id if specified
                                    dept_id = None
                                    if 'department_name' in row and pd.notna(row['department_name']):
                                        dept_query = text("""
                                            SELECT department_id FROM departments 
                                            WHERE department_name = :name
                                        """)
                                        dept_result = db.execute(dept_query, {"name": row['department_name']}).fetchone()
                                        if dept_result:
                                            dept_id = dept_result[0]
                                    
                                    # Insert employee
                                    insert_query = text("""
                                        INSERT INTO employees (
                                            first_name, last_name, email, phone, gender,
                                            role, department_id, job_description, hire_date
                                        )
                                        VALUES (:fn, :ln, :email, :phone, :gender, :role, :dept, :job, :hire)
                                    """)
                                    
                                    db.execute(insert_query, {
                                        "fn": row['first_name'],
                                        "ln": row['last_name'],
                                        "email": row['email'],
                                        "phone": row['phone'],
                                        "gender": row['gender'],
                                        "role": row['role'],
                                        "dept": dept_id,
                                        "job": row.get('job_description', None),
                                        "hire": row.get('hire_date', datetime.now().date())
                                    })
                                    
                                    success_count += 1
                                
                                except Exception as e:
                                    error_count += 1
                                    errors.append(f"Row {idx + 2}: {str(e)}")
                            
                            db.commit()
                            
                            st.success(f"✅ Successfully uploaded {success_count} employees")
                            
                            if error_count > 0:
                                st.warning(f"⚠️ {error_count} rows failed")
                                with st.expander("View Errors"):
                                    for error in errors[:20]:  # Show first 20 errors
                                        st.error(error)
                            
                            st.balloons()
                        
                        except Exception as e:
                            db.rollback()
                            st.error(f"❌ Upload failed: {str(e)}")
                        
                        finally:
                            db.close()
            
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")


def show_bulk_delete():
    """Bulk delete employees"""
    st.markdown("### 🗑️ Bulk Delete Employees")
    
    st.warning("⚠️ **Warning:** This will mark employees as inactive (soft delete)")
    
    db = get_db_connection()
    
    try:
        # Get all active employees
        query = text("""
            SELECT 
                e.employee_id,
                CONCAT(e.first_name, ' ', e.last_name) as full_name,
                e.email,
                e.phone,
                e.role,
                d.department_name
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.department_id
            WHERE e.is_inactive = 0
            ORDER BY e.first_name, e.last_name
        """)
        
        result = db.execute(query).fetchall()
        df = pd.DataFrame(result, columns=[
            'employee_id', 'full_name', 'email', 'phone', 'role', 'department_name'
        ])
        
        if df.empty:
            st.info("No active employees to delete")
            return
        
        st.info(f"📊 Total active employees: {len(df)}")
        
        # Selection method
        method = st.radio("Select deletion method:", ["Select from list", "Upload CSV with IDs"])
        
        if method == "Select from list":
            # Multi-select from dataframe
            st.markdown("#### Select employees to delete:")
            
            # Add checkbox column
            df['select'] = False
            
            # Display editable dataframe
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "select": st.column_config.CheckboxColumn("Select", default=False),
                    "employee_id": "ID",
                    "full_name": "Name",
                    "email": "Email",
                    "phone": "Phone",
                    "role": "Role",
                    "department_name": "Department"
                },
                disabled=["employee_id", "full_name", "email", "phone", "role", "department_name"]
            )
            
            selected = edited_df[edited_df['select'] == True]
            
            if len(selected) > 0:
                st.warning(f"⚠️ You have selected **{len(selected)}** employees to delete")
                
                if st.button("🗑️ Delete Selected Employees", type="primary"):
                    try:
                        delete_query = text("""
                            UPDATE employees
                            SET is_inactive = 1, last_modified = NOW()
                            WHERE employee_id IN :ids
                        """)
                        
                        employee_ids = tuple(selected['employee_id'].tolist())
                        db.execute(delete_query, {"ids": employee_ids})
                        db.commit()
                        
                        st.success(f"✅ Successfully deleted {len(selected)} employees")
                        st.balloons()
                        st.rerun()
                    
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error: {str(e)}")
        
        else:
            # Upload CSV with employee IDs
            st.markdown("#### Upload CSV with Employee IDs")
            
            # Template for deletion
            delete_template = pd.DataFrame({
                'employee_id': df['employee_id'].head(5).tolist()
            })
            
            csv_buffer = io.StringIO()
            delete_template.to_csv(csv_buffer, index=False)
            
            st.download_button(
                label="📄 Download ID Template",
                data=csv_buffer.getvalue(),
                file_name="employees_delete_template.csv",
                mime="text/csv"
            )
            
            uploaded_file = st.file_uploader("Upload CSV with employee_id column", type=['csv'])
            
            if uploaded_file:
                try:
                    delete_df = pd.read_csv(uploaded_file)
                    
                    if 'employee_id' not in delete_df.columns:
                        st.error("❌ CSV must have 'employee_id' column")
                    else:
                        ids_to_delete = delete_df['employee_id'].tolist()
                        st.warning(f"⚠️ Will delete **{len(ids_to_delete)}** employees")
                        
                        # Show preview
                        preview = df[df['employee_id'].isin(ids_to_delete)]
                        st.dataframe(preview, use_container_width=True, hide_index=True)
                        
                        if st.button("🗑️ Confirm Deletion", type="primary"):
                            try:
                                delete_query = text("""
                                    UPDATE employees
                                    SET is_inactive = 1, last_modified = NOW()
                                    WHERE employee_id IN :ids
                                """)
                                
                                db.execute(delete_query, {"ids": tuple(ids_to_delete)})
                                db.commit()
                                
                                st.success(f"✅ Successfully deleted {len(ids_to_delete)} employees")
                                st.balloons()
                                st.rerun()
                            
                            except Exception as e:
                                db.rollback()
                                st.error(f"❌ Error: {str(e)}")
                
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()