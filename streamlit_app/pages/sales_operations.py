import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import datetime
from config.session import get_db_connection
from utils.auth import check_permission

def show():
    """Display sales operations page with full workflow"""
    
    st.markdown("""
        <div class="main-header">
            <h1>🛒 Sales Operations</h1>
            <p>Complete sales workflow: Create → Confirm → Deliver → Return</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Main tabs
    tabs = st.tabs([
        "📝 Create Order",
        "✅ Confirm Order", 
        "🚚 Create Delivery",
        "↩️ Process Return",
        "📋 Order History"
    ])
    
    with tabs[0]:
        show_create_order()
    
    with tabs[1]:
        show_confirm_order()
    
    with tabs[2]:
        show_create_delivery()
    
    with tabs[3]:
        show_process_return()
    
    with tabs[4]:
        show_order_history()


# ============================================================
# TAB 1: CREATE ORDER (DRAFT/CART)
# ============================================================

def show_create_order():
    """Create new sales order (draft state)"""
    st.markdown("### 📝 Create New Sales Order")
    
    # Check permission
    if not check_permission("ORDER_CREATE"):
        st.error("⛔ You don't have permission to create orders")
        return
    
    db = get_db_connection()
    
    try:
        # Get customers
        customers_query = text("""
            SELECT customer_id, CONCAT(first_name, ' ', last_name, ' (', email, ')') as customer_name
            FROM customers
            ORDER BY first_name, last_name
            LIMIT 100
        """)
        customers = db.execute(customers_query).fetchall()
        customers_df = pd.DataFrame(customers, columns=['customer_id', 'customer_name'])
        
        # Get employees
        employees_query = text("""
            SELECT employee_id, CONCAT(first_name, ' ', last_name) as employee_name
            FROM employees
            WHERE role IN ('Staff', 'Manager') AND is_inactive = 0
            ORDER BY first_name, last_name
        """)
        employees = db.execute(employees_query).fetchall()
        employees_df = pd.DataFrame(employees, columns=['employee_id', 'employee_name'])
        
        # Get locations
        locations_query = text("""
            SELECT location_id, location_name
            FROM locations
            WHERE location_type = 'STORE' AND close_date IS NULL
            ORDER BY location_name
        """)
        locations = db.execute(locations_query).fetchall()
        locations_df = pd.DataFrame(locations, columns=['location_id', 'location_name'])
        
        if customers_df.empty or employees_df.empty or locations_df.empty:
            st.warning("⚠️ Missing required data (customers, employees, or locations)")
            return
        
        # Get products
        products_query = text("""
            SELECT product_id, product_name, unit_price,
                   (SELECT COALESCE(SUM(quantity), 0) FROM inventory WHERE product_id = p.product_id) as stock
            FROM products p
            WHERE status = 'ACTIVE'
            ORDER BY product_name
        """)
        products = db.execute(products_query).fetchall()
        products_df = pd.DataFrame(products, columns=['product_id', 'product_name', 'unit_price', 'stock'])
        
        # Get promotions - FIXED: use correct column names
        promotions_query = text("""
            SELECT 
                p.promotion_id, 
                p.promotion_code,
                p.discount_percent, 
                p.discount_value,
                pc.campaign_name
            FROM promotions p
            LEFT JOIN promotions_campaigns pc ON p.campaign_id = pc.campaign_id
            WHERE p.status = 'ACTIVE' 
              AND (pc.start_date IS NULL OR pc.start_date <= CURDATE())
              AND (pc.end_date IS NULL OR pc.end_date >= CURDATE())
            ORDER BY p.promotion_code
        """)
        promotions = db.execute(promotions_query).fetchall()
        promotions_df = pd.DataFrame(promotions, columns=['promotion_id', 'promotion_code', 'discount_percent', 'discount_value', 'campaign_name'])
        
        # Customer lookup section - OUTSIDE form for real-time search
        st.markdown("#### 👤 Customer Information")
        st.markdown("*Enter phone number to search existing customer or create new*")
        
        delivery_phone = st.text_input(
            "📱 Phone Number *",
            placeholder="0912345678",
            help="10-digit phone number",
            key="delivery_phone_input"
        )
        
        # Initialize variables
        customer_id = None
        is_new_customer = False
        first_name = ""
        last_name = ""
        email = ""
        delivery_address = ""
        customer_found = False
        
        # Real-time customer lookup when phone has 10 digits
        if delivery_phone and len(delivery_phone.strip()) >= 10:
            customer_query = text("""
                SELECT customer_id, first_name, last_name, email, address
                FROM customers
                WHERE phone = :phone
            """)
            
            customer = db.execute(customer_query, {"phone": delivery_phone.strip()}).fetchone()
            
            if customer:
                # FOUND: Existing customer
                customer_found = True
                customer_id = customer.customer_id
                is_new_customer = False
                
                st.success(f"✅ Found customer: **{customer.first_name} {customer.last_name}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name *", value=customer.first_name, key="fn_edit")
                    email = st.text_input("Email", value=customer.email or "", key="email_edit")
                with col2:
                    last_name = st.text_input("Last Name *", value=customer.last_name, key="ln_edit")
                    delivery_address = st.text_input("Delivery Address *", value=customer.address or "", key="addr_edit")
                
                st.info("💡 You can edit customer information if needed")
                
            else:
                # NOT FOUND: New customer
                is_new_customer = True
                st.info("📝 New customer - Please fill in details below")
                
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name *", placeholder="Enter first name", key="fn_new")
                    email = st.text_input("Email", placeholder="customer@email.com", key="email_new")
                with col2:
                    last_name = st.text_input("Last Name *", placeholder="Enter last name", key="ln_new")
                    delivery_address = st.text_input("Delivery Address *", placeholder="Full delivery address", key="addr_new")
        
        elif delivery_phone and len(delivery_phone.strip()) > 0 and len(delivery_phone.strip()) < 10:
            st.warning("⚠️ Phone number should be at least 10 digits")
        
        st.markdown("---")
        
        with st.form("create_order_form"):
            st.markdown("#### 📦 Order Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                employee = st.selectbox(
                    "👨‍💼 Sales Employee *",
                    options=employees_df['employee_name'].tolist(),
                    help="Select sales employee"
                )
            
            with col2:
                location = st.selectbox(
                    "🏪 Store Location *",
                    options=locations_df['location_name'].tolist(),
                    help="Select store location"
                )
            
            note = st.text_area("📝 Order Note", placeholder="Optional note...")
            
            st.markdown("---")
            
            # FIXED: Add submit button
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ Create Order", use_container_width=True)
            with col2:
                clear = st.form_submit_button("🔄 Clear", use_container_width=True)
            
        # Move product selection OUTSIDE form for better UX
        st.markdown("---")
        st.markdown("#### Add Products to Order")
        
        # Product selection (up to 5 items) - DYNAMIC
        num_items = st.number_input("Number of products", min_value=1, max_value=5, value=1, key="num_products")
        
        items = []
        selected_product_ids = set()  # Track selected products to prevent duplicates
        
        for i in range(num_items):
            st.markdown(f"**Product #{i+1}**")
            col1, col2, col3 = st.columns([3, 1, 2])
            
            with col1:
                product = st.selectbox(
                    f"Product",
                    options=products_df['product_name'].tolist(),
                    key=f"product_{i}",
                    help="Select product"
                )
            
            with col2:
                quantity = st.number_input(
                    f"Quantity",
                    min_value=1,
                    value=1,
                    key=f"qty_{i}"
                )
            
            with col3:
                # FIXED: use promotion_code instead of promotion_name
                promo_options = ["None"]
                if not promotions_df.empty:
                    promo_options += [f"{row['promotion_code']} ({row['campaign_name'] or 'No Campaign'})" 
                                     for _, row in promotions_df.iterrows()]
                
                promotion = st.selectbox(
                    f"Promotion",
                    options=promo_options,
                    key=f"promo_{i}",
                    help="Optional promotion"
                )
            
            if product:
                product_id = products_df[products_df['product_name'] == product]['product_id'].values[0]
                unit_price = products_df[products_df['product_name'] == product]['unit_price'].values[0]
                stock = products_df[products_df['product_name'] == product]['stock'].values[0]
                
                promotion_id = None
                if promotion != "None" and not promotions_df.empty:
                    # Extract promotion_code from display string
                    promo_code = promotion.split(' (')[0]
                    promo_match = promotions_df[promotions_df['promotion_code'] == promo_code]
                    if not promo_match.empty:
                        promotion_id = promo_match['promotion_id'].values[0]
                
                # Check for duplicate product
                if product_id in selected_product_ids:
                    st.warning(f"⚠️ Product '{product}' already selected! Please choose a different product.")
                else:
                    selected_product_ids.add(product_id)
                    items.append({
                        'product_id': product_id,
                        'product_name': product,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'stock': stock,
                        'promotion_id': promotion_id
                    })
                
                st.info(f"💰 Unit Price: {unit_price:,.0f} VND | 📦 Stock: {stock}")
        
        # Show summary
        if items:
            st.markdown("---")
            st.markdown("#### 📋 Order Summary")
            summary_data = []
            for item in items:
                summary_data.append({
                    'Product': item['product_name'],
                    'Quantity': item['quantity'],
                    'Unit Price': f"{item['unit_price']:,.0f} VND",
                    'Stock': item['stock']
                })
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
            st.metric("📦 Total Items", len(items))
        
        if clear:
            st.rerun()
        
        if submit:
                # Validation
                errors = []
                
                if not delivery_phone or len(delivery_phone.strip()) < 10:
                    errors.append("Valid phone number (10+ digits) is required")
                
                if not first_name or not last_name:
                    errors.append("Customer first name and last name are required")
                
                if not delivery_address:
                    errors.append("Delivery address is required")
                
                if not employee or not location:
                    errors.append("Employee and location are required")
                
                if len(items) == 0:
                    errors.append("Please add at least one product to the order")
                
                # Check stock availability
                for item in items:
                    if item['quantity'] > item['stock']:
                        errors.append(f"Insufficient stock for {item['product_name']} (Available: {item['stock']})")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    try:
                        # Handle customer creation or update
                        if is_new_customer:
                            # Create new customer
                            create_customer_query = text("""
                                INSERT INTO customers (first_name, last_name, phone, email, address)
                                VALUES (:fn, :ln, :phone, :email, :addr)
                            """)
                            
                            db.execute(create_customer_query, {
                                "fn": first_name.strip(),
                                "ln": last_name.strip(),
                                "phone": delivery_phone.strip(),
                                "email": email.strip() if email else None,
                                "addr": delivery_address.strip()
                            })
                            
                            customer_id = db.execute(text("SELECT LAST_INSERT_ID() as id")).fetchone().id
                            st.info(f"✅ Created new customer: {first_name} {last_name}")
                        
                        else:
                            # Update existing customer if information changed
                            update_customer_query = text("""
                                UPDATE customers
                                SET first_name = :fn, 
                                    last_name = :ln, 
                                    email = :email, 
                                    address = :addr,
                                    last_modified = NOW()
                                WHERE customer_id = :cid
                            """)
                            
                            db.execute(update_customer_query, {
                                "fn": first_name.strip(),
                                "ln": last_name.strip(),
                                "email": email.strip() if email else None,
                                "addr": delivery_address.strip(),
                                "cid": customer_id
                            })
                        
                        # Get employee and location IDs
                        employee_id = employees_df[employees_df['employee_name'] == employee]['employee_id'].values[0]
                        location_id = locations_df[locations_df['location_name'] == location]['location_id'].values[0]
                        
                        # Call stored procedure: sp_create_sales_order
                        create_order_query = text("""
                            CALL sp_create_sales_order(:cid, :eid, :lid, :note, :phone, :addr)
                        """)
                        
                        db.execute(create_order_query, {
                            "cid": customer_id,
                            "eid": employee_id,
                            "lid": location_id,
                            "note": note.strip() if note else None,
                            "phone": delivery_phone.strip(),
                            "addr": delivery_address.strip()
                        })
                        
                        # Get the newly created order_id
                        order_id_query = text("SELECT LAST_INSERT_ID() as order_id")
                        order_id = db.execute(order_id_query).fetchone().order_id
                        
                        # Add items using sp_add_sales_order_item
                        for item in items:
                            add_item_query = text("""
                                CALL sp_add_sales_order_item(:oid, :pid, :qty, :promo)
                            """)
                            
                            db.execute(add_item_query, {
                                "oid": order_id,
                                "pid": item['product_id'],
                                "qty": item['quantity'],
                                "promo": item['promotion_id']
                            })
                        
                        db.commit()
                        
                        st.success(f"✅ Order #{order_id} created successfully!")
                        st.balloons()
                        
                        # Show order summary
                        st.markdown("---")
                        st.markdown("### 📋 Order Summary")
                        st.info(f"""
                        **Order ID:** {order_id}  
                        **Customer:** {first_name} {last_name}  
                        **Phone:** {delivery_phone}  
                        **Address:** {delivery_address}  
                        **Location:** {location}  
                        **Status:** OPEN (Draft)  
                        **Items:** {len(items)} products
                        """)
                        
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error creating order: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()


# ============================================================
# TAB 2: CONFIRM ORDER & GENERATE INVOICE
# ============================================================

def show_confirm_order():
    """Confirm sales order and generate invoice"""
    st.markdown("### ✅ Confirm Sales Order")
    
    # Check permission
    if not check_permission("ORDER_CONFIRM"):
        st.error("⛔ You don't have permission to confirm orders")
        return
    
    db = get_db_connection()
    
    try:
        # Get open orders
        orders_query = text("""
            SELECT 
                so.order_id,
                so.order_date,
                CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                l.location_name,
                COUNT(soi.order_item_id) as item_count,
                COALESCE(SUM(soi.final_amount), 0) as total_amount
            FROM sales_orders so
            JOIN customers c ON so.customer_id = c.customer_id
            JOIN locations l ON so.location_id = l.location_id
            LEFT JOIN sales_order_items soi ON so.order_id = soi.order_id
            WHERE so.order_status = 'OPEN'
            GROUP BY so.order_id, so.order_date, c.first_name, c.last_name, l.location_name
            ORDER BY so.order_date DESC
            LIMIT 50
        """)
        
        orders = db.execute(orders_query).fetchall()
        orders_df = pd.DataFrame(orders, columns=[
            'order_id', 'order_date', 'customer_name', 'location_name', 'item_count', 'total_amount'
        ])
        
        if orders_df.empty:
            st.info("ℹ️ No open orders available to confirm")
            return
        
        # Display orders table
        st.markdown("#### 📋 Open Orders (Ready to Confirm)")
        
        st.dataframe(
            orders_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "order_id": "Order ID",
                "order_date": st.column_config.DatetimeColumn("Date", format="DD/MM/YYYY HH:mm"),
                "customer_name": "Customer",
                "location_name": "Location",
                "item_count": "Items",
                "total_amount": st.column_config.NumberColumn("Total (VND)", format="%.0f")
            }
        )
        
        st.markdown("---")
        
        # Get payment methods
        payment_methods_query = text("""
            SELECT payment_method_id, method_name
            FROM payment_methods
            ORDER BY method_name
        """)
        payment_methods = db.execute(payment_methods_query).fetchall()
        payment_methods_df = pd.DataFrame(payment_methods, columns=['payment_method_id', 'method_name'])
        
        # Confirm form
        with st.form("confirm_order_form"):
            st.markdown("#### Confirm Order")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_order = st.selectbox(
                    "📦 Select Order to Confirm *",
                    options=orders_df['order_id'].tolist(),
                    format_func=lambda x: f"Order #{x} - {orders_df[orders_df['order_id']==x]['customer_name'].values[0]}"
                )
            
            with col2:
                payment_method = st.selectbox(
                    "💳 Payment Method *",
                    options=payment_methods_df['method_name'].tolist() if not payment_methods_df.empty else []
                )
            
            # Show order details
            if selected_order:
                st.markdown("---")
                st.markdown("#### 📝 Order Details")
                
                # FIXED: Remove promotion_name reference
                order_items_query = text("""
                    SELECT 
                        p.product_name,
                        soi.quantity,
                        p.unit_price,
                        soi.final_amount,
                        pr.promotion_code
                    FROM sales_order_items soi
                    JOIN products p ON soi.product_id = p.product_id
                    LEFT JOIN promotions pr ON soi.applied_promotion_id = pr.promotion_id
                    WHERE soi.order_id = :oid
                """)
                
                items = db.execute(order_items_query, {"oid": selected_order}).fetchall()
                items_df = pd.DataFrame(items, columns=[
                    'product_name', 'quantity', 'unit_price', 'final_amount', 'promotion_code'
                ])
                
                if not items_df.empty:
                    st.dataframe(
                        items_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "product_name": "Product",
                            "quantity": "Qty",
                            "unit_price": st.column_config.NumberColumn("Unit Price", format="%.0f VND"),
                            "final_amount": st.column_config.NumberColumn("Total", format="%.0f VND"),
                            "promotion_code": "Promotion"
                        }
                    )
                    
                    total = items_df['final_amount'].sum()
                    st.metric("💰 Order Total (incl. VAT)", f"{total:,.0f} VND")
            
            st.markdown("---")
            
            # FIXED: Add submit button
            col1, col2 = st.columns(2)
            with col1:
                confirm = st.form_submit_button("✅ Confirm Order & Generate Invoice", use_container_width=True)
            with col2:
                refresh = st.form_submit_button("🔄 Refresh", use_container_width=True)
            
            if refresh:
                st.rerun()
            
            if confirm:
                if not selected_order or not payment_method:
                    st.error("❌ Please select order and payment method")
                else:
                    try:
                        payment_method_id = payment_methods_df[payment_methods_df['method_name'] == payment_method]['payment_method_id'].values[0]
                        
                        # Call stored procedure: sp_confirm_sales_order
                        confirm_query = text("""
                            CALL sp_confirm_sales_order(:oid, :pmid)
                        """)
                        
                        db.execute(confirm_query, {
                            "oid": selected_order,
                            "pmid": payment_method_id
                        })
                        
                        db.commit()
                        
                        st.success(f"✅ Order #{selected_order} confirmed successfully!")
                        st.info("📄 Invoice generated and inventory updated")
                        st.balloons()
                        
                        # Get sale_id
                        sale_query = text("""
                            SELECT sale_id FROM sales WHERE order_id = :oid AND sale_type = 'INVOICE'
                        """)
                        sale_result = db.execute(sale_query, {"oid": selected_order}).fetchone()
                        
                        if sale_result:
                            st.success(f"📝 Invoice ID: {sale_result.sale_id}")
                        
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error confirming order: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()


# ============================================================
# TAB 3: CREATE DELIVERY
# ============================================================

def show_create_delivery():
    """Create delivery for confirmed invoice"""
    st.markdown("### 🚚 Create Delivery")
    
    # Check permission
    if not check_permission("DELIVERY_CREATE"):
        st.error("⛔ You don't have permission to create deliveries")
        return
    
    db = get_db_connection()
    
    try:
        # Get confirmed sales without delivery
        sales_query = text("""
            SELECT 
                s.sale_id,
                s.sale_date,
                CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                so.delivery_phone,
                so.delivery_address,
                l.location_name,
                l.location_id,
                s.total_amount
            FROM sales s
            JOIN sales_orders so ON s.order_id = so.order_id
            JOIN customers c ON so.customer_id = c.customer_id
            JOIN locations l ON so.location_id = l.location_id
            LEFT JOIN deliveries d ON s.sale_id = d.sale_id
            WHERE s.sale_type = 'INVOICE' 
              AND s.invoice_status = 'PAID'
              AND d.delivery_id IS NULL
            ORDER BY s.sale_date DESC
            LIMIT 50
        """)
        
        sales = db.execute(sales_query).fetchall()
        sales_df = pd.DataFrame(sales, columns=[
            'sale_id', 'sale_date', 'customer_name', 'delivery_phone', 'delivery_address', 'location_name', 'location_id', 'total_amount'
        ])
        
        if sales_df.empty:
            st.info("ℹ️ No invoices available for delivery")
            return
        
        # Display sales
        st.markdown("#### 📋 Invoices Ready for Delivery")
        
        display_df = sales_df[['sale_id', 'sale_date', 'customer_name', 'delivery_phone', 'delivery_address', 'location_name', 'total_amount']]
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "sale_id": "Invoice ID",
                "sale_date": st.column_config.DatetimeColumn("Date", format="DD/MM/YYYY"),
                "customer_name": "Customer",
                "delivery_phone": "Phone",
                "delivery_address": "Delivery Address",
                "location_name": "From Store",
                "total_amount": st.column_config.NumberColumn("Amount", format="%.0f VND")
            }
        )
        
        st.markdown("---")
        
        # Get delivery persons
        delivery_persons_query = text("""
            SELECT employee_id, CONCAT(first_name, ' ', last_name) as employee_name
            FROM employees
            WHERE role = 'Delivery' AND is_inactive = 0
            ORDER BY first_name, last_name
        """)
        delivery_persons = db.execute(delivery_persons_query).fetchall()
        delivery_persons_df = pd.DataFrame(delivery_persons, columns=['employee_id', 'employee_name'])
        
        # Get vendors
        vendors_query = text("""
            SELECT vendor_id, vendor_name
            FROM delivery_vendors
            ORDER BY vendor_name
        """)
        vendors = db.execute(vendors_query).fetchall()
        vendors_df = pd.DataFrame(vendors, columns=['vendor_id', 'vendor_name'])
        
        # Create delivery form
        with st.form("create_delivery_form"):
            st.markdown("#### Create Delivery")
            
            col1, col2 = st.columns(2)
            
            from_location_id = None
            
            with col1:
                selected_sale = st.selectbox(
                    "📦 Select Invoice *",
                    options=sales_df['sale_id'].tolist(),
                    format_func=lambda x: f"Invoice #{x} - {sales_df[sales_df['sale_id']==x]['customer_name'].values[0]}"
                )
                
                delivery_person = st.selectbox(
                    "🚴 Delivery Person *",
                    options=delivery_persons_df['employee_name'].tolist() if not delivery_persons_df.empty else []
                )
            
            with col2:
                vendor = st.selectbox(
                    "🏢 Delivery Vendor",
                    options=["None"] + vendors_df['vendor_name'].tolist() if not vendors_df.empty else ["None"]
                )
                
                # Get from_location
                if selected_sale:
                    from_location_id = sales_df[sales_df['sale_id'] == selected_sale]['location_id'].values[0]
                    from_location_name = sales_df[sales_df['sale_id'] == selected_sale]['location_name'].values[0]
                    st.info(f"📍 From Location: {from_location_name}")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                create = st.form_submit_button("✅ Create Delivery", use_container_width=True)
            with col2:
                refresh = st.form_submit_button("🔄 Refresh", use_container_width=True)
            
            if refresh:
                st.rerun()
            
            if create:
                if not selected_sale or not delivery_person:
                    st.error("❌ Please select invoice and delivery person")
                else:
                    try:
                        delivery_person_id = delivery_persons_df[delivery_persons_df['employee_name'] == delivery_person]['employee_id'].values[0]
                        
                        vendor_id = None
                        if vendor != "None" and not vendors_df.empty:
                            vendor_id = vendors_df[vendors_df['vendor_name'] == vendor]['vendor_id'].values[0]
                        
                        # Call stored procedure: sp_create_delivery_for_sale
                        delivery_query = text("""
                            CALL sp_create_delivery_for_sale(:sid, :flid, :dpid, :vid)
                        """)
                        
                        db.execute(delivery_query, {
                            "sid": selected_sale,
                            "flid": from_location_id,
                            "dpid": delivery_person_id,
                            "vid": vendor_id
                        })
                        
                        db.commit()
                        
                        st.success(f"✅ Delivery created for Invoice #{selected_sale}")
                        st.balloons()
                        
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error creating delivery: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()


# ============================================================
# TAB 4: PROCESS RETURN
# ============================================================

def show_process_return():
    """Process sales return"""
    st.markdown("### ↩️ Process Sales Return")
    
    # Check permission
    if not check_permission("RETURN_PROCESS"):
        st.error("⛔ You don't have permission to process returns")
        return
    
    db = get_db_connection()
    
    try:
        # Get recent sales (INVOICE only)
        sales_query = text("""
            SELECT 
                s.sale_id,
                s.sale_date,
                CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                l.location_name,
                l.location_id,
                s.total_amount
            FROM sales s
            JOIN sales_orders so ON s.order_id = so.order_id
            JOIN customers c ON so.customer_id = c.customer_id
            JOIN locations l ON so.location_id = l.location_id
            WHERE s.sale_type = 'INVOICE'
              AND s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            ORDER BY s.sale_date DESC
            LIMIT 50
        """)
        
        sales = db.execute(sales_query).fetchall()
        sales_df = pd.DataFrame(sales, columns=[
            'sale_id', 'sale_date', 'customer_name', 'location_name', 'location_id', 'total_amount'
        ])
        
        if sales_df.empty:
            st.info("ℹ️ No recent sales available for return")
            return
        
        # Display sales
        st.markdown("#### 📋 Recent Sales (Last 30 Days)")
        
        display_df = sales_df[['sale_id', 'sale_date', 'customer_name', 'location_name', 'total_amount']]
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "sale_id": "Sale ID",
                "sale_date": st.column_config.DatetimeColumn("Date", format="DD/MM/YYYY"),
                "customer_name": "Customer",
                "location_name": "Location",
                "total_amount": st.column_config.NumberColumn("Amount", format="%.0f VND")
            }
        )
        
        st.markdown("---")
        
        # Get payment methods
        payment_methods_query = text("""
            SELECT payment_method_id, method_name
            FROM payment_methods
            ORDER BY method_name
        """)
        payment_methods = db.execute(payment_methods_query).fetchall()
        payment_methods_df = pd.DataFrame(payment_methods, columns=['payment_method_id', 'method_name'])
        
        # Return form
        with st.form("process_return_form"):
            st.markdown("#### Process Return")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_sale = st.selectbox(
                    "📦 Select Original Sale *",
                    options=sales_df['sale_id'].tolist(),
                    format_func=lambda x: f"Sale #{x} - {sales_df[sales_df['sale_id']==x]['customer_name'].values[0]}"
                )
            
            with col2:
                refund_method = st.selectbox(
                    "💳 Refund Method *",
                    options=payment_methods_df['method_name'].tolist() if not payment_methods_df.empty else []
                )
            
            # Show sale items and get return location
            return_product = None
            return_quantity = 1
            product_id = None
            return_location_id = None
            
            if selected_sale:
                st.markdown("---")
                st.markdown("#### 📝 Sale Items")
                
                items_query = text("""
                    SELECT 
                        si.sale_item_id,
                        p.product_id,
                        p.product_name,
                        si.quantity,
                        si.final_amount
                    FROM sales_items si
                    JOIN products p ON si.product_id = p.product_id
                    WHERE si.sale_id = :sid AND si.sale_type = 'INVOICE'
                """)
                
                items = db.execute(items_query, {"sid": selected_sale}).fetchall()
                items_df = pd.DataFrame(items, columns=[
                    'sale_item_id', 'product_id', 'product_name', 'quantity', 'final_amount'
                ])
                
                if not items_df.empty:
                    st.dataframe(
                        items_df[['product_name', 'quantity', 'final_amount']],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Select item to return
                    return_product = st.selectbox(
                        "📦 Product to Return *",
                        options=items_df['product_name'].tolist()
                    )
                    
                    if return_product:
                        max_qty = items_df[items_df['product_name'] == return_product]['quantity'].values[0]
                        return_quantity = st.number_input(
                            "Return Quantity *",
                            min_value=1,
                            max_value=int(max_qty),
                            value=int(max_qty)
                        )
                        
                        product_id = items_df[items_df['product_name'] == return_product]['product_id'].values[0]
                
                # Get return location
                return_location_id = sales_df[sales_df['sale_id'] == selected_sale]['location_id'].values[0]
                return_location_name = sales_df[sales_df['sale_id'] == selected_sale]['location_name'].values[0]
                st.info(f"↩️ Return to Location: {return_location_name}")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                process = st.form_submit_button("✅ Process Return", use_container_width=True)
            with col2:
                refresh = st.form_submit_button("🔄 Refresh", use_container_width=True)
            
            if refresh:
                st.rerun()
            
            if process:
                if not selected_sale or not return_product or not refund_method:
                    st.error("❌ Please fill all required fields")
                else:
                    try:
                        payment_method_id = payment_methods_df[payment_methods_df['method_name'] == refund_method]['payment_method_id'].values[0]
                        
                        # Call stored procedure: sp_process_return
                        return_query = text("""
                            CALL sp_process_return(:osid, :pid, :rqty, :pmid, :rlid)
                        """)
                        
                        db.execute(return_query, {
                            "osid": selected_sale,
                            "pid": product_id,
                            "rqty": return_quantity,
                            "pmid": payment_method_id,
                            "rlid": return_location_id
                        })
                        
                        db.commit()
                        
                        st.success(f"✅ Return processed successfully!")
                        st.info("📦 Inventory restored and refund initiated")
                        st.balloons()
                        
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ Error processing return: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()


# ============================================================
# TAB 5: ORDER HISTORY
# ============================================================

def show_order_history():
    """View order history and status"""
    st.markdown("### 📋 Order History")
    
    # Check permission
    if not check_permission("ORDER_VIEW"):
        st.error("⛔ You don't have permission to view orders")
        return
    
    db = get_db_connection()
    
    try:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Status", ["All", "OPEN", "CONFIRMED", "CANCELLED"])
        
        with col2:
            date_from = st.date_input("From Date", value=pd.to_datetime("today") - pd.Timedelta(days=30))
        
        with col3:
            date_to = st.date_input("To Date", value=pd.to_datetime("today"))
        
        # Build query
        where_clause = "WHERE 1=1"
        params = {}
        
        if status_filter != "All":
            where_clause += " AND so.order_status = :status"
            params["status"] = status_filter
        
        where_clause += " AND so.order_date >= :date_from AND so.order_date <= :date_to"
        params["date_from"] = date_from
        params["date_to"] = date_to
        
        # FIXED: Add all non-aggregated columns to GROUP BY
        orders_query = text(f"""
            SELECT 
                so.order_id,
                so.order_date,
                CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                l.location_name,
                so.order_status,
                COUNT(soi.order_item_id) as item_count,
                COALESCE(SUM(soi.final_amount), 0) as total_amount,
                MAX(s.sale_id) as sale_id,
                MAX(s.invoice_status) as invoice_status,
                MAX(d.delivery_status) as delivery_status
            FROM sales_orders so
            JOIN customers c ON so.customer_id = c.customer_id
            JOIN employees e ON so.employee_id = e.employee_id
            JOIN locations l ON so.location_id = l.location_id
            LEFT JOIN sales_order_items soi ON so.order_id = soi.order_id
            LEFT JOIN sales s ON so.order_id = s.order_id AND s.sale_type = 'INVOICE'
            LEFT JOIN deliveries d ON s.sale_id = d.sale_id
            {where_clause}
            GROUP BY so.order_id, so.order_date, c.first_name, c.last_name, 
                     e.first_name, e.last_name, l.location_name, so.order_status
            ORDER BY so.order_date DESC
            LIMIT 100
        """)
        
        orders = db.execute(orders_query, params).fetchall()
        orders_df = pd.DataFrame(orders, columns=[
            'order_id', 'order_date', 'customer_name', 'employee_name', 'location_name',
            'order_status', 'item_count', 'total_amount', 'sale_id', 'invoice_status', 'delivery_status'
        ])
        
        if orders_df.empty:
            st.info("ℹ️ No orders found")
            return
        
        # Format data
        orders_df['total_amount'] = orders_df['total_amount'].fillna(0)
        # FIXED: Keep sale_id as is (already has NULL/0 handled by MAX() in query)
        # Don't convert to int then back to string - this causes PyArrow error
        orders_df['sale_id'] = orders_df['sale_id'].apply(lambda x: str(int(x)) if x and x > 0 else '-')
        orders_df['invoice_status'] = orders_df['invoice_status'].fillna('-')
        orders_df['delivery_status'] = orders_df['delivery_status'].fillna('-')
        
        # Display table
        st.dataframe(
            orders_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "order_id": "Order ID",
                "order_date": st.column_config.DatetimeColumn("Date", format="DD/MM/YYYY HH:mm"),
                "customer_name": "Customer",
                "employee_name": "Employee",
                "location_name": "Location",
                "order_status": "Status",
                "item_count": "Items",
                "total_amount": st.column_config.NumberColumn("Total", format="%.0f VND"),
                "sale_id": "Invoice ID",
                "invoice_status": "Invoice",
                "delivery_status": "Delivery"
            }
        )
        
        st.info(f"📊 Showing {len(orders_df)} orders")
        
        # Statistics
        st.markdown("---")
        st.markdown("### 📊 Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Orders", len(orders_df))
        with col2:
            st.metric("Open", len(orders_df[orders_df['order_status'] == 'OPEN']))
        with col3:
            st.metric("Confirmed", len(orders_df[orders_df['order_status'] == 'CONFIRMED']))
        with col4:
            total_revenue = orders_df[orders_df['order_status'] == 'CONFIRMED']['total_amount'].sum()
            st.metric("Total Revenue", f"{total_revenue:,.0f} VND")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        db.close()