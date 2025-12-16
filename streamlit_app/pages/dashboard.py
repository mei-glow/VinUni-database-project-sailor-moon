import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text
from config.session import get_db_connection

def show():
    """Display dashboard with KPIs and charts"""
    
    st.markdown("""
        <div class="main-header">
            <h1>🏠 Dashboard</h1>
            <p>Real-time business insights and key performance indicators</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Fetch KPIs
    db = get_db_connection()
    
    try:
        # KPI Metrics
        kpi_query = text("""
            SELECT 
                COUNT(DISTINCT s.sale_id) as total_sales,
                COALESCE(SUM(s.total_amount), 0) as total_revenue,
                COUNT(DISTINCT p.product_id) as total_products,
                COUNT(DISTINCT c.customer_id) as total_customers,
                COUNT(DISTINCT e.employee_id) as total_employees,
                COUNT(DISTINCT l.location_id) as total_locations
            FROM sales s
            CROSS JOIN products p
            CROSS JOIN customers c
            CROSS JOIN employees e
            CROSS JOIN locations l
            WHERE s.sale_type = 'INVOICE'
        """)
        
        kpi_data = db.execute(kpi_query).fetchone()
        
        # Display KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0;">💰 Total Revenue</h3>
                    <h2 style="margin: 0.5rem 0;">{:,.0f} VND</h2>
                    <p style="color: #6c757d; margin: 0;">Total sales amount</p>
                </div>
            """.format(kpi_data.total_revenue), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #28a745; margin: 0;">🛒 Total Sales</h3>
                    <h2 style="margin: 0.5rem 0;">{:,}</h2>
                    <p style="color: #6c757d; margin: 0;">Completed transactions</p>
                </div>
            """.format(kpi_data.total_sales), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #17a2b8; margin: 0;">📦 Products</h3>
                    <h2 style="margin: 0.5rem 0;">{:,}</h2>
                    <p style="color: #6c757d; margin: 0;">Active products</p>
                </div>
            """.format(kpi_data.total_products), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #ffc107; margin: 0;">👥 Customers</h3>
                    <h2 style="margin: 0.5rem 0;">{:,}</h2>
                    <p style="color: #6c757d; margin: 0;">Total customers</p>
                </div>
            """.format(kpi_data.total_customers), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts Section
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Sales by Month")
            
            sales_by_month_query = text("""
                SELECT 
                    DATE_FORMAT(sale_date, '%Y-%m') as month,
                    COUNT(*) as total_sales,
                    SUM(total_amount) as revenue
                FROM sales
                WHERE sale_type = 'INVOICE'
                GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
                ORDER BY month DESC
                LIMIT 12
            """)
            
            result = db.execute(sales_by_month_query).fetchall()
            sales_data = pd.DataFrame(result, columns=['month', 'total_sales', 'revenue'])
            
            if not sales_data.empty:
                sales_data['total_sales'] = pd.to_numeric(sales_data['total_sales'], errors='coerce').fillna(0).astype(int)
                sales_data['revenue'] = pd.to_numeric(sales_data['revenue'], errors='coerce').fillna(0)
            
            if not sales_data.empty:
                fig = px.bar(
                    sales_data,
                    x='month',
                    y='revenue',
                    title='Monthly Revenue',
                    labels={'month': 'Month', 'revenue': 'Revenue (VND)'},
                    color='revenue',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    showlegend=False,
                    height=400,
                    xaxis_title="Month",
                    yaxis_title="Revenue (VND)"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sales data available")
        
        with col2:
            st.markdown("### 🏪 Sales by Location")
            
            sales_by_location_query = text("""
                SELECT 
                    l.location_name,
                    COUNT(s.sale_id) as total_sales,
                    SUM(s.total_amount) as revenue
                FROM sales s
                JOIN sales_orders so ON s.order_id = so.order_id
                JOIN locations l ON so.location_id = l.location_id
                WHERE s.sale_type = 'INVOICE'
                GROUP BY l.location_id, l.location_name
                ORDER BY revenue DESC
                LIMIT 10
            """)
            
            result = db.execute(sales_by_location_query).fetchall()
            location_data = pd.DataFrame(result, columns=['location_name', 'total_sales', 'revenue'])
            
            if not location_data.empty:
                location_data['total_sales'] = pd.to_numeric(location_data['total_sales'], errors='coerce').fillna(0).astype(int)
                location_data['revenue'] = pd.to_numeric(location_data['revenue'], errors='coerce').fillna(0)
            
            if not location_data.empty:
                fig = px.pie(
                    location_data,
                    values='revenue',
                    names='location_name',
                    title='Revenue Distribution by Location',
                    hole=0.4
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No location data available")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Top Products
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔥 Top 10 Products by Sales")
            
            top_products_query = text("""
                SELECT 
                    p.product_name,
                    SUM(si.quantity) as total_quantity,
                    SUM(si.final_amount) as total_revenue
                FROM sales_items si
                JOIN products p ON si.product_id = p.product_id
                JOIN sales s ON si.sale_id = s.sale_id
                WHERE s.sale_type = 'INVOICE'
                GROUP BY p.product_id, p.product_name
                ORDER BY total_revenue DESC
                LIMIT 10
            """)
            
            result = db.execute(top_products_query).fetchall()
            top_products = pd.DataFrame(result, columns=['product_name', 'total_quantity', 'total_revenue'])
            
            if not top_products.empty:
                top_products['total_quantity'] = pd.to_numeric(top_products['total_quantity'], errors='coerce').fillna(0).astype(int)
                top_products['total_revenue'] = pd.to_numeric(top_products['total_revenue'], errors='coerce').fillna(0)
            
            if not top_products.empty:
                fig = px.bar(
                    top_products,
                    x='total_revenue',
                    y='product_name',
                    orientation='h',
                    title='Top 10 Products by Revenue',
                    labels={'total_revenue': 'Revenue (VND)', 'product_name': 'Product'},
                    color='total_revenue',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(
                    showlegend=False,
                    height=400,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No product data available")
        
        with col2:
            st.markdown("### 🚚 Delivery Status")
            
            delivery_status_query = text("""
                SELECT 
                    delivery_status,
                    COUNT(*) as count
                FROM deliveries
                GROUP BY delivery_status
            """)
            
            result = db.execute(delivery_status_query).fetchall()
            delivery_data = pd.DataFrame(result, columns=['delivery_status', 'count'])
            
            if not delivery_data.empty:
                delivery_data['count'] = pd.to_numeric(delivery_data['count'], errors='coerce').fillna(0).astype(int)
            
            if not delivery_data.empty:
                colors = {
                    'DELIVERED': '#28a745',
                    'SHIPPED': '#17a2b8',
                    'PENDING': '#ffc107',
                    'CANCELLED': '#dc3545'
                }
                
                fig = go.Figure(data=[go.Pie(
                    labels=delivery_data['delivery_status'],
                    values=delivery_data['count'],
                    hole=0.4,
                    marker_colors=[colors.get(status, '#6c757d') for status in delivery_data['delivery_status']]
                )])
                
                fig.update_layout(
                    title='Delivery Status Distribution',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No delivery data available")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Recent Sales Table
        st.markdown("### 📋 Recent Sales")
        
        recent_sales_query = text("""
            SELECT 
                s.sale_id,
                s.sale_date,
                c.first_name,
                c.last_name,
                l.location_name,
                s.total_amount,
                s.invoice_status,
                pm.method_name as payment_method
            FROM sales s
            JOIN sales_orders so ON s.order_id = so.order_id
            JOIN customers c ON so.customer_id = c.customer_id
            JOIN locations l ON so.location_id = l.location_id
            LEFT JOIN payment_methods pm ON s.payment_method_id = pm.payment_method_id
            WHERE s.sale_type = 'INVOICE'
            ORDER BY s.sale_date DESC
            LIMIT 20
        """)
        
        result = db.execute(recent_sales_query).fetchall()
        recent_sales = pd.DataFrame(result, columns=[
            'sale_id', 'sale_date', 'first_name', 'last_name', 'location_name',
            'total_amount', 'invoice_status', 'payment_method'
        ])
        
        if not recent_sales.empty:
            recent_sales['total_amount'] = pd.to_numeric(recent_sales['total_amount'], errors='coerce').fillna(0)
            recent_sales['customer_name'] = recent_sales['first_name'] + ' ' + recent_sales['last_name']
            recent_sales['total_amount'] = recent_sales['total_amount'].apply(lambda x: f"{x:,.0f} VND")
            
            display_df = recent_sales[[
                'sale_id', 'sale_date', 'customer_name', 'location_name',
                'total_amount', 'payment_method', 'invoice_status'
            ]]
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "sale_id": "Sale ID",
                    "sale_date": "Date",
                    "customer_name": "Customer",
                    "location_name": "Location",
                    "total_amount": "Amount",
                    "payment_method": "Payment",
                    "invoice_status": st.column_config.TextColumn(
                        "Status",
                        help="Invoice payment status"
                    )
                }
            )
        else:
            st.info("No recent sales data available")
        
    except Exception as e:
        st.error(f"❌ Error loading dashboard: {str(e)}")
    
    finally:
        db.close()