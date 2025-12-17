

-- =========================================================
-- PROCEDURE 1: Create Sales Order (Draft / Cart)
-- =========================================================

CREATE PROCEDURE sp_create_sales_order (
    IN p_customer_id INT,
    IN p_employee_id INT,
    IN p_location_id INT,
    IN p_note VARCHAR(255),
    IN p_delivery_phone VARCHAR(20),
    IN p_delivery_address VARCHAR(255)
)
BEGIN
    START TRANSACTION;

    INSERT INTO sales_orders (
        customer_id,
        employee_id,
        location_id,
        order_status,
        note,
        delivery_phone,
        delivery_address
    )
    VALUES (
        p_customer_id,
        p_employee_id,
        p_location_id,
        'OPEN',
        p_note,
        p_delivery_phone,
        p_delivery_address
    );

    COMMIT;
END;


-- =========================================================
-- PROCEDURE 2: Add Item to Sales Order
-- =========================================================


CREATE PROCEDURE sp_add_sales_order_item (
    IN p_order_id INT,
    IN p_product_id INT,
    IN p_quantity INT,
    IN p_promotion_id INT
)
BEGIN
    INSERT INTO sales_order_items (
        order_id,
        product_id,
        quantity,
        applied_promotion_id
    )
    VALUES (
        p_order_id,
        p_product_id,
        p_quantity,
        p_promotion_id
    );
END;


-- =========================================================
-- PROCEDURE 3: Confirm Sales Order & Generate Invoice
-- FIXED: Initialize total_amount to 0, trigger will update it
-- =========================================================


CREATE PROCEDURE sp_confirm_sales_order (
    IN p_order_id INT,
    IN p_payment_method_id INT
)
BEGIN
    DECLARE v_sale_id INT;

    START TRANSACTION;

    -- Step 1: Confirm order (lock state)
    UPDATE sales_orders
    SET order_status = 'CONFIRMED'
    WHERE order_id = p_order_id
      AND order_status = 'OPEN';

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Order not found or already confirmed';
    END IF;

    -- Step 2: Create invoice
    -- FIXED: Set total_amount = 0, trigger will update after inserting items
    INSERT INTO sales (
        sale_type,
        order_id,
        payment_method_id,
        invoice_status,
        total_amount
    )
    VALUES (
        'INVOICE',
        p_order_id,
        p_payment_method_id,
        'PAID',
        0  -- FIXED: Initialize to 0, trigger updates after items inserted
    );

    SET v_sale_id = LAST_INSERT_ID();

    -- Step 3: Copy order items into sales_items
    -- This triggers: trg_calculate_sale_item_amount + trg_update_sales_total_after_insert
    INSERT INTO sales_items (
        sale_id,
        sale_type,
        product_id,
        quantity,
        applied_promotion_id
    )
    SELECT
        v_sale_id,
        'INVOICE',
        product_id,
        quantity,
        applied_promotion_id
    FROM sales_order_items
    WHERE order_id = p_order_id;

    COMMIT;
END;


-- =========================================================
-- PROCEDURE 4: Create Delivery for Sale
-- =========================================================


CREATE PROCEDURE sp_create_delivery_for_sale (
    IN p_sale_id INT,
    IN p_from_location_id INT,
    IN p_delivery_person_id INT,
    IN p_vendor_id INT
)
BEGIN
    INSERT INTO deliveries (
        delivery_type,
        sale_id,
        from_location_id,
        delivery_person_id,
        vendor_id,
        delivery_status
    )
    VALUES (
        'FULFILLMENT',
        p_sale_id,
        p_from_location_id,
        p_delivery_person_id,
        p_vendor_id,
        'CREATED'
    );
END;


-- =========================================================
-- PROCEDURE 5: Process Sales Return
-- FIXED: Initialize total_amount to 0
-- =========================================================

CREATE PROCEDURE sp_process_return (
    IN p_original_sale_id INT,
    IN p_product_id INT,
    IN p_return_quantity INT,
    IN p_payment_method_id INT,
    IN p_return_location_id INT
)
BEGIN
    DECLARE v_return_sale_id INT;

    START TRANSACTION;

    -- Step 1: Create return sale
    -- FIXED: Set total_amount = 0, trigger will update
    INSERT INTO sales (
        sale_type,
        parent_sale_id,
        payment_method_id,
        invoice_status,
        total_amount
    )
    VALUES (
        'RETURN',
        p_original_sale_id,
        p_payment_method_id,
        'REFUNDED',
        0  -- FIXED: Initialize to 0
    );

    SET v_return_sale_id = LAST_INSERT_ID();

    -- Step 2: Insert return item (negative quantity)
    INSERT INTO sales_items (
        sale_id,
        sale_type,
        product_id,
        quantity
    )
    VALUES (
        v_return_sale_id,
        'RETURN',
        p_product_id,
        -p_return_quantity
    );

    -- Step 3: Create return delivery
    INSERT INTO deliveries (
        delivery_type,
        sale_id,
        to_location_id,
        delivery_status
    )
    VALUES (
        'RETURN',
        v_return_sale_id,
        p_return_location_id,
        'CREATED'
    );

    COMMIT;
END;

-- Verify procedures
SELECT '✅ All stored procedures updated successfully!' AS status;

SHOW PROCEDURE STATUS WHERE Db = 'vinretail';