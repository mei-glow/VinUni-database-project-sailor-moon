use vinretail;
CREATE OR REPLACE VIEW vw_dashboard_kpi AS
SELECT
  COUNT(DISTINCT s.sale_id)            AS total_sales,
  COALESCE(SUM(s.total_amount), 0)     AS total_revenue,
  COUNT(DISTINCT p.product_id)         AS total_products
FROM sales s
LEFT JOIN sales_items si ON s.sale_id = si.sale_id
LEFT JOIN products p ON si.product_id = p.product_id;
