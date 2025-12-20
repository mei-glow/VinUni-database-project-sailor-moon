use vinretail;
-- testing 1
EXPLAIN FORMAT=TRADITIONAL
SELECT *
FROM sales 
WHERE sale_date BETWEEN '2025-12-01' AND '2025-12-07';
-- Sales date filtering
CREATE INDEX idx_sales_sale_date ON sales (sale_date);
EXPLAIN FORMAT=TRADITIONAL
SELECT *
FROM sales 
WHERE sale_date BETWEEN '2025-12-01' AND '2025-12-07';

-- Order date filtering
CREATE INDEX idx_sales_orders_order_date ON sales_orders (order_date);

-- Delivery tracking by creation time
CREATE INDEX idx_deliveries_created_at ON deliveries (created_at);
-- testing 2
EXPLAIN FORMAT=TRADITIONAL
SELECT *
FROM customers
WHERE phone = '0912000119';
-- Phone indexing
drop INDEX phone on customers;
CREATE INDEX idx_customers_phone ON customers (phone);
EXPLAIN FORMAT=TRADITIONAL
SELECT *
FROM customers
WHERE phone = '0912000119';