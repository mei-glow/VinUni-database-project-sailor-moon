use vinretail;
CREATE OR REPLACE VIEW vw_dashboard_kpi AS
SELECT
  COUNT(DISTINCT s.sale_id)            AS total_sales,
  COALESCE(SUM(s.total_amount), 0)     AS total_revenue,
  COUNT(DISTINCT p.product_id)         AS total_products
FROM sales s
LEFT JOIN sales_items si ON s.sale_id = si.sale_id
LEFT JOIN products p ON si.product_id = p.product_id;

-- I. Sales Views
-- 1. Sales Order Overview
CREATE OR REPLACE VIEW vw_sales_order_overview AS
SELECT 
    l.region, l.city, l.store_name,
    COUNT(so.order_id) AS order_count,
    SUM(so.total_value) AS total_order_value,
    so.status AS order_status
FROM sales_orders so
JOIN locations l ON so.location_id = l.location_id
GROUP BY l.region, l.city, l.store_name, so.status;

-- 2. Sales Revenue & Gross Margin (GM)
CREATE OR REPLACE VIEW vw_sales_revenue_gm AS
SELECT 
    p.product_name, pc.category_name,
    SUM(si.quantity * si.unit_price) AS total_revenue,
    SUM(si.quantity * si.unit_cost) AS total_cost,
    SUM(si.quantity * (si.unit_price - si.unit_cost)) AS gross_margin,
    (SUM(si.quantity * (si.unit_price - si.unit_cost)) / SUM(si.quantity * si.unit_price)) * 100 AS gm_percentage
FROM sales s
JOIN sales_items si ON s.sales_id = si.sales_id
JOIN products p ON si.product_id = p.product_id
JOIN product_class pc ON p.class_id = pc.class_id
GROUP BY p.product_name, pc.category_name;

-- 3. Sales Returns Analysis
CREATE OR REPLACE VIEW vw_sales_returns_analysis AS
SELECT 
    s.invoice_reference AS original_invoice,
    COUNT(si.item_id) AS number_of_returns,
    SUM(si.return_value) AS total_return_value,
    (SUM(si.return_value) / SUM(s.total_value)) * 100 AS return_rate_percentage
FROM sales s
JOIN sales_items si ON s.sales_id = si.sales_id
WHERE si.status = 'RETURNED'
GROUP BY s.invoice_reference;

-- 4. Sales by Payment Method
CREATE OR REPLACE VIEW vw_sales_by_payment_method AS
SELECT 
    pm.payment_method_name,
    COUNT(so.order_id) AS number_of_orders,
    SUM(s.total_amount) AS total_revenue,
    (SUM(s.total_amount) / (SELECT SUM(total_amount) FROM sales) * 100) AS percentage_contribution
FROM sales s
JOIN sales_orders so ON s.order_id = so.order_id
JOIN payment_methods pm ON so.payment_method_id = pm.payment_method_id
GROUP BY pm.payment_method_name;

-- 5. Sales Employee & Location Performance
CREATE OR REPLACE VIEW vw_sales_employee_location_performance AS
SELECT 
    l.store_name,
    l.store_manager,
    e.employee_name,
    COUNT(so.order_id) AS orders_handled,
    SUM(s.total_amount) AS total_sales,
    AVG(s.total_amount) AS average_order_value,
    (SUM(s.total_amount) / (SELECT SUM(total_amount) FROM sales) * 100) AS contribution_percentage
FROM sales s
JOIN sales_orders so ON s.order_id = so.order_id
JOIN employees e ON so.employee_id = e.employee_id
JOIN locations l ON so.location_id = l.location_id
GROUP BY l.store_name, l.store_manager, e.employee_name;

II. Delivery Views
-- 1. Delivery Volume by Type
CREATE OR REPLACE VIEW vw_delivery_volume_by_type AS
SELECT 
    delivery_type, -- (TRANSFER, FULFILLMENT, RETURN)
    COUNT(delivery_id) AS number_of_deliveries
FROM deliveries
GROUP BY delivery_type;

-- 2. Delivery Vendor Performance
CREATE OR REPLACE VIEW vw_delivery_vendor_performance AS
SELECT 
    dv.vendor_name,
    COUNT(d.delivery_id) AS total_deliveries,
    SUM(CASE WHEN d.status = 'SUCCESS' THEN 1 ELSE 0 END) / COUNT(d.delivery_id) * 100 AS success_rate
FROM deliveries d
JOIN delivery_vendors dv ON d.vendor_id = dv.vendor_id
GROUP BY dv.vendor_name;

-- 3. Delivery Employee Performance
CREATE OR REPLACE VIEW vw_delivery_employee_performance AS
SELECT 
    e.employee_name,
    COUNT(d.delivery_id) AS deliveries_handled,
    SUM(CASE WHEN d.status = 'SUCCESS' THEN 1 ELSE 0 END) / COUNT(d.delivery_id) * 100 AS delivery_success_rate
FROM deliveries d
JOIN employees e ON d.driver_id = e.employee_id
GROUP BY e.employee_name;

-- 4. Delivery Vehicle Utilization
CREATE OR REPLACE VIEW vw_delivery_vehicle_utilization AS
SELECT 
    dv.vehicle_id,
    dv.license_plate,
    dv.vehicle_type,
    COUNT(d.delivery_id) AS number_of_deliveries_per_vehicle,
    -- Utilization Rate: Deliveries relative to an assumed capacity or average
    (COUNT(d.delivery_id) / NULLIF((SELECT COUNT(delivery_id) FROM deliveries), 0) * 100) AS vehicle_utilization_rate
FROM delivery_vehicles dv
LEFT JOIN deliveries d ON dv.vehicle_id = d.vehicle_id
GROUP BY dv.vehicle_id, dv.license_plate, dv.vehicle_type;