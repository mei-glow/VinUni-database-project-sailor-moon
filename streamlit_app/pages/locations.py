import streamlit as st
import pandas as pd
import io
from datetime import datetime
from sqlalchemy import text
from config.session import get_db_connection
from utils.auth import check_permission

def show():
    """Display locations management page"""
    
    st.markdown("""
        <div class="main-header">
            <h1>📍 Locations Management</h1>
            <p>Manage stores and warehouse locations</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check permissions
    if not check_permission("SYSTEM_CONFIG"):
        st.error("⛔ You don't have permission to manage locations")
        return
    
    # Tabs
    tabs = st.tabs([
        "📋 Location List",
        "➕ Create Location",
        "📤 Bulk Upload",
        "🗑️ Bulk Delete"
    ])
    
    with tabs[0]:
        show_location_list()
    
    with tabs[1]:
        show_create_location()
    
    with tabs[2]:
        show_bulk_upload()
    
    with tabs[3]:
        show_bulk_delete()


def show_location_list():
    """Display list of locations"""
    st.markdown("### 📋 All Locations")
    
    db = get_db_connection()
    
    try:
        query = text("""
            SELECT 
                l.location_id,
                l.location_name,
                l.location_type,
                l.address,
                l.city,
                l.region,
                l.channel,
                l.email,
                l.opening_date,
                l.close_date,
                CONCAT(e.first_name, ' ', e.last_name) as manager_name
            FROM locations l
            LEFT JOIN employees e ON l.store_manager_id = e.employee_id
            ORDER BY l.location_id DESC
        """)
        
        result = db.execute(query).fetchall()
        df = pd.DataFrame(result, columns=[
            'location_id', 'location_name', 'location_type', 'address',
            'city', 'region', 'channel', 'email', 'opening_date', 'close_date', 'manager_name'
        ])
        
        if not df.empty:
            # Format data
            df['status'] = df['close_date'].apply(
                lambda x: '❌ Closed' if pd.notna(x) else '✅ Active'
            )
            
            # Filters
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                search = st.text_input("🔍 Search", placeholder="Location name")
            
            with col2:
                type_filter = st.selectbox("Type", ["All", "STORE", "WAREHOUSE"])
            
            with col3:
                region_filter = st.selectbox("Region", ["All", "North", "South"])
            
            with col4:
                status_filter = st.selectbox("Status", ["All", "Active", "Closed"])
            
            # Apply filters
            filtered_df = df.copy()
            
            if search:
                filtered_df = filtered_df[
                    filtered_df['location_name'].str.contains(search, case=False, na=False)
                ]
            
            if type_filter != "All":
                filtered_df = filtered_df[filtered_df['location_type'] == type_filter]
            
            if region_filter != "All":
                filtered_df = filtered_df[filtered_df['region'] == region_filter]
            
            if status_filter == "Active":
                filtered_df = filtered_df[filtered_df['close_date'].isna()]
            elif status_filter == "Closed":
                filtered_df = filtered_df[filtered_df['close_date'].notna()]
            
            # Display table
            st.dataframe(
                filtered_df[[
                    'location_id', 'location_name', 'location_type',
                    'city', 'region', 'channel', 'manager_name', 'status'
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "location_id": "ID",
                    "location_name": "Name",
                    "location_type": "Type",
                    "city": "City",
                    "region": "Region",
                    "channel": "Channel",
                    "manager_name": "Manager",
                    "status": "Status"
                }
            )
            
            st.info(f"📊 Showing {len(filtered_df)} of {len(df)} locations")
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total", len(df))
            with col2:
                st.metric("Stores", len(df[df['location_type'] == 'STORE']))
            with col3:
                st.metric("Warehouses", len(df[df['location_type'] == 'WAREHOUSE']))
            with col4:
                st.metric("Active", len(df[df['close_date'].isna()]))
        
        else:
            st.info("No locations found")
    
    except Exception as e:
        st.error(f"❌ Error loading locations: {str(e)}")
    
    finally:
        db.close()


def show_create_location():
    """Create new location form"""
    st.markdown("### ➕ Create New Location")
    
    db = get_db_connection()
    
    try:
        # Get managers
        managers_query = text("""
            SELECT employee_id, CONCAT(first_name, ' ', last_name) as name
            FROM employees
            WHERE role = 'Manager' AND is_inactive = 0
            ORDER BY first_name, last_name
        """)
        managers = db.execute(managers_query).fetchall()
        managers_df = pd.DataFrame(managers, columns=['employee_id', 'name'])
        
        with st.form("create_location_form"):
            st.markdown("#### Basic Information")
            col1, col2 = st.columns(2)
            
            with col1:
                location_name = st.text_input("Location Name *", placeholder="VinRetail Store HN01")
                location_type = st.selectbox("Type *", ["STORE", "WAREHOUSE"])
                city = st.text_input("City *", placeholder="Hanoi")
            
            with col2:
                region = st.selectbox("Region *", ["North", "South"])
                channel = st.selectbox("Channel", ["Online", "Offline", "Ecommerce", "Warehouse"])
                email = st.text_input("Email", placeholder="location@vinretail.com")
            
            st.markdown("#### Address & Details")
            col1, col2 = st.columns(2)
            
            with col1:
                address = st.text_area("Address", placeholder="Full address")
                manager = st.selectbox(
                    "Store Manager",
                    ["None"] + managers_df['name'].tolist() if not managers_df.empty else ["None"]
                )
            
            with col2:
                opening_date = st.date_input("Opening Date", value=datetime.now())
                st.info("💡 Leave close_date empty for active locations")
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ Create Location", use_container_width=True)
            with col2:
                if st.form_submit_button("🔄 Clear", use_container_width=True):
                    st.rerun()
            
            if submit:
                if not all([location_name, location_type, city, region]):
                    st.error("❌ Please fill all required fields")
                else:
                    try:
                        manager_id = None
                        if manager != "None" and not managers_df.empty:
                            manager_id = managers_df[managers_df['name'] == manager]['employee_id'].values[0]
                        
                        insert_query = text("""
                            INSERT INTO locations (
                                location_name, location_type, address, city, region,
                                channel, email, store_manager_id, opening_date
                            )
                            VALUES (:name, :type, :addr, :city, :region, :channel, :email, :mgr, :open)
                        """)
                        
                        db.execute(insert_query, {
                            "name": location_name.strip(),
                            "type": location_type,
                            "addr": address.strip() if address else None,
                            "city": city.strip(),
                            "region": region,
                            "channel": channel,
                            "email": email.strip() if email else None,
                            "mgr": manager_id,
                            "open": opening_date
                        })
                        
                        db.commit()
                        st.success(f"✅ Location '{location_name}' created successfully!")
                        st.balloons()
                    
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()


def show_bulk_upload():
    """Bulk upload locations from CSV/Excel"""
    st.markdown("### 📤 Bulk Upload Locations")
    
    st.info("""
    **How to use:**
    1. Download the template file
    2. Fill in location data
    3. Upload the completed file
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📥 Download Template")
        
        # Create template
        template_data = {
            'location_name': ['VinRetail Store HN01', 'VinRetail Warehouse HN'],
            'location_type': ['STORE', 'WAREHOUSE'],
            'address': ['123 ABC Street', '456 XYZ Avenue'],
            'city': ['Hanoi', 'Hanoi'],
            'region': ['North', 'North'],
            'channel': ['Offline', 'Warehouse'],
            'email': ['hn01@vinretail.com', 'warehouse@vinretail.com'],
            'opening_date': ['2024-01-15', '2024-02-01']
        }
        
        template_df = pd.DataFrame(template_data)
        
        # CSV Download
        csv_buffer = io.StringIO()
        template_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📄 Download CSV Template",
            data=csv_buffer.getvalue(),
            file_name="locations_template.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Excel Download
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            template_df.to_excel(writer, index=False, sheet_name='Locations')
        
        st.download_button(
            label="📊 Download Excel Template",
            data=excel_buffer.getvalue(),
            file_name="locations_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        st.markdown("**📋 Field Info:**")
        st.markdown("""
        - **location_type**: STORE or WAREHOUSE
        - **region**: North or South
        - **channel**: Online, Offline, Ecommerce, Warehouse
        - **opening_date**: YYYY-MM-DD format
        """)
    
    with col2:
        st.markdown("#### 📤 Upload File")
        
        uploaded_file = st.file_uploader(
            "Choose CSV or Excel file",
            type=['csv', 'xlsx', 'xls']
        )
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    upload_df = pd.read_csv(uploaded_file)
                else:
                    upload_df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ File loaded: {len(upload_df)} rows")
                
                # Validate
                required_cols = ['location_name', 'location_type', 'city', 'region']
                missing_cols = [col for col in required_cols if col not in upload_df.columns]
                
                if missing_cols:
                    st.error(f"❌ Missing columns: {', '.join(missing_cols)}")
                else:
                    st.dataframe(upload_df.head(10), use_container_width=True)
                    
                    if st.button("✅ Upload Locations", type="primary", use_container_width=True):
                        db = get_db_connection()
                        try:
                            success_count = 0
                            error_count = 0
                            errors = []
                            
                            for idx, row in upload_df.iterrows():
                                try:
                                    insert_query = text("""
                                        INSERT INTO locations (
                                            location_name, location_type, address, city, region,
                                            channel, email, opening_date
                                        )
                                        VALUES (:name, :type, :addr, :city, :region, :channel, :email, :open)
                                    """)
                                    
                                    db.execute(insert_query, {
                                        "name": row['location_name'],
                                        "type": row['location_type'],
                                        "addr": row.get('address', None),
                                        "city": row['city'],
                                        "region": row['region'],
                                        "channel": row.get('channel', 'Offline'),
                                        "email": row.get('email', None),
                                        "open": row.get('opening_date', datetime.now().date())
                                    })
                                    
                                    success_count += 1
                                
                                except Exception as e:
                                    error_count += 1
                                    errors.append(f"Row {idx + 2}: {str(e)}")
                            
                            db.commit()
                            st.success(f"✅ Uploaded {success_count} locations")
                            
                            if error_count > 0:
                                st.warning(f"⚠️ {error_count} failed")
                                with st.expander("Errors"):
                                    for error in errors[:20]:
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
    """Bulk delete locations (soft delete via close_date)"""
    st.markdown("### 🗑️ Bulk Delete Locations")
    
    st.warning("⚠️ **Warning:** This will mark locations as closed")
    
    db = get_db_connection()
    
    try:
        query = text("""
            SELECT 
                l.location_id,
                l.location_name,
                l.location_type,
                l.city,
                l.region
            FROM locations l
            WHERE l.close_date IS NULL
            ORDER BY l.location_name
        """)
        
        result = db.execute(query).fetchall()
        df = pd.DataFrame(result, columns=[
            'location_id', 'location_name', 'location_type', 'city', 'region'
        ])
        
        if df.empty:
            st.info("No active locations to delete")
            return
        
        st.info(f"📊 Total active locations: {len(df)}")
        
        method = st.radio("Select method:", ["Select from list", "Upload CSV with IDs"])
        
        if method == "Select from list":
            df['select'] = False
            
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "select": st.column_config.CheckboxColumn("Select", default=False),
                    "location_id": "ID",
                    "location_name": "Name",
                    "location_type": "Type",
                    "city": "City",
                    "region": "Region"
                },
                disabled=["location_id", "location_name", "location_type", "city", "region"]
            )
            
            selected = edited_df[edited_df['select'] == True]
            
            if len(selected) > 0:
                st.warning(f"⚠️ Selected **{len(selected)}** locations to close")
                
                if st.button("🗑️ Close Selected Locations", type="primary"):
                    try:
                        close_query = text("""
                            UPDATE locations
                            SET close_date = CURDATE()
                            WHERE location_id IN :ids
                        """)
                        
                        location_ids = tuple(selected['location_id'].tolist())
                        db.execute(close_query, {"ids": location_ids})
                        db.commit()
                        
                        st.success(f"✅ Closed {len(selected)} locations")
                        st.balloons()
                        st.rerun()
                    
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error: {str(e)}")
        
        else:
            st.markdown("#### Upload CSV with Location IDs")
            
            delete_template = pd.DataFrame({
                'location_id': df['location_id'].head(5).tolist()
            })
            
            csv_buffer = io.StringIO()
            delete_template.to_csv(csv_buffer, index=False)
            
            st.download_button(
                label="📄 Download ID Template",
                data=csv_buffer.getvalue(),
                file_name="locations_delete_template.csv",
                mime="text/csv"
            )
            
            uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
            
            if uploaded_file:
                try:
                    delete_df = pd.read_csv(uploaded_file)
                    
                    if 'location_id' not in delete_df.columns:
                        st.error("❌ CSV must have 'location_id' column")
                    else:
                        ids_to_delete = delete_df['location_id'].tolist()
                        st.warning(f"⚠️ Will close **{len(ids_to_delete)}** locations")
                        
                        preview = df[df['location_id'].isin(ids_to_delete)]
                        st.dataframe(preview, use_container_width=True, hide_index=True)
                        
                        if st.button("🗑️ Confirm Close", type="primary"):
                            try:
                                close_query = text("""
                                    UPDATE locations
                                    SET close_date = CURDATE()
                                    WHERE location_id IN :ids
                                """)
                                
                                db.execute(close_query, {"ids": tuple(ids_to_delete)})
                                db.commit()
                                
                                st.success(f"✅ Closed {len(ids_to_delete)} locations")
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