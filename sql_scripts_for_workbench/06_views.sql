USE vinretail;

-- =====================================================
-- 1. SALES REPORTS
-- =====================================================

-- -----------------------------------------------------
-- vw_sales_order_overview
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_sales_order_overview AS
SELECT
    so.order_id,
    COUNT(so.order_id) AS order_count,
    SUM(soi.final_amount) AS total_order_value,
    so.order_status,
    l.region,
    l.city,
    l.location_name AS store_name
FROM sales_orders so
JOIN sales_order_items soi
    ON so.order_id = soi.order_id
JOIN locations l
    ON so.location_id = l.location_id
GROUP BY
    so.order_id,
    so.order_status,
    l.region,
    l.city,
    l.location_name;

-- -----------------------------------------------------
-- vw_sales_revenue_gm
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_sales_revenue_gm AS
SELECT
    l.region,
    l.city,
    l.location_name AS store_name,
    e.employee_id,
    CONCAT(e.first_name,' ',e.last_name) AS employee_name,
    p.product_id,
    p.product_name,
    pc.class_name,
    SUM(si.final_amount) AS total_revenue,
    SUM(ABS(si.quantity) * p.cost) AS total_cost,
    SUM(si.final_amount) - SUM(ABS(si.quantity) * p.cost) AS gross_margin,
    ROUND(
        (SUM(si.final_amount) - SUM(ABS(si.quantity) * p.cost))
        / NULLIF(SUM(si.final_amount),0) * 100,
        2
    ) AS gross_margin_percent
FROM sales s
JOIN sales_items si ON s.sale_id = si.sale_id
JOIN products p ON si.product_id = p.product_id
JOIN product_class pc ON p.class_id = pc.class_id
JOIN sales_orders so ON s.order_id = so.order_id
JOIN employees e ON so.employee_id = e.employee_id
JOIN locations l ON so.location_id = l.location_id
WHERE s.sale_type = 'INVOICE'
GROUP BY
    l.region, l.city, l.location_name,
    e.employee_id, employee_name,
    p.product_id, p.product_name, pc.class_name;

-- -----------------------------------------------------
-- vw_sales_returns_analysis
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_sales_returns_analysis AS
SELECT
    s.sale_id AS return_sale_id,
    s.parent_sale_id AS original_sale_id,
    COUNT(si.sale_item_id) AS number_of_returns,
    ABS(SUM(si.final_amount)) AS return_value,
    ROUND(
        ABS(SUM(si.final_amount))
        / NULLIF(orig.total_amount,0) * 100,
        2
    ) AS return_rate_percent
FROM sales s
JOIN sales_items si ON s.sale_id = si.sale_id
JOIN sales orig ON s.parent_sale_id = orig.sale_id
WHERE s.sale_type = 'RETURN'
GROUP BY
    s.sale_id,
    s.parent_sale_id,
    orig.total_amount;

-- -----------------------------------------------------
-- vw_sales_by_payment_method
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_sales_by_payment_method AS
SELECT
    pm.method_name,
    COUNT(DISTINCT s.sale_id) AS number_of_orders,
    SUM(s.total_amount) AS revenue,
    ROUND(
        SUM(s.total_amount)
        / NULLIF((SELECT SUM(total_amount)
                  FROM sales
                  WHERE sale_type='INVOICE'),0) * 100,
        2
    ) AS contribution_percent
FROM sales s
JOIN payment_methods pm ON s.payment_method_id = pm.payment_method_id
WHERE s.sale_type='INVOICE'
GROUP BY pm.method_name;

-- -----------------------------------------------------
-- vw_sales_employee_location_performance
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_sales_employee_location_performance AS
SELECT
    l.location_name AS store_name,
    CONCAT(m.first_name,' ',m.last_name) AS store_manager,
    CONCAT(e.first_name,' ',e.last_name) AS employee_name,
    COUNT(DISTINCT so.order_id) AS orders_handled,
    SUM(s.total_amount) AS total_sales,
    ROUND(AVG(s.total_amount),0) AS avg_order_value,
    ROUND(
        SUM(s.total_amount)
        / NULLIF((SELECT SUM(total_amount)
                  FROM sales
                  WHERE sale_type='INVOICE'),0) * 100,
        2
    ) AS contribution_percent
FROM sales s
JOIN sales_orders so ON s.order_id = so.order_id
JOIN employees e ON so.employee_id = e.employee_id
JOIN locations l ON so.location_id = l.location_id
LEFT JOIN employees m ON l.store_manager_id = m.employee_id
WHERE s.sale_type='INVOICE'
GROUP BY store_name, store_manager, employee_name;

-- =====================================================
-- 2. DELIVERY REPORTS
-- =====================================================

-- -----------------------------------------------------
-- vw_delivery_volume_by_type
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_delivery_volume_by_type AS
SELECT
    delivery_type,
    COUNT(delivery_id) AS number_of_deliveries
FROM deliveries
GROUP BY delivery_type;

-- -----------------------------------------------------
-- vw_delivery_vendor_performance
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_delivery_vendor_performance AS
SELECT
    v.vendor_name,
    COUNT(d.delivery_id) AS deliveries_count,
    SUM(d.delivery_status='DELIVERED') AS success_count,
    SUM(d.delivery_status<>'DELIVERED') AS failure_count,
    ROUND(
        SUM(d.delivery_status='DELIVERED')
        / NULLIF(COUNT(d.delivery_id),0) * 100,
        2
    ) AS success_rate_percent
FROM deliveries d
JOIN delivery_vendors v ON d.vendor_id = v.vendor_id
GROUP BY v.vendor_name;

-- -----------------------------------------------------
-- vw_delivery_employee_performance
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_delivery_employee_performance AS
SELECT
    CONCAT(e.first_name,' ',e.last_name) AS delivery_staff,
    COUNT(d.delivery_id) AS deliveries_handled,
    ROUND(
        SUM(d.delivery_status='DELIVERED')
        / NULLIF(COUNT(d.delivery_id),0) * 100,
        2
    ) AS delivery_success_rate
FROM deliveries d
JOIN employees e ON d.delivery_person_id = e.employee_id
GROUP BY delivery_staff;

-- -----------------------------------------------------
-- vw_delivery_vehicle_utilization
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_delivery_vehicle_utilization AS
SELECT
    v.vehicle_id,
    v.plate_number,
    COUNT(d.delivery_id) AS deliveries_per_vehicle,
    ROUND(
        COUNT(d.delivery_id)
        / NULLIF((SELECT COUNT(*) FROM deliveries),0) * 100,
        2
    ) AS utilization_rate_percent
FROM deliveries d
JOIN delivery_vehicles v ON d.vehicle_id = v.vehicle_id
GROUP BY v.vehicle_id, v.plate_number;

-- =====================================================
-- 3. INVENTORY REPORTS
-- =====================================================

-- -----------------------------------------------------
-- vw_inventory_current_status
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_inventory_current_status AS
SELECT
    p.product_name,
    l.location_name,
    i.quantity AS current_stock_quantity,
    CASE
        WHEN i.quantity < 50 THEN 'LOW'
        ELSE 'NORMAL'
    END AS stock_status
FROM inventory i
JOIN products p ON i.product_id = p.product_id
JOIN locations l ON i.location_id = l.location_id;

-- -----------------------------------------------------
-- vw_inventory_movement_summary
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_inventory_movement_summary AS
SELECT
    product_id,
    change_type,
    DATE(created_at) AS period,
    SUM(quantity_change) AS total_quantity
FROM inventory_history
GROUP BY product_id, change_type, DATE(created_at);

-- =====================================================
-- 4. HR & BONUS REPORTS
-- =====================================================

-- -----------------------------------------------------
-- vw_employee_sales_bonus
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_employee_sales_bonus AS
SELECT
    e.employee_id,
    CONCAT(e.first_name,' ',e.last_name) AS employee_name,
    SUM(s.total_amount) AS sales_volume,
    r.bonus_type,
    r.bonus_percentage,
    r.fixed_bonus_class,
    CASE
        WHEN r.bonus_type='PERCENT'
            THEN ROUND(SUM(s.total_amount) * r.bonus_percentage / 100, 0)
        WHEN r.bonus_type='FIXED'
            THEN r.fixed_bonus_class
        ELSE 0
    END AS bonus_amount
FROM employees e
JOIN sales_orders so ON e.employee_id = so.employee_id
JOIN sales s ON so.order_id = s.order_id
JOIN employee_bonus_rules r
    ON (r.start_date IS NULL OR s.sale_date >= r.start_date)
   AND (r.end_date IS NULL OR s.sale_date <= r.end_date)
WHERE s.sale_type='INVOICE'
GROUP BY
    e.employee_id,
    employee_name,
    r.bonus_type,
    r.bonus_percentage,
    r.fixed_bonus_class;

-- -----------------------------------------------------
-- vw_delivery_bonus_summary
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_delivery_bonus_summary AS
SELECT
    e.employee_id,
    CONCAT(e.first_name,' ',e.last_name) AS delivery_staff,
    COUNT(d.delivery_id) AS deliveries_completed,
    r.rule_type,
    r.bonus_amount,
    COUNT(d.delivery_id) * r.bonus_amount AS bonus_earned
FROM deliveries d
JOIN employees e ON d.delivery_person_id = e.employee_id
JOIN delivery_bonus_rules r
    ON (r.delivery_type IS NULL OR r.delivery_type = d.delivery_type)
   AND (r.start_date IS NULL OR d.created_at >= r.start_date)
   AND (r.end_date IS NULL OR d.created_at <= r.end_date)
WHERE d.delivery_status='DELIVERED'
GROUP BY
    e.employee_id,
    delivery_staff,
    r.rule_type,
    r.bonus_amount;

-- =====================================================
-- 5. LOYALTY & PROMOTION
-- =====================================================

-- -----------------------------------------------------
-- vw_loyalty_level_distribution
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_loyalty_level_distribution AS
SELECT
    ll.level_name AS loyalty_tier,
    COUNT(cl.customer_id) AS customer_count,
    SUM(cl.loyalty_points) AS points_balance
FROM customer_loyalty cl
JOIN loyalty_levels ll ON cl.loyalty_id = ll.loyalty_id
GROUP BY ll.level_name;

-- -----------------------------------------------------
-- vw_promotion_effectiveness
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_promotion_effectiveness AS
SELECT
    p.promotion_code,
    p.rule_type,
    COUNT(si.sale_item_id) AS usage_count,
    SUM(si.final_amount) AS revenue_contribution,
    ROUND(
        SUM(si.final_amount)
        / NULLIF((SELECT SUM(final_amount) FROM sales_items),0) * 100,
        2
    ) AS contribution_percent
FROM promotions p
JOIN sales_items si ON p.promotion_id = si.applied_promotion_id
GROUP BY p.promotion_code, p.rule_type;

-- =====================================================
-- 6. PRODUCT PERFORMANCE
-- =====================================================

-- -----------------------------------------------------
-- vw_product_sales_performance
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_product_sales_performance AS
SELECT
    p.product_id,
    p.product_name,
    SUM(si.quantity) AS quantity_sold,
    SUM(si.final_amount) AS revenue
FROM sales_items si
JOIN products p ON si.product_id = p.product_id
WHERE si.sale_type='INVOICE'
GROUP BY p.product_id, p.product_name;

-- -----------------------------------------------------
-- vw_product_class_performance
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_product_class_performance AS
SELECT
    pc.class_name,
    SUM(si.final_amount) AS revenue,
    ROUND(
        SUM(si.final_amount)
        / NULLIF((SELECT SUM(final_amount)
                  FROM sales_items
                  WHERE sale_type='INVOICE'),0) * 100,
        2
    ) AS contribution_percent
FROM sales_items si
JOIN products p ON si.product_id = p.product_id
JOIN product_class pc ON p.class_id = pc.class_id
WHERE si.sale_type='INVOICE'
GROUP BY pc.class_name;

-- =====================================================
-- 7. EXECUTIVE REPORTS
-- =====================================================

-- -----------------------------------------------------
-- vw_executive_kpi_overview
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_executive_kpi_overview AS
SELECT
    DATE(s.sale_date) AS period,
    SUM(s.total_amount) AS net_sales,
    ROUND(
        (SUM(si.final_amount) - SUM(ABS(si.quantity)*p.cost))
        / NULLIF(SUM(si.final_amount),0) * 100,
        2
    ) AS gross_margin_percent,
    ROUND(
        SUM(s.sale_type='RETURN')
        / NULLIF(COUNT(s.sale_id),0) * 100,
        2
    ) AS return_rate_percent,
    ROUND(
        SUM(d.delivery_status='DELIVERED')
        / NULLIF(COUNT(d.delivery_id),0) * 100,
        2
    ) AS delivery_success_rate
FROM sales s
JOIN sales_items si ON s.sale_id = si.sale_id
JOIN products p ON si.product_id = p.product_id
LEFT JOIN deliveries d ON s.sale_id = d.sale_id
GROUP BY DATE(s.sale_date);

-- -----------------------------------------------------
-- vw_regional_performance_summary
-- -----------------------------------------------------
CREATE OR REPLACE VIEW vw_regional_performance_summary AS
SELECT
    l.region,
    l.location_name AS store_name,
    SUM(s.total_amount) AS revenue
FROM sales s
JOIN sales_orders so ON s.order_id = so.order_id
JOIN locations l ON so.location_id = l.location_id
WHERE s.sale_type='INVOICE'
GROUP BY l.region, l.location_name;
