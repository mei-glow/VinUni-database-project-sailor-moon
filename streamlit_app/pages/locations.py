import streamlit as st
import pandas as pd
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
    tab1, tab2 = st.tabs(["📋 Location List", "➕ Create Location"])
    
    with tab1:
        show_location_list()
    
    with tab2:
        show_create_location()

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
                l.email,
                l.close_date,
                CONCAT(e.first_name, ' ', e.last_name) as manager_name
            FROM locations l
            LEFT JOIN employees e ON l.store_manager_id = e.employee_id
            ORDER BY l.location_id DESC
        """)
        
        result = db.execute(query).fetchall()
        locations_df = pd.DataFrame(result, columns=[
            'location_id', 'location_name', 'location_type', 'address',
            'city', 'region', 'email', 'close_date', 'manager_name'
        ])
        
        if not locations_df.empty:
            # Format data
            locations_df['status'] = locations_df['close_date'].apply(
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
            filtered_df = locations_df.copy()
            
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
                    'city', 'region', 'manager_name', 'status'
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "location_id": "ID",
                    "location_name": "Name",
                    "location_type": "Type",
                    "city": "City",
                    "region": "Region",
                    "manager_name": "Manager",
                    "status": "Status"
                }
            )
            
            st.info(f"📊 Showing {len(filtered_df)} of {len(locations_df)} locations")
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Locations", len(locations_df))
            with col2:
                st.metric("Stores", len(locations_df[locations_df['location_type'] == 'STORE']))
            with col3:
                st.metric("Warehouses", len(locations_df[locations_df['location_type'] == 'WAREHOUSE']))
            with col4:
                st.metric("Active", len(locations_df[locations_df['close_date'].isna()]))
            
            # Location details expander
            st.markdown("---")
            with st.expander("📋 View Detailed Information"):
                selected_location = st.selectbox(
                    "Select Location",
                    options=filtered_df['location_name'].tolist()
                )
                
                if selected_location:
                    loc_data = filtered_df[filtered_df['location_name'] == selected_location].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**📍 Location Information**")
                        st.write(f"**ID:** {loc_data['location_id']}")
                        st.write(f"**Name:** {loc_data['location_name']}")
                        st.write(f"**Type:** {loc_data['location_type']}")
                        st.write(f"**Region:** {loc_data['region']}")
                    
                    with col2:
                        st.write("**📧 Contact Information**")
                        st.write(f"**City:** {loc_data['city']}")
                        st.write(f"**Address:** {loc_data['address'] if pd.notna(loc_data['address']) else 'N/A'}")
                        st.write(f"**Email:** {loc_data['email'] if pd.notna(loc_data['email']) else 'N/A'}")
                        st.write(f"**Manager:** {loc_data['manager_name'] if pd.notna(loc_data['manager_name']) else 'N/A'}")
        
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
        result = db.execute(managers_query).fetchall()
        managers = pd.DataFrame(result, columns=['employee_id', 'name'])
        
        with st.form("create_location_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                location_name = st.text_input("🏢 Location Name *", placeholder="VinRetail Store HN01")
                location_type = st.selectbox("🏷️ Type *", ["STORE", "WAREHOUSE"])
                city = st.text_input("🏙️ City *", placeholder="Hanoi")
                region = st.selectbox("🗺️ Region *", ["North", "South"])
            
            with col2:
                address = st.text_area("📍 Address", placeholder="Full address")
                email = st.text_input("📧 Email", placeholder="location@vinretail.com")
                
                manager = st.selectbox(
                    "👔 Store Manager",
                    options=["None"] + managers['name'].tolist() if not managers.empty else ["None"],
                    help="Select store manager (optional)"
                )
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ Create Location", use_container_width=True)
            with col2:
                if st.form_submit_button("🔄 Clear", use_container_width=True):
                    st.rerun()
            
            if submit:
                # Validation
                if not all([location_name, location_type, city, region]):
                    st.error("❌ Please fill all required fields")
                else:
                    try:
                        # Get manager_id if selected
                        manager_id = None
                        if manager != "None" and not managers.empty:
                            manager_id = managers[managers['name'] == manager]['employee_id'].values[0]
                        
                        # Create location
                        create_query = text("""
                            INSERT INTO locations (
                                location_name, location_type, address,
                                city, region, email, store_manager_id
                            )
                            VALUES (:n, :t, :a, :c, :r, :e, :m)
                        """)
                        
                        db.execute(create_query, {
                            "n": location_name,
                            "t": location_type,
                            "a": address if address else None,
                            "c": city,
                            "r": region,
                            "e": email if email else None,
                            "m": manager_id
                        })
                        
                        db.commit()
                        st.success(f"✅ Location '{location_name}' created successfully!")
                        st.balloons()
                    
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error creating location: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()