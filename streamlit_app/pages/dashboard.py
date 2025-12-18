import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from datetime import datetime, timedelta
from config.session import get_db_connection

def show():
    """Display lightweight dashboard with essential KPIs"""
    
    st.markdown("""
        <div class="main-header">
            <h1>🏠 Dashboard</h1>
            <p>Quick overview of key metrics</p>
        </div>
    """, unsafe_allow_html=True)
    
    db = get_db_connection()
    
    try:
        # Quick date filter
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            days_back = st.selectbox("Time Period", [7, 30, 90, 365], index=1, format_func=lambda x: f"Last {x} days")
        with col2:
            st.write("")  # Spacer
        with col3:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        st.markdown("---")
        
        # =====================================================
        # KPI CARDS - Simple metrics
        # =====================================================
        
        kpi_query = text("""
            SELECT 
                COUNT(DISTINCT s.sale_id) as total_orders,
                COALESCE(SUM(s.total_amount), 0) as total_revenue,
                COUNT(DISTINCT so.customer_id) as total_customers,
                COALESCE(AVG(s.total_amount), 0) as avg_order_value
            FROM sales s
            JOIN sales_orders so ON s.order_id = so.order_id
            WHERE s.sale_type = 'INVOICE'
                AND s.sale_date >= :start_date
        """)
        
        kpi = db.execute(kpi_query, {"start_date": start_date}).fetchone()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💰 Total Revenue",
                value=f"{kpi.total_revenue:,.0f} VND"
            )
        
        with col2:
            st.metric(
                label="🛒 Total Orders",
                value=f"{kpi.total_orders:,}"
            )
        
        with col3:
            st.metric(
                label="👥 Customers",
                value=f"{kpi.total_customers:,}"
            )
        
        with col4:
            st.metric(
                label="📊 Avg Order",
                value=f"{kpi.avg_order_value:,.0f} VND"
            )
        
        st.markdown("---")
        
        # =====================================================
        # CHARTS - 2x2 Grid
        # =====================================================
        
        col1, col2 = st.columns(2)
        
        # Chart 1: Daily Sales Trend
        with col1:
            st.markdown("### 📈 Daily Sales")
            
            trend_query = text("""
                SELECT 
                    DATE(sale_date) as date,
                    COUNT(*) as orders,
                    SUM(total_amount) as revenue
                FROM sales
                WHERE sale_type = 'INVOICE'
                    AND sale_date >= :start_date
                GROUP BY DATE(sale_date)
                ORDER BY date
            """)
            
            result = db.execute(trend_query, {"start_date": start_date}).fetchall()
            df = pd.DataFrame(result, columns=['date', 'orders', 'revenue'])
            
            if not df.empty:
                df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
                
                fig = px.line(
                    df,
                    x='date',
                    y='revenue',
                    markers=True,
                    labels={'date': 'Date', 'revenue': 'Revenue (VND)'}
                )
                fig.update_layout(height=300, showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data")
        
        # Chart 2: Top 5 Products
        with col2:
            st.markdown("### 🔥 Top 5 Products")
            
            products_query = text("""
                SELECT 
                    p.product_name,
                    SUM(si.final_amount) as revenue
                FROM sales_items si
                JOIN products p ON si.product_id = p.product_id
                JOIN sales s ON si.sale_id = s.sale_id
                WHERE s.sale_type = 'INVOICE'
                    AND s.sale_date >= :start_date
                GROUP BY p.product_id, p.product_name
                ORDER BY revenue DESC
                LIMIT 5
            """)
            
            result = db.execute(products_query, {"start_date": start_date}).fetchall()
            df = pd.DataFrame(result, columns=['product_name', 'revenue'])
            
            if not df.empty:
                df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
                
                fig = px.bar(
                    df,
                    y='product_name',
                    x='revenue',
                    orientation='h',
                    labels={'product_name': '', 'revenue': 'Revenue (VND)'},
                    color='revenue',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=300, showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data")
        
        # Chart 3: Sales by Region
        with col1:
            st.markdown("### 🌍 Sales by Region")
            
            region_query = text("""
                SELECT 
                    l.region,
                    COUNT(s.sale_id) as orders,
                    SUM(s.total_amount) as revenue
                FROM sales s
                JOIN sales_orders so ON s.order_id = so.order_id
                JOIN locations l ON so.location_id = l.location_id
                WHERE s.sale_type = 'INVOICE'
                    AND s.sale_date >= :start_date
                    AND l.region IS NOT NULL
                GROUP BY l.region
            """)
            
            result = db.execute(region_query, {"start_date": start_date}).fetchall()
            df = pd.DataFrame(result, columns=['region', 'orders', 'revenue'])
            
            if not df.empty:
                df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
                
                fig = px.pie(
                    df,
                    values='revenue',
                    names='region',
                    hole=0.4,
                    color_discrete_sequence=['#667eea', '#48bb78']
                )
                fig.update_layout(height=300, showlegend=True, margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data")
        
        # Chart 4: Delivery Status
        with col2:
            st.markdown("### 🚚 Delivery Status")
            
            delivery_query = text("""
                SELECT 
                    delivery_status,
                    COUNT(*) as count
                FROM deliveries
                WHERE created_at >= :start_date
                GROUP BY delivery_status
            """)
            
            result = db.execute(delivery_query, {"start_date": start_date}).fetchall()
            df = pd.DataFrame(result, columns=['delivery_status', 'count'])
            
            if not df.empty:
                df['count'] = pd.to_numeric(df['count'], errors='coerce')
                
                # Color mapping
                color_map = {
                    'DELIVERED': '#28a745',
                    'SHIPPED': '#17a2b8',
                    'PACKED': '#ffc107',
                    'CREATED': '#6c757d',
                    'FAILED': '#dc3545'
                }
                df['color'] = df['delivery_status'].map(color_map)
                
                fig = px.pie(
                    df,
                    values='count',
                    names='delivery_status',
                    hole=0.4,
                    color='delivery_status',
                    color_discrete_map=color_map
                )
                fig.update_layout(height=300, showlegend=True, margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data")
        
        st.markdown("---")
        
        # =====================================================
        # RECENT ACTIVITY - Compact table
        # =====================================================
        
        st.markdown("### 📋 Recent Orders (Last 10)")
        
        recent_query = text("""
            SELECT 
                s.sale_id,
                DATE_FORMAT(s.sale_date, '%Y-%m-%d %H:%i') as sale_date,
                CONCAT(c.first_name, ' ', c.last_name) as customer,
                l.location_name,
                s.total_amount,
                pm.method_name
            FROM sales s
            JOIN sales_orders so ON s.order_id = so.order_id
            JOIN customers c ON so.customer_id = c.customer_id
            JOIN locations l ON so.location_id = l.location_id
            LEFT JOIN payment_methods pm ON s.payment_method_id = pm.payment_method_id
            WHERE s.sale_type = 'INVOICE'
            ORDER BY s.sale_date DESC
            LIMIT 10
        """)
        
        result = db.execute(recent_query).fetchall()
        df = pd.DataFrame(result, columns=[
            'sale_id', 'sale_date', 'customer', 'location_name', 'total_amount', 'method_name'
        ])
        
        if not df.empty:
            df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
            df['amount_display'] = df['total_amount'].apply(lambda x: f"{x:,.0f} VND")
            
            st.dataframe(
                df[['sale_id', 'sale_date', 'customer', 'location_name', 'amount_display', 'method_name']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "sale_id": st.column_config.NumberColumn("ID", width="small"),
                    "sale_date": st.column_config.TextColumn("Date", width="medium"),
                    "customer": st.column_config.TextColumn("Customer", width="medium"),
                    "location_name": st.column_config.TextColumn("Location", width="medium"),
                    "amount_display": st.column_config.TextColumn("Amount", width="medium"),
                    "method_name": st.column_config.TextColumn("Payment", width="small")
                }
            )
        else:
            st.info("No recent orders")
        
        # Quick stats row at bottom
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        
        stats_query = text("""
            SELECT 
                COUNT(DISTINCT p.product_id) as products,
                COUNT(DISTINCT l.location_id) as locations,
                COUNT(DISTINCT e.employee_id) as employees,
                (SELECT COUNT(*) FROM inventory WHERE quantity < 100) as low_stock
            FROM products p
            CROSS JOIN locations l
            CROSS JOIN employees e
            WHERE p.status = 'ACTIVE'
                AND e.is_inactive = FALSE
        """)
        
        stats = db.execute(stats_query).fetchone()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📦 Active Products", f"{stats.products:,}")
        with col2:
            st.metric("🏪 Locations", f"{stats.locations:,}")
        with col3:
            st.metric("👨‍💼 Employees", f"{stats.employees:,}")
        with col4:
            st.metric("⚠️ Low Stock Items", f"{stats.low_stock:,}")
    
    except Exception as e:
        st.error(f"❌ Error loading dashboard: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
    
    finally:
        db.close()