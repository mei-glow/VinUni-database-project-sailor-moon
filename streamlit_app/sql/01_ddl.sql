-- =====================================================
-- VinRetail Database Initialization
-- =====================================================

-- 1. Drop database if exists
DROP DATABASE IF EXISTS vinretail;
SELECT 'Existing database vinretail dropped (if existed)' AS status;
-- 2. Create database
CREATE DATABASE vinretail;
USE vinretail;
SELECT 'Database vinretail created successfully' AS status;

-- 3. Use database
USE vinretail;
SELECT 'Using database vinretail' AS status;

-- =====================================================
-- Tables
-- =====================================================
-- departments
CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP 
        ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- brandschk_sales_item_type
CREATE TABLE brands (
    brand_id INT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- loyalty_levels
CREATE TABLE loyalty_levels (
    loyalty_id INT AUTO_INCREMENT PRIMARY KEY,
    level_name VARCHAR(50) NOT NULL UNIQUE,
    min_total_spent DECIMAL(12,2) NOT NULL CHECK (min_total_spent >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- payment_methods
CREATE TABLE payment_methods (
    payment_method_id INT AUTO_INCREMENT PRIMARY KEY,
    method_name VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- employees
CREATE TABLE employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(100),
    gender ENUM('M','F','OTHER'),
    department_id INT,
    role ENUM('Staff','Warehouse','Manager','Delivery','Admin'),
    job_description VARCHAR(255),
    hire_date DATE,
    phone VARCHAR(20),
    supervisor_id INT,
    is_inactive BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP 
        ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_emp_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id),
    CONSTRAINT fk_emp_supervisor
        FOREIGN KEY (supervisor_id) REFERENCES employees(employee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- locations
CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(150) NOT NULL,
    location_type ENUM('STORE','WAREHOUSE') NOT NULL,
    address VARCHAR(255),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    city VARCHAR(100),
    region ENUM('North','South'),
    channel ENUM('Online','Offline','Ecommerce','Warehouse'),
    email VARCHAR(100),
    store_manager_id INT,
    opening_date DATE,
    close_date DATE,
    CONSTRAINT fk_location_manager
        FOREIGN KEY (store_manager_id) REFERENCES employees(employee_id),
    CONSTRAINT chk_location_date
        CHECK (close_date IS NULL OR opening_date <= close_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- product_class
CREATE TABLE product_class (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    brand_id INT NOT NULL,
    product_group ENUM(
  'electronics',
  'clothing',
  'food',
  'beverages',
  'home_appliances',
  'furniture',
  'beauty_personal_care',
  'healthcare',
  'baby_kids',
  'sports_outdoor',
  'fashion_accessories',
  'footwear',
  'stationery_books',
  'toys_games',
  'pet_supplies',
  'automotive',
  'home_living',
  'jewelry_watches',
  'office_equipment',
  'digital_products',
  'services',
  'other'
),
    CONSTRAINT fk_class_brand
        FOREIGN KEY (brand_id) REFERENCES brands(brand_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- products
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    class_id INT NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL CHECK (unit_price >= 0),
	cost DECIMAL(12,2) NOT NULL CHECK (cost >= 0),
    status ENUM('ACTIVE','INACTIVE','DISCONTINUED') DEFAULT 'ACTIVE',
    color VARCHAR(50),
    pattern VARCHAR(50),
    weight DECIMAL(6,2),
    thickness DECIMAL(6,2),
    length DECIMAL(6,2),
    width DECIMAL(6,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP 
        ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_class
        FOREIGN KEY (class_id) REFERENCES product_class(class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- customers
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    gender ENUM('M','F','OTHER'),
    date_of_birth DATE,
    address VARCHAR(255),
    email VARCHAR(100),
    phone VARCHAR(20) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP 
        ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- customer_preferences
CREATE TABLE customer_preferences (
    customer_id INT NOT NULL,
    class_id INT NOT NULL,
    PRIMARY KEY (customer_id, class_id),
    CONSTRAINT fk_pref_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_pref_class
        FOREIGN KEY (class_id) REFERENCES product_class(class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- customer_loyalty
CREATE TABLE customer_loyalty (
  customer_id INT PRIMARY KEY,
  loyalty_id INT NOT NULL,
  loyalty_points INT NOT NULL DEFAULT 0 CHECK (loyalty_points >= 0),
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  loyalty_points_expired_date DATE,
  CONSTRAINT fk_cl_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  CONSTRAINT fk_cl_level FOREIGN KEY (loyalty_id) REFERENCES loyalty_levels(loyalty_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- inventory
CREATE TABLE inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    location_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),
    CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT fk_inventory_location
        FOREIGN KEY (location_id) REFERENCES locations(location_id),
    CONSTRAINT uq_inventory UNIQUE (product_id, location_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- inventory_history
CREATE TABLE inventory_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    location_id INT NOT NULL,
    change_type ENUM('IN','OUT','TRANSFER','ADJUST') NOT NULL,
    quantity_change INT NOT NULL,
    reference_table VARCHAR(50),
    reference_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_hist_product
        FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT fk_hist_location
        FOREIGN KEY (location_id) REFERENCES locations(location_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- sales_orders
CREATE TABLE sales_orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    employee_id INT NOT NULL,
    location_id INT NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    order_status ENUM('OPEN','CONFIRMED','CANCELLED'),
    note VARCHAR(255),
    closed_reason VARCHAR(255),
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP 
        ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_order_employee FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    CONSTRAINT fk_order_location FOREIGN KEY (location_id) REFERENCES locations(location_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- promotions_campaigns
CREATE TABLE promotions_campaigns (
    campaign_id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    campaign_name VARCHAR(150),
    campaign_description VARCHAR(255),
    start_date DATE,
    end_date DATE,
    CONSTRAINT fk_campaign_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- promotions
CREATE TABLE promotions (
    promotion_id INT AUTO_INCREMENT PRIMARY KEY,
    promotion_code VARCHAR(50) NOT NULL UNIQUE,
    rule_type ENUM('PERCENT','FIXED','BUY_X_GET_Y') NOT NULL,
    buy_product_id INT,
    buy_quantity INT,
    get_product_id INT,
    get_quantity INT,
    discount_value DECIMAL(10,2),
    discount_percent DECIMAL(5,2),
    status ENUM('ACTIVE','EXPIRED'),
    campaign_id INT,
    CONSTRAINT fk_promo_campaign
        FOREIGN KEY (campaign_id) REFERENCES promotions_campaigns(campaign_id),
    CONSTRAINT fk_promo_buy_product
        FOREIGN KEY (buy_product_id) REFERENCES products(product_id),
    CONSTRAINT fk_promo_get_product
        FOREIGN KEY (get_product_id) REFERENCES products(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- sales_order_items
CREATE TABLE sales_order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    applied_promotion_id INT,
    final_amount DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_orderitem_order FOREIGN KEY (order_id) REFERENCES sales_orders(order_id),
    CONSTRAINT fk_orderitem_product FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT fk_orderitem_promo FOREIGN KEY (applied_promotion_id) REFERENCES promotions(promotion_id),
    CONSTRAINT uq_order_product UNIQUE (order_id, product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- sales
CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_type ENUM('INVOICE','RETURN') NOT NULL,     -- Distinguish invoice vs return
    parent_sale_id INT NULL,  -- Link return to original invoice
    order_id INT NULL,
    total_amount DECIMAL(14,2) NOT NULL,
    payment_method_id INT NOT NULL,
    invoice_status ENUM('PAID','UNPAID','REFUNDED') NOT NULL,
    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    expected_delivery_date DATE,
    CONSTRAINT fk_sale_order
        FOREIGN KEY (order_id) REFERENCES sales_orders(order_id),
    CONSTRAINT fk_sale_payment
        FOREIGN KEY (payment_method_id) REFERENCES payment_methods(payment_method_id),
    CONSTRAINT fk_sale_parent
        FOREIGN KEY (parent_sale_id) REFERENCES sales(sale_id),
    CONSTRAINT chk_sales_type       -- Logical constraints
        CHECK (
            (sale_type = 'INVOICE' AND parent_sale_id IS NULL)
            OR
            (sale_type = 'RETURN' AND parent_sale_id IS NOT NULL)
        )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- sales_items
CREATE TABLE sales_items (
    sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    sale_type ENUM('INVOICE','RETURN') NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,     -- Positive for INVOICE, negative for RETURN
    applied_promotion_id INT NULL,
    final_amount DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_saleitem_sale
        FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
    CONSTRAINT fk_saleitem_product
        FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT fk_saleitem_promo
        FOREIGN KEY (applied_promotion_id) REFERENCES promotions(promotion_id),
    -- Logical constraints
    CONSTRAINT chk_sales_item_type
        CHECK (
            (sale_type = 'INVOICE' AND quantity >= 0 AND final_amount >= 0)
            OR
            (sale_type = 'RETURN' AND quantity <= 0 AND final_amount <= 0)
        )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- delivery_vendors
CREATE TABLE delivery_vendors (
    vendor_id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_name VARCHAR(100),
    vendor_type ENUM('INTERNAL','THIRD_PARTY', 'DROPSHIPPING')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- delivery_vehicles
CREATE TABLE delivery_vehicles (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    plate_number VARCHAR(20) NOT NULL UNIQUE,
    capacity INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP 
        ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- deliveries
CREATE TABLE deliveries (
    delivery_id INT AUTO_INCREMENT PRIMARY KEY,
    delivery_type ENUM('FULFILLMENT','TRANSFER','RETURN') NOT NULL,
    sale_id INT NULL,      -- Sale reference (required for fulfillment & return)
    delivery_person_id INT,
    vendor_id INT,
    vehicle_id INT,
    from_location_id INT NULL,
    to_location_id INT NULL,
    delivery_status ENUM(
        'CREATED',
        'PACKED',
        'SHIPPED',
        'DELIVERED',
        'FAILED'
    ) NOT NULL DEFAULT 'CREATED',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP 
        ON UPDATE CURRENT_TIMESTAMP,
    note VARCHAR(255),
    CONSTRAINT fk_delivery_sale
        FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
    CONSTRAINT fk_delivery_employee
        FOREIGN KEY (delivery_person_id) REFERENCES employees(employee_id),
    CONSTRAINT fk_delivery_vendor
        FOREIGN KEY (vendor_id) REFERENCES delivery_vendors(vendor_id),
    CONSTRAINT fk_delivery_vehicle
        FOREIGN KEY (vehicle_id) REFERENCES delivery_vehicles(vehicle_id),
    CONSTRAINT fk_delivery_from_location
        FOREIGN KEY (from_location_id) REFERENCES locations(location_id),
    CONSTRAINT fk_delivery_to_location
        FOREIGN KEY (to_location_id) REFERENCES locations(location_id),
    CONSTRAINT chk_delivery_logic     -- Business logic constraints
        CHECK (
            -- Transfer between locations
            (delivery_type = 'TRANSFER' 
                AND from_location_id IS NOT NULL 
                AND to_location_id IS NOT NULL
                AND from_location_id <> to_location_id)
            OR
            -- Fulfillment to customer
            (delivery_type = 'FULFILLMENT'
                AND sale_id IS NOT NULL
                AND from_location_id IS NOT NULL)
            OR
            -- Return from customer
            (delivery_type = 'RETURN'
                AND sale_id IS NOT NULL
                AND to_location_id IS NOT NULL)
        )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- delivery_status_history
CREATE TABLE delivery_status_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    delivery_id INT NOT NULL,
    old_status ENUM('CREATED','PACKED','SHIPPED','DELIVERED','FAILED'),
    new_status ENUM('CREATED','PACKED','SHIPPED','DELIVERED','FAILED'),
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_delivery_history
        FOREIGN KEY (delivery_id) REFERENCES deliveries(delivery_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- employee_bonus_rules
CREATE TABLE employee_bonus_rules (
    rule_id INT AUTO_INCREMENT PRIMARY KEY,
    bonus_type ENUM('PERCENT','FIXED', 'KPI'),
    min_sales DECIMAL(12,2),
    bonus_percentage DECIMAL(5,2),
    start_date DATE,
    end_date DATE,
    class_id INT,
    fixed_bonus_class DECIMAL(10,2),
    CONSTRAINT fk_bonus_class
        FOREIGN KEY (class_id) REFERENCES product_class(class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- delivery_bonus_rules
CREATE TABLE delivery_bonus_rules (
    rule_id INT AUTO_INCREMENT PRIMARY KEY,
    rule_type ENUM('BY_COUNT','BY_CLASS','BY_DELIVERY_TYPE'),
    min_deliveries INT,
    bonus_amount DECIMAL(10,2),
    delivery_type ENUM('TRANSFER','FULFILLMENT', 'RETURN'),
    class_id INT,
    start_date DATE,
    end_date DATE,
    CONSTRAINT fk_delivery_bonus_class
        FOREIGN KEY (class_id) REFERENCES product_class(class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- users
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- roles
CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE, -- Example roles: ADMIN, SALES, WAREHOUSE, DELIVERY, HR, MANAGER, ANALYST
    description VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- user_roles 
CREATE TABLE user_roles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_ur_user
        FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_ur_role
        FOREIGN KEY (role_id) REFERENCES roles(role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- permissions
CREATE TABLE permissions (
    permission_id INT AUTO_INCREMENT PRIMARY KEY,
    permission_code VARCHAR(100) NOT NULL UNIQUE, -- example: VIEW_SALES_DASHBOARD, CREATE_ORDER, CONFIRM_ORDER, MANAGE_PRODUCTS, MANAGE_DELIVERIES, VIEW_HR_REPORTS...
    description VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- role_permissions
CREATE TABLE role_permissions (
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    CONSTRAINT fk_rp_role
        FOREIGN KEY (role_id) REFERENCES roles(role_id),
    CONSTRAINT fk_rp_permission
        FOREIGN KEY (permission_id) REFERENCES permissions(permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- audit_logs

CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    operation_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
    old_value TEXT,
    new_value TEXT,
    record_id INT,
    changed_by INT NULL,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user
        FOREIGN KEY (changed_by) REFERENCES users(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Verification
-- =====================================================

SELECT 'Tables created in vinretail database:' AS info;

SHOW TABLES;

SELECT 'Database schema initialization completed successfully' AS status;
