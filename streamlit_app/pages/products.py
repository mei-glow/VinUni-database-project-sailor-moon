import streamlit as st
import pandas as pd
from sqlalchemy import text
from config.session import get_db_connection
from utils.auth import check_permission

def show():
    """Display products management page"""
    
    st.markdown("""
        <div class="main-header">
            <h1>📦 Products Management</h1>
            <p>Manage product catalog and inventory</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check permissions
    if not check_permission("PRODUCT_VIEW"):
        st.error("⛔ You don't have permission to view products")
        return
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Product List", "➕ Create Product", "📊 Inventory"])
    
    with tab1:
        show_product_list()
    
    with tab2:
        if check_permission("PRODUCT_CREATE"):
            show_create_product()
        else:
            st.warning("⚠️ You don't have permission to create products")
    
    with tab3:
        show_inventory()

def show_product_list():
    """Display list of products"""
    st.markdown("### 📋 All Products")
    
    db = get_db_connection()
    
    try:
        query = text("""
            SELECT 
                p.product_id,
                p.product_name,
                p.unit_price,
                p.cost,
                p.status,
                pc.class_name,
                pc.product_group,
                COALESCE(SUM(i.quantity), 0) as total_inventory
            FROM products p
            JOIN product_class pc ON p.class_id = pc.class_id
            LEFT JOIN inventory i ON p.product_id = i.product_id
            GROUP BY p.product_id
            ORDER BY p.product_id DESC
        """)
        
        result = db.execute(query).fetchall()
        products_df = pd.DataFrame(result, columns=[
            'product_id', 'product_name', 'unit_price', 'cost', 'status',
            'class_name', 'product_group', 'total_inventory'
        ])
        
        
        if not products_df.empty:
            # Convert numeric columns
            products_df['product_id'] = pd.to_numeric(products_df['product_id'], errors='coerce')
            products_df['unit_price'] = pd.to_numeric(products_df['unit_price'], errors='coerce')
            products_df['cost'] = pd.to_numeric(products_df['cost'], errors='coerce')
            products_df['total_inventory'] = pd.to_numeric(products_df['total_inventory'], errors='coerce').fillna(0).astype(int)
            
            # Format data
            products_df['margin'] = ((products_df['unit_price'] - products_df['cost']) / products_df['cost'] * 100).round(2)
            products_df['price_display'] = products_df['unit_price'].apply(lambda x: f"{x:,.0f} VND" if pd.notna(x) else "0 VND")
            products_df['cost_display'] = products_df['cost'].apply(lambda x: f"{x:,.0f} VND" if pd.notna(x) else "0 VND")
            products_df['status_display'] = products_df['status'].apply(
                lambda x: '✅ Active' if x == 'ACTIVE' else ('❌ Inactive' if x == 'INACTIVE' else '⚠️ Discontinued')
            )
            
            # Filters
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                search = st.text_input("🔍 Search", placeholder="Product name")
            
            with col2:
                group_filter = st.selectbox("Group", ["All"] + products_df['product_group'].unique().tolist())
            
            with col3:
                class_filter = st.selectbox("Class", ["All"] + products_df['class_name'].unique().tolist())
            
            with col4:
                status_filter = st.selectbox("Status", ["All", "ACTIVE", "INACTIVE", "DISCONTINUED"])
            
            # Apply filters
            filtered_df = products_df.copy()
            
            if search:
                filtered_df = filtered_df[
                    filtered_df['product_name'].str.contains(search, case=False, na=False)
                ]
            
            if group_filter != "All":
                filtered_df = filtered_df[filtered_df['product_group'] == group_filter]
            
            if class_filter != "All":
                filtered_df = filtered_df[filtered_df['class_name'] == class_filter]
            
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            
            # Display table
            st.dataframe(
                filtered_df[[
                    'product_id', 'product_name', 'product_group', 'class_name',
                    'price_display', 'cost_display', 'margin', 'total_inventory', 'status_display'
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "product_id": "ID",
                    "product_name": "Product Name",
                    "product_group": "Group",
                    "class_name": "Class",
                    "price_display": "Price",
                    "cost_display": "Cost",
                    "margin": st.column_config.NumberColumn(
                        "Margin %",
                        format="%.2f%%"
                    ),
                    "total_inventory": "Stock",
                    "status_display": "Status"
                }
            )
            
            st.info(f"📊 Showing {len(filtered_df)} of {len(products_df)} products")
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Products", len(products_df))
            with col2:
                st.metric("Active", len(products_df[products_df['status'] == 'ACTIVE']))
            with col3:
                avg_margin = products_df['margin'].mean()
                st.metric("Avg Margin", f"{avg_margin:.1f}%")
            with col4:
                total_stock = products_df['total_inventory'].sum()
                st.metric("Total Stock", f"{total_stock:,.0f}")
        
        else:
            st.info("No products found")
    
    except Exception as e:
        st.error(f"❌ Error loading products: {str(e)}")
    
    finally:
        db.close()

def show_create_product():
    """Create new product form"""
    st.markdown("### ➕ Create New Product")
    
    db = get_db_connection()
    
    try:
        # Get product classes
        classes_query = text("""
            SELECT class_id, class_name, product_group
            FROM product_class
            ORDER BY product_group, class_name
        """)
        result = db.execute(classes_query).fetchall()
        classes = pd.DataFrame(result, columns=['class_id', 'class_name', 'product_group'])
        
        with st.form("create_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input("📦 Product Name *", placeholder="Product name")
                
                product_class = st.selectbox(
                    "🏷️ Product Class *",
                    options=classes['class_name'].tolist() if not classes.empty else [],
                    format_func=lambda x: f"{x} ({classes[classes['class_name']==x]['product_group'].values[0]})"
                                         if not classes.empty else x
                )
                
                unit_price = st.number_input("💰 Unit Price (VND) *", min_value=0, step=1000, value=0)
            
            with col2:
                cost = st.number_input("💵 Cost (VND) *", min_value=0, step=1000, value=0)
                
                status = st.selectbox("📊 Status *", ["ACTIVE", "INACTIVE", "DISCONTINUED"])
                
                # Calculate margin
                if cost > 0:
                    margin = ((unit_price - cost) / cost * 100)
                    st.metric("📈 Profit Margin", f"{margin:.2f}%")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ Create Product", use_container_width=True)
            with col2:
                if st.form_submit_button("🔄 Clear", use_container_width=True):
                    st.rerun()
            
            if submit:
                # Validation
                if not all([product_name, product_class]) or unit_price <= 0 or cost <= 0:
                    st.error("❌ Please fill all required fields with valid values")
                else:
                    try:
                        # Get class_id
                        class_id = classes[classes['class_name'] == product_class]['class_id'].values[0]
                        
                        # Create product
                        create_query = text("""
                            INSERT INTO products (
                                product_name, class_id, unit_price, cost, status
                            )
                            VALUES (:n, :c, :p, :cost, :s)
                        """)
                        
                        db.execute(create_query, {
                            "n": product_name,
                            "c": class_id,
                            "p": unit_price,
                            "cost": cost,
                            "s": status
                        })
                        
                        db.commit()
                        st.success(f"✅ Product '{product_name}' created successfully!")
                        st.balloons()
                    
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error creating product: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()

def show_inventory():
    """Display inventory across locations"""
    st.markdown("### 📊 Inventory Overview")
    
    db = get_db_connection()
    
    try:
        query = text("""
            SELECT 
                p.product_id,
                p.product_name,
                l.location_name,
                l.location_type,
                i.quantity,
                p.unit_price,
                (i.quantity * p.unit_price) as inventory_value
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            JOIN locations l ON i.location_id = l.location_id
            WHERE i.quantity > 0
            ORDER BY inventory_value DESC
        """)
        
        result = db.execute(query).fetchall()
        inventory_df = pd.DataFrame(result, columns=[
            'product_id', 'product_name', 'location_name', 'location_type',
            'quantity', 'unit_price', 'inventory_value'
        ])
        
        
        if not inventory_df.empty:
            # Convert numeric columns
            inventory_df['product_id'] = pd.to_numeric(inventory_df['product_id'], errors='coerce')
            inventory_df['quantity'] = pd.to_numeric(inventory_df['quantity'], errors='coerce').fillna(0).astype(int)
            inventory_df['unit_price'] = pd.to_numeric(inventory_df['unit_price'], errors='coerce')
            inventory_df['inventory_value'] = pd.to_numeric(inventory_df['inventory_value'], errors='coerce')
            
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search = st.text_input("🔍 Search Product", placeholder="Product name")
            
            with col2:
                location_filter = st.selectbox("Location", ["All"] + inventory_df['location_name'].unique().tolist())
            
            with col3:
                type_filter = st.selectbox("Location Type", ["All", "STORE", "WAREHOUSE"])
            
            # Apply filters
            filtered_df = inventory_df.copy()
            
            if search:
                filtered_df = filtered_df[
                    filtered_df['product_name'].str.contains(search, case=False, na=False)
                ]
            
            if location_filter != "All":
                filtered_df = filtered_df[filtered_df['location_name'] == location_filter]
            
            if type_filter != "All":
                filtered_df = filtered_df[filtered_df['location_type'] == type_filter]
            
            # Format display
            filtered_df['unit_price_display'] = filtered_df['unit_price'].apply(
                lambda x: f"{x:,.0f} VND" if pd.notna(x) else "0 VND"
            )
            filtered_df['inventory_value_display'] = filtered_df['inventory_value'].apply(
                lambda x: f"{x:,.0f} VND" if pd.notna(x) else "0 VND"
            )
            
            # Display table
            st.dataframe(
                filtered_df[[
                    'product_id', 'product_name', 'location_name', 'location_type',
                    'quantity', 'unit_price_display', 'inventory_value_display'
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "product_id": "Product ID",
                    "product_name": "Product",
                    "location_name": "Location",
                    "location_type": "Type",
                    "quantity": "Quantity",
                    "unit_price_display": "Unit Price",
                    "inventory_value_display": "Total Value"
                }
            )
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Items", f"{filtered_df['quantity'].sum():,.0f}")
            with col2:
                st.metric("Total Value", f"{filtered_df['inventory_value'].sum():,.0f} VND")
            with col3:
                st.metric("Unique Products", filtered_df['product_id'].nunique())
            with col4:
                st.metric("Locations", filtered_df['location_name'].nunique())
            
            # Low stock alert
            st.markdown("---")
            st.markdown("### ⚠️ Low Stock Alert")
            
            low_stock_query = text("""
                SELECT 
                    p.product_name,
                    l.location_name,
                    i.quantity
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                JOIN locations l ON i.location_id = l.location_id
                WHERE i.quantity < 100 AND i.quantity > 0
                ORDER BY i.quantity ASC
                LIMIT 10
            """)
            
            result = db.execute(low_stock_query).fetchall()
            low_stock = pd.DataFrame(result, columns=['product_name', 'location_name', 'quantity'])
            
            if not low_stock.empty:
                low_stock['quantity'] = pd.to_numeric(low_stock['quantity'], errors='coerce').fillna(0).astype(int)
            
            if not low_stock.empty:
                st.warning(f"⚠️ {len(low_stock)} products with low stock (< 100 units)")
                st.dataframe(low_stock, use_container_width=True, hide_index=True)
            else:
                st.success("✅ All products have adequate stock levels")
        
        else:
            st.info("No inventory data available")
    
    except Exception as e:
        st.error(f"❌ Error loading inventory: {str(e)}")
    
    finally:
        db.close()