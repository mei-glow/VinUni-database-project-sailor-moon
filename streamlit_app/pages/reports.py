import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text
from datetime import datetime, timedelta
from config.session import get_db_connection

def execute_query_to_df(db, query, params=None):
    """Helper function to execute query and return DataFrame with proper types"""
    if params:
        result = db.execute(query, params).fetchall()
    else:
        result = db.execute(query).fetchall()
    
    if not result:
        return pd.DataFrame()
    
    # Get column names from result keys
    columns = result[0]._fields if hasattr(result[0], '_fields') else result[0].keys()
    df = pd.DataFrame(result, columns=columns)
    
    # Convert numeric columns (common column names)
    numeric_cols = ['count', 'total_sales', 'revenue', 'total_spent', 'total_orders', 
                    'loyalty_points', 'units_sold', 'total_quantity', 'total_revenue',
                    'unit_margin', 'total_margin', 'total_deliveries', 'successful_deliveries',
                    'success_rate', 'costs', 'gross_profit', 'customer_count']
    
    for col in df.columns:
        if col in numeric_cols or any(x in col.lower() for x in ['amount', 'price', 'cost', 'revenue', 'total', 'count']):
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def show():
    """Display reports and analytics page"""
    
    st.markdown("""
        <div class="main-header">
            <h1>📊 Reports & Analytics</h1>
            <p>Business intelligence and data analysis</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Report selector
    report_type = st.selectbox(
        "Select Report Type",
        [
            "📈 Sales Analysis",
            "👥 Customer Analytics",
            "📦 Product Performance",
            "🚚 Delivery Analytics",
            "💰 Financial Reports"
        ]
    )
    
    if report_type == "📈 Sales Analysis":
        show_sales_analysis()
    elif report_type == "👥 Customer Analytics":
        show_customer_analytics()
    elif report_type == "📦 Product Performance":
        show_product_performance()
    elif report_type == "🚚 Delivery Analytics":
        show_delivery_analytics()
    elif report_type == "💰 Financial Reports":
        show_financial_reports()

def show_sales_analysis():
    """Sales analysis report"""
    st.markdown("### 📈 Sales Analysis")
    
    db = get_db_connection()
    
    try:
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=90))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        # Sales trend
        sales_trend_query = text("""
            SELECT 
                DATE(sale_date) as date,
                COUNT(*) as transactions,
                SUM(total_amount) as revenue
            FROM sales
            WHERE sale_type = 'INVOICE'
                AND sale_date BETWEEN :start AND :end
            GROUP BY DATE(sale_date)
            ORDER BY date
        """)
        
        sales_trend = execute_query_to_df(db, sales_trend_query, params={
            "start": start_date,
            "end": end_date
        })
        
        if not sales_trend.empty:
            # Line chart for revenue
            fig = px.line(
                sales_trend,
                x='date',
                y='revenue',
                title='Daily Revenue Trend',
                labels={'date': 'Date', 'revenue': 'Revenue (VND)'},
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_revenue = sales_trend['revenue'].sum()
                st.metric("Total Revenue", f"{total_revenue:,.0f} VND")
            
            with col2:
                total_transactions = sales_trend['transactions'].sum()
                st.metric("Transactions", f"{total_transactions:,.0f}")
            
            with col3:
                avg_order = total_revenue / total_transactions if total_transactions > 0 else 0
                st.metric("Avg Order Value", f"{avg_order:,.0f} VND")
            
            with col4:
                days = (end_date - start_date).days + 1
                daily_avg = total_revenue / days if days > 0 else 0
                st.metric("Daily Avg", f"{daily_avg:,.0f} VND")
            
            # Sales by location
            st.markdown("---")
            st.markdown("#### Sales by Location")
            
            location_sales_query = text("""
                SELECT 
                    l.location_name,
                    l.city,
                    COUNT(s.sale_id) as transactions,
                    SUM(s.total_amount) as revenue
                FROM sales s
                JOIN sales_orders so ON s.order_id = so.order_id
                JOIN locations l ON so.location_id = l.location_id
                WHERE s.sale_type = 'INVOICE'
                    AND s.sale_date BETWEEN :start AND :end
                GROUP BY l.location_id
                ORDER BY revenue DESC
            """)
            
            location_sales = execute_query_to_df(db, location_sales_query, params={
                "start": start_date,
                "end": end_date
            })
            
            if not location_sales.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(
                        location_sales.head(10),
                        x='revenue',
                        y='location_name',
                        orientation='h',
                        title='Top 10 Locations by Revenue',
                        labels={'revenue': 'Revenue (VND)', 'location_name': 'Location'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.pie(
                        location_sales.head(10),
                        values='transactions',
                        names='location_name',
                        title='Transaction Distribution',
                        hole=0.4
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("No sales data available for selected period")
    
    except Exception as e:
        st.error(f"❌ Error loading sales analysis: {str(e)}")
    
    finally:
        db.close()

def show_customer_analytics():
    """Customer analytics report"""
    st.markdown("### 👥 Customer Analytics")
    
    db = get_db_connection()
    
    try:
        # Customer segments
        segment_query = text("""
            SELECT 
                ll.level_name,
                COUNT(DISTINCT cl.customer_id) as customer_count,
                COALESCE(SUM(s.total_amount), 0) as total_spent
            FROM customer_loyalty cl
            JOIN loyalty_levels ll ON cl.loyalty_id = ll.loyalty_id
            LEFT JOIN sales_orders so ON cl.customer_id = so.customer_id
            LEFT JOIN sales s ON so.order_id = s.order_id AND s.sale_type = 'INVOICE'
            GROUP BY ll.loyalty_id, ll.level_name
            ORDER BY ll.min_total_spent DESC
        """)
        
        segments = execute_query_to_df(db, segment_query)
        
        if not segments.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    segments,
                    x='level_name',
                    y='customer_count',
                    title='Customers by Loyalty Level',
                    labels={'level_name': 'Loyalty Level', 'customer_count': 'Customers'},
                    color='customer_count',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.pie(
                    segments,
                    values='total_spent',
                    names='level_name',
                    title='Revenue by Loyalty Level',
                    hole=0.4
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Top customers
        st.markdown("#### 🏆 Top Customers")
        
        top_customers_query = text("""
            SELECT 
                c.customer_id,
                CONCAT(c.first_name, ' ', c.last_name) as name,
                c.email,
                cl.loyalty_points,
                ll.level_name,
                COUNT(DISTINCT so.order_id) as total_orders,
                COALESCE(SUM(s.total_amount), 0) as total_spent
            FROM customers c
            LEFT JOIN customer_loyalty cl ON c.customer_id = cl.customer_id
            LEFT JOIN loyalty_levels ll ON cl.loyalty_id = ll.loyalty_id
            LEFT JOIN sales_orders so ON c.customer_id = so.customer_id
            LEFT JOIN sales s ON so.order_id = s.order_id AND s.sale_type = 'INVOICE'
            GROUP BY c.customer_id
            ORDER BY total_spent DESC
            LIMIT 20
        """)
        
        top_customers = execute_query_to_df(db, top_customers_query)
        
        if not top_customers.empty:
            top_customers['total_spent_display'] = top_customers['total_spent'].apply(
                lambda x: f"{x:,.0f} VND"
            )
            
            st.dataframe(
                top_customers[[
                    'customer_id', 'name', 'email', 'level_name',
                    'total_orders', 'loyalty_points', 'total_spent_display'
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "customer_id": "ID",
                    "name": "Name",
                    "email": "Email",
                    "level_name": "Loyalty Level",
                    "total_orders": "Orders",
                    "loyalty_points": "Points",
                    "total_spent_display": "Total Spent"
                }
            )
    
    except Exception as e:
        st.error(f"❌ Error loading customer analytics: {str(e)}")
    
    finally:
        db.close()

def show_product_performance():
    """Product performance report"""
    st.markdown("### 📦 Product Performance")
    
    db = get_db_connection()
    
    try:
        # Top products by revenue
        top_products_query = text("""
            SELECT 
                p.product_id,
                p.product_name,
                pc.product_group,
                SUM(si.quantity) as units_sold,
                SUM(si.final_amount) as revenue,
                (p.unit_price - p.cost) as unit_margin,
                SUM((p.unit_price - p.cost) * si.quantity) as total_margin
            FROM sales_items si
            JOIN products p ON si.product_id = p.product_id
            JOIN product_class pc ON p.class_id = pc.class_id
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE s.sale_type = 'INVOICE'
            GROUP BY p.product_id
            ORDER BY revenue DESC
            LIMIT 20
        """)
        
        top_products = execute_query_to_df(db, top_products_query)
        
        if not top_products.empty:
            # Format display
            top_products['revenue_display'] = top_products['revenue'].apply(lambda x: f"{x:,.0f} VND")
            top_products['margin_display'] = top_products['total_margin'].apply(lambda x: f"{x:,.0f} VND")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    top_products.head(10),
                    x='revenue',
                    y='product_name',
                    orientation='h',
                    title='Top 10 Products by Revenue',
                    labels={'revenue': 'Revenue (VND)', 'product_name': 'Product'},
                    color='revenue',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    top_products.head(10),
                    x='units_sold',
                    y='product_name',
                    orientation='h',
                    title='Top 10 Products by Units Sold',
                    labels={'units_sold': 'Units', 'product_name': 'Product'},
                    color='units_sold',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            # Product table
            st.markdown("#### 📋 Detailed Product Performance")
            
            st.dataframe(
                top_products[[
                    'product_id', 'product_name', 'product_group',
                    'units_sold', 'revenue_display', 'margin_display'
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "product_id": "ID",
                    "product_name": "Product",
                    "product_group": "Group",
                    "units_sold": "Units Sold",
                    "revenue_display": "Revenue",
                    "margin_display": "Profit"
                }
            )
    
    except Exception as e:
        st.error(f"❌ Error loading product performance: {str(e)}")
    
    finally:
        db.close()

def show_delivery_analytics():
    """Delivery analytics report"""
    st.markdown("### 🚚 Delivery Analytics")
    
    db = get_db_connection()
    
    try:
        # Delivery status distribution
        status_query = text("""
            SELECT 
                delivery_status,
                COUNT(*) as count
            FROM deliveries
            GROUP BY delivery_status
        """)
        
        status_data = execute_query_to_df(db, status_query)
        
        if not status_data.empty:
            fig = px.pie(
                status_data,
                values='count',
                names='delivery_status',
                title='Delivery Status Distribution',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Delivery performance by vendor
            vendor_query = text("""
                SELECT 
                    dv.company_name,
                    COUNT(d.delivery_id) as total_deliveries,
                    SUM(CASE WHEN d.delivery_status = 'DELIVERED' THEN 1 ELSE 0 END) as successful_deliveries,
                    ROUND(SUM(CASE WHEN d.delivery_status = 'DELIVERED' THEN 1 ELSE 0 END) * 100.0 / COUNT(d.delivery_id), 2) as success_rate
                FROM deliveries d
                JOIN delivery_vendors dv ON d.vendor_id = dv.vendor_id
                GROUP BY dv.vendor_id
                ORDER BY success_rate DESC
            """)
            
            vendor_data = execute_query_to_df(db, vendor_query)
            
            if not vendor_data.empty:
                st.markdown("#### 📊 Delivery Vendor Performance")
                st.dataframe(
                    vendor_data,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "company_name": "Vendor",
                        "total_deliveries": "Total Deliveries",
                        "successful_deliveries": "Successful",
                        "success_rate": st.column_config.NumberColumn(
                            "Success Rate",
                            format="%.2f%%"
                        )
                    }
                )
    
    except Exception as e:
        st.error(f"❌ Error loading delivery analytics: {str(e)}")
    
    finally:
        db.close()

def show_financial_reports():
    """Financial reports"""
    st.markdown("### 💰 Financial Reports")
    
    db = get_db_connection()
    
    try:
        # Revenue and costs
        financial_query = text("""
            SELECT 
                DATE_FORMAT(s.sale_date, '%Y-%m') as month,
                SUM(s.total_amount) as revenue,
                SUM(si.quantity * p.cost) as costs,
                SUM(s.total_amount - si.quantity * p.cost) as gross_profit
            FROM sales s
            JOIN sales_items si ON s.sale_id = si.sale_id
            JOIN products p ON si.product_id = p.product_id
            WHERE s.sale_type = 'INVOICE'
            GROUP BY DATE_FORMAT(s.sale_date, '%Y-%m')
            ORDER BY month DESC
            LIMIT 12
        """)
        
        financial_data = execute_query_to_df(db, financial_query)
        
        if not financial_data.empty:
            # Format display
            financial_data['revenue_display'] = financial_data['revenue'].apply(lambda x: f"{x:,.0f}")
            financial_data['costs_display'] = financial_data['costs'].apply(lambda x: f"{x:,.0f}")
            financial_data['profit_display'] = financial_data['gross_profit'].apply(lambda x: f"{x:,.0f}")
            financial_data['margin'] = (financial_data['gross_profit'] / financial_data['revenue'] * 100).round(2)
            
            # Line chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=financial_data['month'],
                y=financial_data['revenue'],
                name='Revenue',
                mode='lines+markers',
                line=dict(color='#667eea', width=3)
            ))
            fig.add_trace(go.Scatter(
                x=financial_data['month'],
                y=financial_data['costs'],
                name='Costs',
                mode='lines+markers',
                line=dict(color='#f56565', width=3)
            ))
            fig.add_trace(go.Scatter(
                x=financial_data['month'],
                y=financial_data['gross_profit'],
                name='Gross Profit',
                mode='lines+markers',
                line=dict(color='#48bb78', width=3)
            ))
            
            fig.update_layout(
                title='Monthly Financial Performance',
                xaxis_title='Month',
                yaxis_title='Amount (VND)',
                height=500,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Financial table
            st.dataframe(
                financial_data[[
                    'month', 'revenue_display', 'costs_display',
                    'profit_display', 'margin'
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "month": "Month",
                    "revenue_display": "Revenue (VND)",
                    "costs_display": "Costs (VND)",
                    "profit_display": "Gross Profit (VND)",
                    "margin": st.column_config.NumberColumn(
                        "Margin %",
                        format="%.2f%%"
                    )
                }
            )
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_revenue = financial_data['revenue'].sum()
                st.metric("Total Revenue", f"{total_revenue:,.0f} VND")
            
            with col2:
                total_profit = financial_data['gross_profit'].sum()
                st.metric("Total Profit", f"{total_profit:,.0f} VND")
            
            with col3:
                avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
                st.metric("Avg Margin", f"{avg_margin:.2f}%")
    
    except Exception as e:
        st.error(f"❌ Error loading financial reports: {str(e)}")
    
    finally:
        db.close()