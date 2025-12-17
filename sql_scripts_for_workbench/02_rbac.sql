/* =========================================================
   RBAC INITIALIZATION SCRIPT
   VinRetail Management System
   Safe to commit (no secrets)
   ========================================================= */

-- =========================
-- 1. ROLES
-- =========================
use vinretail;
INSERT INTO roles (role_name, description) VALUES
('ADMIN', 'System administrator'),
('SALES', 'Sales staff'),
('WAREHOUSE', 'Warehouse staff'),
('DELIVERY', 'Delivery staff'),
('HR', 'Human resources staff'),
('MANAGER', 'Store or regional manager'),
('ANALYST', 'Business data analyst');

-- =========================
-- 2. PERMISSIONS
-- =========================
INSERT INTO permissions (permission_code, description) VALUES

-- USER & SECURITY
('USER_CREATE', 'Create system user'),
('USER_VIEW', 'View users'),
('USER_UPDATE', 'Update users'),
('USER_DISABLE', 'Disable users'),
('ROLE_VIEW', 'View roles and permissions'),

-- PRODUCT & INVENTORY
('PRODUCT_CREATE', 'Create product'),
('PRODUCT_VIEW', 'View product'),
('PRODUCT_UPDATE', 'Update product'),
('PRODUCT_DELETE', 'Delete product'),
('PRODUCT_MANAGE', 'Product management'),

('INVENTORY_VIEW', 'View inventory'),
('INVENTORY_UPDATE', 'Update inventory'),

-- SALES & ORDER
('ORDER_CREATE', 'Create sales order'),
('ORDER_VIEW', 'View sales order'),
('ORDER_UPDATE', 'Update sales order'),
('ORDER_CONFIRM', 'Confirm sales order'),

('INVOICE_VIEW', 'View invoice'),
('RETURN_PROCESS', 'Process sales return'),

-- EMPLOYEE (HR)
('EMPLOYEE_CREATE', 'Create employee record'),
('EMPLOYEE_VIEW', 'View employees'),
('EMPLOYEE_UPDATE', 'Update employee record'),
('EMPLOYEE_DISABLE', 'Disable employee'),

-- DELIVERY
('DELIVERY_CREATE', 'Create delivery'),
('DELIVERY_VIEW', 'View delivery'),
('DELIVERY_UPDATE_STATUS', 'Update delivery status'),

-- DASHBOARD / REPORT (SQL VIEWS)
('DASHBOARD_SALES_VIEW', 'View sales dashboard'),
('DASHBOARD_INVENTORY_VIEW', 'View inventory dashboard'),
('DASHBOARD_DELIVERY_VIEW', 'View delivery dashboard'),
('DASHBOARD_HR_VIEW', 'View HR dashboard'),
('DASHBOARD_EXECUTIVE_VIEW', 'View executive KPIs'),

-- AUDIT & SYSTEM
('AUDIT_VIEW', 'View audit logs'),
('SYSTEM_CONFIG', 'System configuration access');

-- =========================
-- 3. ROLE → PERMISSION MAPPING
-- =========================

-- ---------- ADMIN (ALL PERMISSIONS)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r
CROSS JOIN permissions p
WHERE r.role_name = 'ADMIN';

-- ---------- SALES
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r
JOIN permissions p ON p.permission_code IN (
    'PRODUCT_VIEW',
    'ORDER_CREATE',
    'ORDER_VIEW',
    'ORDER_UPDATE',
    'ORDER_CONFIRM',
    'INVOICE_VIEW',
    'RETURN_PROCESS',
    'DASHBOARD_SALES_VIEW'
)
WHERE r.role_name = 'SALES';

-- ---------- WAREHOUSE
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r
JOIN permissions p ON p.permission_code IN (
    'PRODUCT_VIEW',
    'INVENTORY_VIEW',
    'INVENTORY_UPDATE',
    'DASHBOARD_INVENTORY_VIEW'
)
WHERE r.role_name = 'WAREHOUSE';
-- ---------- HR
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r
JOIN permissions p ON p.permission_code IN (
    'USER_VIEW',
    'EMPLOYEE_CREATE',
    'EMPLOYEE_VIEW',
    'EMPLOYEE_UPDATE',
    'EMPLOYEE_DISABLE',
    'DASHBOARD_HR_VIEW'
)
WHERE r.role_name = 'HR';


-- ---------- DELIVERY
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r
JOIN permissions p ON p.permission_code IN (
    'DELIVERY_CREATE',
    'DELIVERY_VIEW',
    'DELIVERY_UPDATE_STATUS',
    'DASHBOARD_DELIVERY_VIEW'
)
WHERE r.role_name = 'DELIVERY';


-- ---------- MANAGER
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r
JOIN permissions p ON p.permission_code IN (
    'DASHBOARD_SALES_VIEW',
    'DASHBOARD_INVENTORY_VIEW',
    'DASHBOARD_DELIVERY_VIEW',
    'DASHBOARD_EXECUTIVE_VIEW'
)
WHERE r.role_name = 'MANAGER';

-- ---------- ANALYST
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM roles r
JOIN permissions p ON p.permission_code IN (
    'DASHBOARD_SALES_VIEW',
    'DASHBOARD_INVENTORY_VIEW',
    'DASHBOARD_EXECUTIVE_VIEW'
)
WHERE r.role_name = 'ANALYST';

-- =========================
-- 4. VERIFICATION QUERIES
-- =========================

-- View permissions per role
SELECT r.role_name, p.permission_code
FROM role_permissions rp
JOIN roles r ON rp.role_id = r.role_id
JOIN permissions p ON rp.permission_id = p.permission_id
ORDER BY r.role_name, p.permission_code;
