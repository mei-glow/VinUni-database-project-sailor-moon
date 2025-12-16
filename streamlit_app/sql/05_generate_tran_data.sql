-- =====================================================
-- VinRetail Transaction Data
-- FINAL VERSION – TRIGGER SAFE – INVENTORY SAFE
-- =====================================================

USE vinretail;
SET SQL_SAFE_UPDATES = 0;

-- =====================================================
-- RESET TRANSACTION TABLES
-- =====================================================
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE deliveries;
TRUNCATE inventory_history;
TRUNCATE sales_items;
TRUNCATE sales;
TRUNCATE sales_order_items;
TRUNCATE sales_orders;
SET FOREIGN_KEY_CHECKS = 1;

SET @start_time = NOW();

-- =====================================================
-- TEMP: RANDOM DATES (LAST 6 MONTHS)
-- =====================================================
DROP TEMPORARY TABLE IF EXISTS temp_dates;
CREATE TEMPORARY TABLE temp_dates (date_value DATETIME);

INSERT INTO temp_dates
SELECT DATE_SUB(CURDATE(), INTERVAL n DAY)
FROM (
    SELECT a.n + b.n*10 AS n
    FROM
        (SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a,
        (SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) b
    WHERE a.n + b.n*10 < 180
) t;

-- =====================================================
-- STEP 1: CREATE SALES ORDERS (200)
-- =====================================================
INSERT INTO sales_orders (
    customer_id,
    employee_id,
    location_id,
    order_date,
    order_status
)
SELECT
    c.customer_id,
    e.employee_id,
    l.location_id,
    d.date_value,
    'OPEN'
FROM
    (SELECT customer_id FROM customers ORDER BY RAND() LIMIT 200) c
CROSS JOIN
    (SELECT employee_id FROM employees WHERE role = 'Staff' ORDER BY RAND() LIMIT 1) e
CROSS JOIN
    (SELECT location_id FROM locations WHERE location_type = 'STORE' ORDER BY RAND() LIMIT 1) l
JOIN
    (SELECT date_value FROM temp_dates ORDER BY RAND() LIMIT 200) d;

-- =====================================================
-- STEP 2: SALES ORDER ITEMS (NO DUPLICATE)
-- =====================================================

-- ITEM 1 (100%)
INSERT INTO sales_order_items (
    order_id,
    product_id,
    quantity,
    applied_promotion_id,
    final_amount
)
SELECT
    so.order_id,
    (SELECT product_id FROM products ORDER BY RAND() LIMIT 1),
    FLOOR(1 + RAND()*3),
    NULL,
    0
FROM sales_orders so;

-- ITEM 2 (70%)
INSERT INTO sales_order_items (
    order_id,
    product_id,
    quantity,
    applied_promotion_id,
    final_amount
)
SELECT
    so.order_id,
    (
        SELECT p.product_id
        FROM products p
        WHERE p.product_id NOT IN (
            SELECT product_id
            FROM sales_order_items
            WHERE order_id = so.order_id
        )
        ORDER BY RAND()
        LIMIT 1
    ),
    FLOOR(1 + RAND()*3),
    NULL,
    0
FROM sales_orders so
WHERE RAND() < 0.7;

-- ITEM 3 (30%)
INSERT INTO sales_order_items (
    order_id,
    product_id,
    quantity,
    applied_promotion_id,
    final_amount
)
SELECT
    so.order_id,
    (
        SELECT p.product_id
        FROM products p
        WHERE p.product_id NOT IN (
            SELECT product_id
            FROM sales_order_items
            WHERE order_id = so.order_id
        )
        ORDER BY RAND()
        LIMIT 1
    ),
    FLOOR(1 + RAND()*2),
    NULL,
    0
FROM sales_orders so
WHERE RAND() < 0.3;

-- =====================================================
-- STEP 3: CONFIRM / CANCEL ORDERS
-- =====================================================
UPDATE sales_orders
SET order_status = 'CONFIRMED'
WHERE RAND() < 0.9;

UPDATE sales_orders
SET order_status = 'CANCELLED',
    closed_reason = 'Customer cancelled'
WHERE order_status = 'OPEN';


-- =====================================================
-- STEP 5: SEED INVENTORY (FIXED)
-- =====================================================

INSERT INTO inventory (
    product_id,
    location_id,
    quantity
)
SELECT
    p.product_id,
    l.location_id,
    5000    -- initial stock
FROM products p
JOIN locations l
    ON l.location_type = 'STORE'
LEFT JOIN inventory i
    ON i.product_id = p.product_id
   AND i.location_id = l.location_id
WHERE i.product_id IS NULL;



-- =====================================================
-- STEP 4: CREATE SALES (OPTIMIZED)
-- =====================================================

SET @rand_payment_method :=
(
    SELECT payment_method_id
    FROM payment_methods
    ORDER BY RAND()
    LIMIT 1
);

INSERT INTO sales (
    sale_type,
    order_id,
    payment_method_id,
    invoice_status,
    sale_date,
    total_amount
)
SELECT
    'INVOICE',
    order_id,
    @rand_payment_method,
    'PAID',
    order_date,
    0
FROM sales_orders
WHERE order_status = 'CONFIRMED';

-- =====================================================
-- STEP 6: TEMP MAP (ORDER → SALE)
-- =====================================================
DROP TEMPORARY TABLE IF EXISTS tmp_order_sale;
CREATE TEMPORARY TABLE tmp_order_sale AS
SELECT order_id, sale_id
FROM sales
WHERE sale_type = 'INVOICE';

-- =====================================================
-- STEP 7: SALES ITEMS (TRIGGER SAFE)
-- =====================================================
INSERT INTO sales_items (
    sale_id,
    sale_type,
    product_id,
    quantity,
    applied_promotion_id,
    final_amount
)
SELECT
    m.sale_id,
    'INVOICE',
    soi.product_id,
    soi.quantity,
    soi.applied_promotion_id,
    0
FROM sales_order_items soi
JOIN tmp_order_sale m
    ON soi.order_id = m.order_id;

-- =====================================================
-- STEP 8: DELIVERIES
-- =====================================================
INSERT INTO deliveries (
    delivery_type,
    sale_id,
    delivery_person_id,
    vendor_id,
    vehicle_id,
    from_location_id,
    delivery_status,
    created_at
)
SELECT
    'FULFILLMENT',
    m.sale_id,
    (SELECT employee_id FROM employees WHERE role = 'Delivery' ORDER BY RAND() LIMIT 1),
    (SELECT vendor_id FROM delivery_vendors ORDER BY RAND() LIMIT 1),
    (SELECT vehicle_id FROM delivery_vehicles ORDER BY RAND() LIMIT 1),
    so.location_id,
    IF(RAND() < 0.85, 'DELIVERED', 'SHIPPED'),
    CURRENT_TIMESTAMP
FROM tmp_order_sale m
JOIN sales_orders so
    ON m.order_id = so.order_id;

-- =====================================================
-- CLEANUP
-- =====================================================
DROP TEMPORARY TABLE temp_dates;
DROP TEMPORARY TABLE tmp_order_sale;

SET SQL_SAFE_UPDATES = 1;

SELECT
    'TRANSACTION GENERATION COMPLETED SUCCESSFULLY' AS status,
    TIMESTAMPDIFF(SECOND, @start_time, NOW()) AS execution_seconds;
