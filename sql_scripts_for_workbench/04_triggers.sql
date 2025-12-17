-- =====================================================
-- VinRetail Triggers
-- File: triggers.sql
-- Description: All business logic triggers
-- Run AFTER: DDL, RBAC, sample_data
-- =====================================================

USE vinretail;

DELIMITER $$

-- =====================================================
-- TRIGGER 1: Calculate final_amount for Sales Order Items
-- =====================================================

DROP TRIGGER IF EXISTS trg_calculate_order_item_amount$$
CREATE TRIGGER trg_calculate_order_item_amount
BEFORE INSERT ON sales_order_items
FOR EACH ROW
BEGIN
    DECLARE v_unit_price DECIMAL(12,2);
    DECLARE v_discount_percent DECIMAL(5,2) DEFAULT 0;
    DECLARE v_discount_value DECIMAL(10,2) DEFAULT 0;
    DECLARE v_base_amount DECIMAL(12,2);
    DECLARE v_discount_amount DECIMAL(12,2) DEFAULT 0;

    SELECT unit_price INTO v_unit_price
    FROM products
    WHERE product_id = NEW.product_id;

    IF v_unit_price IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product not found or has no price';
    END IF;

    SET v_base_amount = v_unit_price * NEW.quantity;

    IF NEW.applied_promotion_id IS NOT NULL THEN
        SELECT
            COALESCE(discount_percent, 0),
            COALESCE(discount_value, 0)
        INTO v_discount_percent, v_discount_value
        FROM promotions
        WHERE promotion_id = NEW.applied_promotion_id
          AND status = 'ACTIVE';

        IF v_discount_percent > 0 THEN
            SET v_discount_amount = v_base_amount * v_discount_percent / 100;
        ELSEIF v_discount_value > 0 THEN
            SET v_discount_amount = v_discount_value;
        END IF;
    END IF;

    SET NEW.final_amount = ROUND((v_base_amount - v_discount_amount) * 1.10, 0);

    IF NEW.final_amount < 0 THEN
        SET NEW.final_amount = 0;
    END IF;
END$$

-- =====================================================
-- TRIGGER 2: Calculate final_amount for Sales Items
-- =====================================================

DROP TRIGGER IF EXISTS trg_calculate_sale_item_amount$$
CREATE TRIGGER trg_calculate_sale_item_amount
BEFORE INSERT ON sales_items
FOR EACH ROW
BEGIN
    DECLARE v_unit_price DECIMAL(12,2);
    DECLARE v_discount_percent DECIMAL(5,2) DEFAULT 0;
    DECLARE v_discount_value DECIMAL(10,2) DEFAULT 0;
    DECLARE v_base_amount DECIMAL(12,2);
    DECLARE v_discount_amount DECIMAL(12,2) DEFAULT 0;
    DECLARE v_abs_quantity INT;
    DECLARE v_final_amount DECIMAL(12,2);

    SELECT unit_price INTO v_unit_price
    FROM products
    WHERE product_id = NEW.product_id;

    IF v_unit_price IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product not found or has no price';
    END IF;

    SET v_abs_quantity = ABS(NEW.quantity);
    SET v_base_amount = v_unit_price * v_abs_quantity;

    IF NEW.applied_promotion_id IS NOT NULL THEN
        SELECT
            COALESCE(discount_percent, 0),
            COALESCE(discount_value, 0)
        INTO v_discount_percent, v_discount_value
        FROM promotions
        WHERE promotion_id = NEW.applied_promotion_id
          AND status = 'ACTIVE';

        IF v_discount_percent > 0 THEN
            SET v_discount_amount = v_base_amount * v_discount_percent / 100;
        ELSEIF v_discount_value > 0 THEN
            SET v_discount_amount = v_discount_value;
        END IF;
    END IF;

    SET v_final_amount = ROUND((v_base_amount - v_discount_amount) * 1.10, 0);

    IF v_final_amount < 0 THEN
        SET v_final_amount = 0;
    END IF;

    IF NEW.sale_type = 'RETURN' THEN
        SET NEW.final_amount = -v_final_amount;
    ELSE
        SET NEW.final_amount = v_final_amount;
    END IF;
END$$

-- =====================================================
-- TRIGGER 3: Update Sales Total
-- =====================================================

DROP TRIGGER IF EXISTS trg_update_sales_total_after_insert$$
CREATE TRIGGER trg_update_sales_total_after_insert
AFTER INSERT ON sales_items
FOR EACH ROW
BEGIN
    UPDATE sales
    SET total_amount = (
        SELECT COALESCE(SUM(final_amount), 0)
        FROM sales_items
        WHERE sale_id = NEW.sale_id
    )
    WHERE sale_id = NEW.sale_id;
END$$

-- =====================================================
-- TRIGGER 4: Global Inventory Deduction + Correct Returns
-- =====================================================

DROP TRIGGER IF EXISTS trg_update_inventory_after_sale$$
CREATE TRIGGER trg_update_inventory_after_sale
AFTER INSERT ON sales_items
FOR EACH ROW
BEGIN
    DECLARE v_remaining_qty INT;
    DECLARE v_location_id INT;
    DECLARE v_location_qty INT;
    DECLARE v_deduct_qty INT;

    IF NEW.sale_type = 'INVOICE' THEN
        SET v_remaining_qty = NEW.quantity;

        inventory_loop: WHILE v_remaining_qty > 0 DO

            SELECT location_id, quantity
            INTO v_location_id, v_location_qty
            FROM inventory
            WHERE product_id = NEW.product_id
              AND quantity > 0
            ORDER BY quantity DESC
            LIMIT 1;

            IF v_location_id IS NULL THEN
                LEAVE inventory_loop;
            END IF;

            SET v_deduct_qty = LEAST(v_location_qty, v_remaining_qty);

            UPDATE inventory
            SET quantity = quantity - v_deduct_qty
            WHERE product_id = NEW.product_id
              AND location_id = v_location_id;

            INSERT INTO inventory_history (
                product_id,
                location_id,
                change_type,
                quantity_change,
                reference_table,
                reference_id
            ) VALUES (
                NEW.product_id,
                v_location_id,
                'OUT',
                -v_deduct_qty,
                'sales_items',
                NEW.sale_item_id
            );

            SET v_remaining_qty = v_remaining_qty - v_deduct_qty;
        END WHILE;
    END IF;

    IF NEW.sale_type = 'RETURN' THEN
        SELECT so.location_id
        INTO v_location_id
        FROM sales s
        JOIN sales_orders so ON s.order_id = so.order_id
        WHERE s.sale_id = NEW.sale_id;

        IF v_location_id IS NOT NULL THEN
            UPDATE inventory
            SET quantity = quantity - NEW.quantity
            WHERE product_id = NEW.product_id
              AND location_id = v_location_id;

            INSERT INTO inventory_history (
                product_id,
                location_id,
                change_type,
                quantity_change,
                reference_table,
                reference_id
            ) VALUES (
                NEW.product_id,
                v_location_id,
                'IN',
                -NEW.quantity,
                'sales_items',
                NEW.sale_item_id
            );
        END IF;
    END IF;
END$$

-- =====================================================
-- TRIGGER 5: Prevent Negative Inventory
-- =====================================================

DROP TRIGGER IF EXISTS trg_check_inventory_before_sale$$
CREATE TRIGGER trg_check_inventory_before_sale
BEFORE INSERT ON sales_items
FOR EACH ROW
BEGIN
    DECLARE v_available_qty INT;

    IF NEW.sale_type = 'INVOICE' AND NEW.quantity > 0 THEN
        SELECT COALESCE(SUM(quantity), 0)
        INTO v_available_qty
        FROM inventory
        WHERE product_id = NEW.product_id;

        IF v_available_qty < NEW.quantity THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Insufficient inventory for this product (global stock)';
        END IF;
    END IF;
END$$

-- =====================================================
-- TRIGGER 6: Update Customer Loyalty Points
-- =====================================================

DROP TRIGGER IF EXISTS trg_update_loyalty_after_sale$$
CREATE TRIGGER trg_update_loyalty_after_sale
AFTER INSERT ON sales
FOR EACH ROW
BEGIN
    DECLARE v_customer_id INT;
    DECLARE v_points_to_add INT;
    DECLARE v_current_total_spent DECIMAL(12,2);
    DECLARE v_new_loyalty_id INT;

    IF NEW.sale_type = 'INVOICE' AND NEW.order_id IS NOT NULL THEN
        SELECT customer_id INTO v_customer_id
        FROM sales_orders
        WHERE order_id = NEW.order_id;

        IF v_customer_id IS NOT NULL THEN
            SET v_points_to_add = FLOOR(NEW.total_amount / 10000);

            UPDATE customer_loyalty
            SET loyalty_points = loyalty_points + v_points_to_add,
                updated_at = CURRENT_TIMESTAMP
            WHERE customer_id = v_customer_id;

            SELECT COALESCE(SUM(s.total_amount), 0)
            INTO v_current_total_spent
            FROM sales_orders so
            JOIN sales s ON so.order_id = s.order_id
            WHERE so.customer_id = v_customer_id
              AND s.sale_type = 'INVOICE';

            SELECT loyalty_id INTO v_new_loyalty_id
            FROM loyalty_levels
            WHERE min_total_spent <= v_current_total_spent
            ORDER BY min_total_spent DESC
            LIMIT 1;

            IF v_new_loyalty_id IS NOT NULL THEN
                UPDATE customer_loyalty
                SET loyalty_id = v_new_loyalty_id
                WHERE customer_id = v_customer_id;
            END IF;
        END IF;
    END IF;
END$$

-- =====================================================
-- TRIGGER 7: Audit Sales Order Item Insert
-- =====================================================

DROP TRIGGER IF EXISTS trg_audit_order_item_insert$$
CREATE TRIGGER trg_audit_order_item_insert
AFTER INSERT ON sales_order_items
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        table_name,
        operation_type,
        new_value,
        record_id,
        changed_at
    ) VALUES (
        'sales_order_items',
        'INSERT',
        JSON_OBJECT(
            'order_item_id', NEW.order_item_id,
            'order_id', NEW.order_id,
            'product_id', NEW.product_id,
            'quantity', NEW.quantity,
            'applied_promotion_id', NEW.applied_promotion_id,
            'final_amount', NEW.final_amount
        ),
        NEW.order_item_id,
        CURRENT_TIMESTAMP
    );
END$$

-- =====================================================
-- TRIGGER 8: Audit Product Insert
-- =====================================================

DROP TRIGGER IF EXISTS trg_audit_product_insert$$
CREATE TRIGGER trg_audit_product_insert
AFTER INSERT ON products
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        table_name,
        operation_type,
        new_value,
        record_id,
        changed_at
    ) VALUES (
        'products',
        'INSERT',
        JSON_OBJECT(
            'product_id', NEW.product_id,
            'product_name', NEW.product_name,
            'class_id', NEW.class_id,
            'unit_price', NEW.unit_price,
            'cost', NEW.cost,
            'status', NEW.status
        ),
        NEW.product_id,
        CURRENT_TIMESTAMP
    );
END$$

-- =====================================================
-- TRIGGER 9: Audit Employee Insert
-- =====================================================

DROP TRIGGER IF EXISTS trg_audit_employee_insert$$
CREATE TRIGGER trg_audit_employee_insert
AFTER INSERT ON employees
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        table_name,
        operation_type,
        new_value,
        record_id,
        changed_at
    ) VALUES (
        'employees',
        'INSERT',
        JSON_OBJECT(
            'employee_id', NEW.employee_id,
            'first_name', NEW.first_name,
            'last_name', NEW.last_name,
            'email', NEW.email,
            'role', NEW.role,
            'department_id', NEW.department_id
        ),
        NEW.employee_id,
        CURRENT_TIMESTAMP
    );
END$$

-- =====================================================
-- TRIGGER 10: Track Delivery Status Changes
-- =====================================================

DROP TRIGGER IF EXISTS trg_track_delivery_status$$
CREATE TRIGGER trg_track_delivery_status
AFTER UPDATE ON deliveries
FOR EACH ROW
BEGIN
    IF OLD.delivery_status <> NEW.delivery_status THEN
        INSERT INTO delivery_status_history (
            delivery_id,
            old_status,
            new_status,
            changed_at
        ) VALUES (
            NEW.delivery_id,
            OLD.delivery_status,
            NEW.delivery_status,
            CURRENT_TIMESTAMP
        );
    END IF;
END$$

DELIMITER ;

-- =====================================================
-- Verification
-- =====================================================

SELECT 'All Triggers Created Successfully!' AS status;

SELECT 
    TRIGGER_NAME,
    EVENT_MANIPULATION,
    EVENT_OBJECT_TABLE,
    ACTION_TIMING
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'vinretail'
ORDER BY EVENT_OBJECT_TABLE, ACTION_TIMING, EVENT_MANIPULATION;

SELECT 'Total triggers created:' AS info, COUNT(*) AS count
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'vinretail';
