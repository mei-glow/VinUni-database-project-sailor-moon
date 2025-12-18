import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text
from datetime import datetime, timedelta
from config.session import get_db_connection
from utils.auth import check_permission

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
    
    # Convert numeric columns
    numeric_cols = ['count', 'total_sales', 'revenue', 'total_spent', 'total_orders', 
                    'loyalty_points', 'units_sold', 'total_quantity', 'total_revenue',
                    'unit_margin', 'total_margin', 'total_deliveries', 'successful_deliveries',
                    'success_rate', 'costs', 'gross_profit', 'customer_count', 'quantity_sold',
                    'contribution_percent', 'gross_margin', 'gross_margin_percent', 'bonus_amount',
                    'deliveries_count', 'success_count', 'failure_count', 'utilization_rate_percent',
                    'number_of_orders', 'number_of_returns', 'return_value', 'return_rate_percent',
                    'orders_handled', 'avg_order_value', 'deliveries_handled', 'delivery_success_rate',
                    'deliveries_per_vehicle', 'current_stock_quantity', 'total_movement', 'sales_volume',
                    'bonus_earned', 'deliveries_completed', 'net_sales', 'margin', 'order_count',
                    'total_order_value', 'total_value', 'usage_count', 'revenue_contribution',
                    'success_rate_percent', 'points_balance']
    
    for col in df.columns:
        if col in numeric_cols or any(x in col.lower() for x in ['amount', 'price', 'cost', 'revenue', 'total', 'count', 'percent', 'rate', 'margin', 'bonus', 'value', 'points', 'quantity']):
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def format_currency(value):
    """Format number as VND currency"""
    if pd.isna(value):
        return "0 VND"
    return f"{value:,.0f} VND"

def show():
    """Display reports and analytics page"""
    
    st.markdown("""
        <div class="main-header">
            <h1>📊 Reports & Analytics</h1>
            <p>Business intelligence and data analysis</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check if user is authenticated
    if "user" not in st.session_state:
        st.error("⛔ Please login to view reports")
        return
    
    # Debug: Show user permissions
    with st.expander("🔍 Debug: View My Permissions", expanded=False):
        if "permissions" in st.session_state:
            st.write("**Your Permissions:**")
            st.write(st.session_state.permissions)
        else:
            st.write("No permissions loaded yet")
            if st.button("Reload Permissions"):
                from utils.auth import get_user_permissions
                st.session_state.permissions = get_user_permissions(st.session_state.user["user_id"])
                st.rerun()
    
    # Build tabs based on permissions
    available_tabs = []
    tab_functions = {}
    
    if check_permission("DASHBOARD_SALES_VIEW"):
        available_tabs.extend(["📈 Sales Analysis", "👥 Customer Analytics", "📦 Product Performance"])
        tab_functions["📈 Sales Analysis"] = show_sales_analysis
        tab_functions["👥 Customer Analytics"] = show_customer_analytics
        tab_functions["📦 Product Performance"] = show_product_performance
    
    if check_permission("DASHBOARD_DELIVERY_VIEW"):
        available_tabs.append("🚚 Delivery Analytics")
        tab_functions["🚚 Delivery Analytics"] = show_delivery_analytics
    
    if check_permission("DASHBOARD_EXECUTIVE_VIEW"):
        available_tabs.extend(["💰 Financial Reports", "🎯 Executive Dashboard"])
        tab_functions["💰 Financial Reports"] = show_financial_reports
        tab_functions["🎯 Executive Dashboard"] = show_executive_dashboard
    
    if check_permission("DASHBOARD_INVENTORY_VIEW"):
        available_tabs.append("📊 Inventory Reports")
        tab_functions["📊 Inventory Reports"] = show_inventory_reports
    
    if check_permission("DASHBOARD_HR_VIEW"):
        available_tabs.append("👨‍💼 HR & Bonus Reports")
        tab_functions["👨‍💼 HR & Bonus Reports"] = show_hr_bonus_reports
    
    if not available_tabs:
        st.error("⛔ You don't have permission to view any reports")
        st.info("Contact your administrator to grant dashboard permissions")
        return
    
    # Create tabs
    tabs = st.tabs(available_tabs)
    
    for i, tab_name in enumerate(available_tabs):
        with tabs[i]:
            tab_functions[tab_name]()

# =====================================================
# SALES ANALYSIS (DASHBOARD_SALES_VIEW)
# =====================================================

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
                st.metric("Total Revenue", format_currency(total_revenue))
            
            with col2:
                total_transactions = sales_trend['transactions'].sum()
                st.metric("Transactions", f"{total_transactions:,.0f}")
            
            with col3:
                avg_order = total_revenue / total_transactions if total_transactions > 0 else 0
                st.metric("Avg Order Value", format_currency(avg_order))
            
            with col4:
                days = (end_date - start_date).days + 1
                daily_avg = total_revenue / days if days > 0 else 0
                st.metric("Daily Avg", format_currency(daily_avg))
            
            # Sales by payment method
            st.markdown("---")
            st.markdown("#### 💳 Sales by Payment Method")
            
            payment_query = text("SELECT * FROM vw_sales_by_payment_method")
            payment_data = execute_query_to_df(db, payment_query)
            
            if not payment_data.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(
                        payment_data,
                        values='revenue',
                        names='method_name',
                        title='Revenue by Payment Method',
                        hole=0.4
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(
                        payment_data,
                        x='method_name',
                        y='number_of_orders',
                        title='Orders by Payment Method',
                        labels={'method_name': 'Payment Method', 'number_of_orders': 'Orders'},
                        color='number_of_orders',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Employee performance
            st.markdown("---")
            st.markdown("#### 👨‍💼 Employee Performance")
            
            emp_perf_query = text("""
                SELECT * FROM vw_sales_employee_location_performance
                ORDER BY total_sales DESC
                LIMIT 10
            """)
            emp_perf = execute_query_to_df(db, emp_perf_query)
            
            if not emp_perf.empty:
                fig = px.bar(
                    emp_perf,
                    x='total_sales',
                    y='employee_name',
                    orientation='h',
                    title='Top 10 Employees by Sales',
                    labels={'total_sales': 'Total Sales (VND)', 'employee_name': 'Employee'},
                    color='total_sales',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            # Revenue & Gross Margin
            st.markdown("---")
            st.markdown("#### 💹 Revenue & Gross Margin by Product")
            
            gm_query = text("""
                SELECT 
                    product_name,
                    class_name,
                    total_revenue,
                    gross_margin,
                    gross_margin_percent
                FROM vw_sales_revenue_gm
                ORDER BY total_revenue DESC
                LIMIT 20
            """)
            gm_data = execute_query_to_df(db, gm_query)
            
            if not gm_data.empty:
                gm_data['revenue_display'] = gm_data['total_revenue'].apply(format_currency)
                gm_data['margin_display'] = gm_data['gross_margin'].apply(format_currency)
                
                st.dataframe(
                    gm_data[[
                        'product_name', 'class_name', 'revenue_display',
                        'margin_display', 'gross_margin_percent'
                    ]],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "product_name": "Product",
                        "class_name": "Category",
                        "revenue_display": "Revenue",
                        "margin_display": "Gross Margin",
                        "gross_margin_percent": st.column_config.NumberColumn(
                            "GM %",
                            format="%.2f%%"
                        )
                    }
                )
        else:
            st.info("No sales data available for selected period")
    
    except Exception as e:
        st.error(f"❌ Error loading sales analysis: {str(e)}")
    
    finally:
        db.close()

# =====================================================
# CUSTOMER ANALYTICS (DASHBOARD_SALES_VIEW)
# =====================================================

def show_customer_analytics():
    """Customer analytics report"""
    st.markdown("### 👥 Customer Analytics")
    
    db = get_db_connection()
    
    try:
        # Loyalty level distribution
        st.markdown("#### 🏆 Loyalty Level Distribution")
        
        loyalty_query = text("SELECT * FROM vw_loyalty_level_distribution")
        loyalty_data = execute_query_to_df(db, loyalty_query)
        
        if not loyalty_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    loyalty_data,
                    x='loyalty_tier',
                    y='customer_count',
                    title='Customers by Loyalty Level',
                    labels={'loyalty_tier': 'Loyalty Level', 'customer_count': 'Customers'},
                    color='customer_count',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.pie(
                    loyalty_data,
                    values='points_balance',
                    names='loyalty_tier',
                    title='Points Distribution by Loyalty Level',
                    hole=0.4
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Top customers
        st.markdown("---")
        st.markdown("#### 💎 Top Customers")
        
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
            top_customers['total_spent_display'] = top_customers['total_spent'].apply(format_currency)
            
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
        
        # Promotion effectiveness
        st.markdown("---")
        st.markdown("#### 🎁 Promotion Effectiveness")
        
        promo_query = text("SELECT * FROM vw_promotion_effectiveness ORDER BY revenue_contribution DESC")
        promo_data = execute_query_to_df(db, promo_query)
        
        if not promo_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    promo_data.head(10),
                    x='usage_count',
                    y='promotion_code',
                    orientation='h',
                    title='Top Promotions by Usage',
                    labels={'usage_count': 'Times Used', 'promotion_code': 'Promotion Code'},
                    color='usage_count',
                    color_continuous_scale='Oranges'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                promo_data['revenue_display'] = promo_data['revenue_contribution'].apply(format_currency)
                st.dataframe(
                    promo_data.head(10)[['promotion_code', 'rule_type', 'usage_count', 'revenue_display', 'contribution_percent']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "promotion_code": "Code",
                        "rule_type": "Type",
                        "usage_count": "Usage",
                        "revenue_display": "Revenue",
                        "contribution_percent": st.column_config.NumberColumn(
                            "Contribution %",
                            format="%.2f%%"
                        )
                    }
                )
    
    except Exception as e:
        st.error(f"❌ Error loading customer analytics: {str(e)}")
    
    finally:
        db.close()

# =====================================================
# PRODUCT PERFORMANCE (DASHBOARD_SALES_VIEW)
# =====================================================

def show_product_performance():
    """Product performance report"""
    st.markdown("### 📦 Product Performance")
    
    db = get_db_connection()
    
    try:
        # Product sales performance
        product_query = text("""
            SELECT * FROM vw_product_sales_performance
            ORDER BY revenue DESC
            LIMIT 20
        """)
        
        product_data = execute_query_to_df(db, product_query)
        
        if not product_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    product_data.head(10),
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
                    product_data.head(10),
                    x='quantity_sold',
                    y='product_name',
                    orientation='h',
                    title='Top 10 Products by Units Sold',
                    labels={'quantity_sold': 'Units', 'product_name': 'Product'},
                    color='quantity_sold',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            # Product class performance
            st.markdown("---")
            st.markdown("#### 📊 Performance by Product Category")
            
            class_query = text("SELECT * FROM vw_product_class_performance ORDER BY revenue DESC")
            class_data = execute_query_to_df(db, class_query)
            
            if not class_data.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(
                        class_data,
                        values='revenue',
                        names='class_name',
                        title='Revenue by Product Category',
                        hole=0.4
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    class_data['revenue_display'] = class_data['revenue'].apply(format_currency)
                    st.dataframe(
                        class_data[['class_name', 'revenue_display', 'contribution_percent']],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "class_name": "Category",
                            "revenue_display": "Revenue",
                            "contribution_percent": st.column_config.NumberColumn(
                                "Contribution %",
                                format="%.2f%%"
                            )
                        }
                    )
            
            # Detailed product table
            st.markdown("---")
            st.markdown("#### 📋 Detailed Product Performance")
            
            product_data['revenue_display'] = product_data['revenue'].apply(format_currency)
            
            st.dataframe(
                product_data[[
                    'product_id', 'product_name', 'quantity_sold', 'revenue_display'
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "product_id": "ID",
                    "product_name": "Product",
                    "quantity_sold": "Units Sold",
                    "revenue_display": "Revenue"
                }
            )
    
    except Exception as e:
        st.error(f"❌ Error loading product performance: {str(e)}")
    
    finally:
        db.close()

# =====================================================
# DELIVERY ANALYTICS (DASHBOARD_DELIVERY_VIEW)
# =====================================================

def show_delivery_analytics():
    """Delivery analytics report"""
    st.markdown("### 🚚 Delivery Analytics")
    
    if not check_permission("DASHBOARD_DELIVERY_VIEW"):
        st.error("⛔ You don't have permission to view delivery analytics")
        return
    
    db = get_db_connection()
    
    try:
        # Delivery volume by type
        st.markdown("#### 📦 Delivery Volume by Type")
        
        volume_query = text("SELECT * FROM vw_delivery_volume_by_type")
        volume_data = execute_query_to_df(db, volume_query)
        
        if not volume_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    volume_data,
                    values='number_of_deliveries',
                    names='delivery_type',
                    title='Deliveries by Type',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    volume_data,
                    x='delivery_type',
                    y='number_of_deliveries',
                    title='Delivery Count by Type',
                    labels={'delivery_type': 'Type', 'number_of_deliveries': 'Count'},
                    color='number_of_deliveries',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Vendor performance
        st.markdown("---")
        st.markdown("#### 🏢 Delivery Vendor Performance")
        
        vendor_query = text("SELECT * FROM vw_delivery_vendor_performance ORDER BY success_rate_percent DESC")
        vendor_data = execute_query_to_df(db, vendor_query)
        
        if not vendor_data.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Success',
                x=vendor_data['vendor_name'],
                y=vendor_data['success_count'],
                marker_color='green'
            ))
            
            fig.add_trace(go.Bar(
                name='Failure',
                x=vendor_data['vendor_name'],
                y=vendor_data['failure_count'],
                marker_color='red'
            ))
            
            fig.update_layout(
                title='Vendor Performance: Success vs Failure',
                xaxis_title='Vendor',
                yaxis_title='Deliveries',
                barmode='stack',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(
                vendor_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "vendor_name": "Vendor",
                    "deliveries_count": "Total Deliveries",
                    "success_count": "Successful",
                    "failure_count": "Failed",
                    "success_rate_percent": st.column_config.NumberColumn(
                        "Success Rate",
                        format="%.2f%%"
                    )
                }
            )
        
        # Employee performance
        st.markdown("---")
        st.markdown("#### 👨‍💼 Delivery Staff Performance")
        
        emp_query = text("""
            SELECT * FROM vw_delivery_employee_performance 
            ORDER BY deliveries_handled DESC
            LIMIT 15
        """)
        emp_data = execute_query_to_df(db, emp_query)
        
        if not emp_data.empty:
            fig = px.bar(
                emp_data,
                x='deliveries_handled',
                y='delivery_staff',
                orientation='h',
                title='Top Delivery Staff by Volume',
                labels={'deliveries_handled': 'Deliveries', 'delivery_staff': 'Staff'},
                color='delivery_success_rate',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Vehicle utilization
        st.markdown("---")
        st.markdown("#### 🚗 Vehicle Utilization")
        
        vehicle_query = text("SELECT * FROM vw_delivery_vehicle_utilization ORDER BY deliveries_per_vehicle DESC")
        vehicle_data = execute_query_to_df(db, vehicle_query)
        
        if not vehicle_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    vehicle_data.head(10),
                    x='deliveries_per_vehicle',
                    y='plate_number',
                    orientation='h',
                    title='Top 10 Vehicles by Usage',
                    labels={'deliveries_per_vehicle': 'Deliveries', 'plate_number': 'Vehicle'},
                    color='utilization_rate_percent',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.dataframe(
                    vehicle_data,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "vehicle_id": "ID",
                        "plate_number": "Plate Number",
                        "deliveries_per_vehicle": "Deliveries",
                        "utilization_rate_percent": st.column_config.NumberColumn(
                            "Utilization %",
                            format="%.2f%%"
                        )
                    }
                )
    
    except Exception as e:
        st.error(f"❌ Error loading delivery analytics: {str(e)}")
    
    finally:
        db.close()

# =====================================================
# FINANCIAL REPORTS (DASHBOARD_EXECUTIVE_VIEW)
# =====================================================

def show_financial_reports():
    """Financial reports"""
    st.markdown("### 💰 Financial Reports")
    
    if not check_permission("DASHBOARD_EXECUTIVE_VIEW"):
        st.error("⛔ You don't have permission to view financial reports")
        return
    
    db = get_db_connection()
    
    try:
        # Revenue and costs
        financial_query = text("""
            SELECT 
                DATE_FORMAT(s.sale_date, '%Y-%m') as month,
                SUM(s.total_amount) as revenue,
                SUM(ABS(si.quantity) * p.cost) as costs,
                SUM(s.total_amount - ABS(si.quantity) * p.cost) as gross_profit
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
                st.metric("Total Revenue", format_currency(total_revenue))
            
            with col2:
                total_profit = financial_data['gross_profit'].sum()
                st.metric("Total Profit", format_currency(total_profit))
            
            with col3:
                avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
                st.metric("Avg Margin", f"{avg_margin:.2f}%")
        
        # Sales Returns Analysis
        st.markdown("---")
        st.markdown("#### 🔄 Sales Returns Analysis")
        
        returns_query = text("SELECT * FROM vw_sales_returns_analysis ORDER BY return_value DESC LIMIT 20")
        returns_data = execute_query_to_df(db, returns_query)
        
        if not returns_data.empty:
            returns_data['return_value_display'] = returns_data['return_value'].apply(format_currency)
            
            st.dataframe(
                returns_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "return_sale_id": "Return ID",
                    "original_sale_id": "Original Sale ID",
                    "number_of_returns": "Items Returned",
                    "return_value_display": "Return Value",
                    "return_rate_percent": st.column_config.NumberColumn(
                        "Return Rate %",
                        format="%.2f%%"
                    )
                }
            )
    
    except Exception as e:
        st.error(f"❌ Error loading financial reports: {str(e)}")
    
    finally:
        db.close()

# =====================================================
# INVENTORY REPORTS (DASHBOARD_INVENTORY_VIEW)
# =====================================================

def show_inventory_reports():
    """Inventory reports"""
    st.markdown("### 📊 Inventory Reports")
    
    if not check_permission("DASHBOARD_INVENTORY_VIEW"):
        st.error("⛔ You don't have permission to view inventory reports")
        return
    
    db = get_db_connection()
    
    try:
        # Current inventory status
        st.markdown("#### 📦 Current Inventory Status")
        
        inventory_query = text("""
            SELECT * FROM vw_inventory_current_status
            ORDER BY current_stock_quantity ASC
            LIMIT 50
        """)
        inventory_data = execute_query_to_df(db, inventory_query)
        
        if not inventory_data.empty:
            # Low stock items
            low_stock = inventory_data[inventory_data['stock_status'] == 'LOW']
            
            if not low_stock.empty:
                st.warning(f"⚠️ {len(low_stock)} items with LOW stock levels")
                
                fig = px.bar(
                    low_stock.head(20),
                    x='current_stock_quantity',
                    y='product_name',
                    orientation='h',
                    title='Low Stock Items',
                    labels={'current_stock_quantity': 'Quantity', 'product_name': 'Product'},
                    color='current_stock_quantity',
                    color_continuous_scale='Reds'
                )
                fig.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            # Full inventory table
            st.markdown("#### 📋 All Inventory Items")
            st.dataframe(
                inventory_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "product_name": "Product",
                    "location_name": "Location",
                    "current_stock_quantity": "Stock",
                    "stock_status": "Status"
                }
            )
        
        # Inventory movement summary
        st.markdown("---")
        st.markdown("#### 📈 Inventory Movement Summary")
        
        movement_query = text("""
            SELECT 
                change_type,
                period,
                SUM(total_quantity) as total_movement
            FROM vw_inventory_movement_summary
            WHERE period >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY change_type, period
            ORDER BY period DESC
        """)
        movement_data = execute_query_to_df(db, movement_query)
        
        if not movement_data.empty:
            # Pivot for better visualization
            movement_pivot = movement_data.pivot(
                index='period',
                columns='change_type',
                values='total_movement'
            ).fillna(0)
            
            fig = go.Figure()
            
            for col in movement_pivot.columns:
                fig.add_trace(go.Scatter(
                    x=movement_pivot.index,
                    y=movement_pivot[col],
                    name=col,
                    mode='lines+markers'
                ))
            
            fig.update_layout(
                title='Inventory Movement by Type (Last 30 Days)',
                xaxis_title='Date',
                yaxis_title='Quantity',
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Error loading inventory reports: {str(e)}")
    
    finally:
        db.close()

# =====================================================
# HR & BONUS REPORTS (DASHBOARD_HR_VIEW)
# =====================================================

def show_hr_bonus_reports():
    """HR and bonus reports"""
    st.markdown("### 👨‍💼 HR & Bonus Reports")
    
    if not check_permission("DASHBOARD_HR_VIEW"):
        st.error("⛔ You don't have permission to view HR reports")
        return
    
    db = get_db_connection()
    
    try:
        # Employee sales bonus
        st.markdown("#### 💰 Employee Sales Bonus")
        
        sales_bonus_query = text("""
            SELECT * FROM vw_employee_sales_bonus
            ORDER BY bonus_amount DESC
            LIMIT 20
        """)
        sales_bonus_data = execute_query_to_df(db, sales_bonus_query)
        
        if not sales_bonus_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    sales_bonus_data.head(10),
                    x='bonus_amount',
                    y='employee_name',
                    orientation='h',
                    title='Top 10 Employees by Bonus',
                    labels={'bonus_amount': 'Bonus (VND)', 'employee_name': 'Employee'},
                    color='bonus_amount',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                sales_bonus_data['sales_display'] = sales_bonus_data['sales_volume'].apply(format_currency)
                sales_bonus_data['bonus_display'] = sales_bonus_data['bonus_amount'].apply(format_currency)
                
                st.dataframe(
                    sales_bonus_data.head(10)[['employee_name', 'bonus_type', 'sales_display', 'bonus_display']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "employee_name": "Employee",
                        "bonus_type": "Type",
                        "sales_display": "Sales Volume",
                        "bonus_display": "Bonus"
                    }
                )
        
        # Delivery bonus
        st.markdown("---")
        st.markdown("#### 🚚 Delivery Staff Bonus")
        
        delivery_bonus_query = text("""
            SELECT * FROM vw_delivery_bonus_summary
            ORDER BY bonus_earned DESC
            LIMIT 20
        """)
        delivery_bonus_data = execute_query_to_df(db, delivery_bonus_query)
        
        if not delivery_bonus_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    delivery_bonus_data.head(10),
                    x='bonus_earned',
                    y='delivery_staff',
                    orientation='h',
                    title='Top 10 Delivery Staff by Bonus',
                    labels={'bonus_earned': 'Bonus (VND)', 'delivery_staff': 'Staff'},
                    color='bonus_earned',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                delivery_bonus_data['bonus_display'] = delivery_bonus_data['bonus_earned'].apply(format_currency)
                
                st.dataframe(
                    delivery_bonus_data.head(10)[['delivery_staff', 'deliveries_completed', 'rule_type', 'bonus_display']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "delivery_staff": "Staff",
                        "deliveries_completed": "Deliveries",
                        "rule_type": "Type",
                        "bonus_display": "Bonus Earned"
                    }
                )
        
        # Total bonus summary
        st.markdown("---")
        st.markdown("#### 📊 Total Bonus Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_sales_bonus = sales_bonus_data['bonus_amount'].sum() if not sales_bonus_data.empty else 0
            st.metric("Total Sales Bonus", format_currency(total_sales_bonus))
        
        with col2:
            total_delivery_bonus = delivery_bonus_data['bonus_earned'].sum() if not delivery_bonus_data.empty else 0
            st.metric("Total Delivery Bonus", format_currency(total_delivery_bonus))
        
        with col3:
            total_bonus = total_sales_bonus + total_delivery_bonus
            st.metric("Total Bonus Payout", format_currency(total_bonus))
    
    except Exception as e:
        st.error(f"❌ Error loading HR & bonus reports: {str(e)}")
    
    finally:
        db.close()

# =====================================================
# EXECUTIVE DASHBOARD (DASHBOARD_EXECUTIVE_VIEW)
# =====================================================

def show_executive_dashboard():
    """Executive dashboard"""
    st.markdown("### 🎯 Executive Dashboard")
    
    if not check_permission("DASHBOARD_EXECUTIVE_VIEW"):
        st.error("⛔ You don't have permission to view executive dashboard")
        return
    
    db = get_db_connection()
    
    try:
        # Executive KPI overview
        st.markdown("#### 📊 Key Performance Indicators")
        
        kpi_query = text("""
            SELECT * FROM vw_executive_kpi_overview
            WHERE period >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            ORDER BY period DESC
        """)
        kpi_data = execute_query_to_df(db, kpi_query)
        
        if not kpi_data.empty:
            # Latest KPIs
            latest = kpi_data.iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Net Sales", format_currency(latest['net_sales']))
            
            with col2:
                st.metric("Gross Margin %", f"{latest['gross_margin_percent']:.2f}%")
            
            with col3:
                st.metric("Return Rate %", f"{latest['return_rate_percent']:.2f}%")
            
            with col4:
                st.metric("Delivery Success %", f"{latest['delivery_success_rate']:.2f}%")
            
            # KPI trends
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=kpi_data['period'],
                y=kpi_data['net_sales'],
                name='Net Sales',
                yaxis='y',
                mode='lines+markers',
                line=dict(color='#667eea', width=3)
            ))
            
            fig.add_trace(go.Scatter(
                x=kpi_data['period'],
                y=kpi_data['gross_margin_percent'],
                name='Gross Margin %',
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='#48bb78', width=2)
            ))
            
            fig.update_layout(
                title='Executive KPI Trends (Last 30 Days)',
                xaxis_title='Date',
                yaxis=dict(title='Net Sales (VND)', side='left'),
                yaxis2=dict(title='Gross Margin %', side='right', overlaying='y'),
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Regional performance
        st.markdown("---")
        st.markdown("#### 🌍 Regional Performance")
        
        regional_query = text("""
            SELECT * FROM vw_regional_performance_summary
            ORDER BY revenue DESC
        """)
        regional_data = execute_query_to_df(db, regional_query)
        
        if not regional_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    regional_data.groupby('region')['revenue'].sum().reset_index(),
                    values='revenue',
                    names='region',
                    title='Revenue by Region',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                top_stores = regional_data.head(10)
                fig = px.bar(
                    top_stores,
                    x='revenue',
                    y='store_name',
                    orientation='h',
                    title='Top 10 Stores by Revenue',
                    labels={'revenue': 'Revenue (VND)', 'store_name': 'Store'},
                    color='region',
                    color_discrete_sequence=['#667eea', '#f56565']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Order status overview
        st.markdown("---")
        st.markdown("#### 📋 Order Status Overview")
        
        order_query = text("""
            SELECT 
                order_status,
                COUNT(*) as order_count,
                SUM(total_order_value) as total_value
            FROM vw_sales_order_overview
            GROUP BY order_status
        """)
        order_data = execute_query_to_df(db, order_query)
        
        if not order_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    order_data,
                    values='order_count',
                    names='order_status',
                    title='Orders by Status',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                order_data['total_value_display'] = order_data['total_value'].apply(format_currency)
                st.dataframe(
                    order_data,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "order_status": "Status",
                        "order_count": "Orders",
                        "total_value_display": "Total Value"
                    }
                )
    
    except Exception as e:
        st.error(f"❌ Error loading executive dashboard: {str(e)}")
    
    finally:
        db.close()