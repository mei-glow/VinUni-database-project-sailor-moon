import threading
import random
import time
from sqlalchemy import text
from config.session import SessionLocal

NUM_USERS = 100
ORDERS_PER_USER = 1


def simulate_user(user_no: int):
    """
    Each user creates 1 order with 1–3 order items
    Executed inside a single transaction
    
    """
    start_ts = time.time()
    print(f"🟡 User {user_no} START at {start_ts:.4f}")
    db = SessionLocal()
    try:
        # ----------------------------
        # Random master data
        # ----------------------------
        customer_id = random.randint(1, 50)
        employee_id = random.randint(1, 10)
        location_id = random.randint(1, 5)

        # ----------------------------
        # 1. Create sales order
        # ----------------------------
        result = db.execute(
            text("""
                INSERT INTO sales_orders
                (customer_id, employee_id, location_id, order_status)
                VALUES (:c, :e, :l, 'OPEN')
            """),
            {
                "c": customer_id,
                "e": employee_id,
                "l": location_id
            }
        )

        order_id = result.lastrowid

        # ----------------------------
        # 2. Add order items
        # ----------------------------
        num_items = random.randint(1, 3)
        product_ids = random.sample(range(1, 30), num_items)

        for product_id in product_ids:
            quantity = random.randint(1, 5)

            price = db.execute(
                text("SELECT unit_price FROM products WHERE product_id = :p"),
                {"p": product_id}
            ).scalar()

            final_amount = price * quantity

            db.execute(
                text("""
                    INSERT INTO sales_order_items
                    (order_id, product_id, quantity, final_amount)
                    VALUES (:o, :p, :q, :a)
                """),
                {
                    "o": order_id,
                    "p": product_id,
                    "q": quantity,
                    "a": final_amount
                }
            )

        # ----------------------------
        # Commit transaction
        # ----------------------------
        end_ts = time.time()
        print(f"🟢 User {user_no} END at {end_ts:.4f} (duration {end_ts - start_ts:.2f}s)")
        db.commit()
        print(f"✅ User {user_no}: Order {order_id} created")

    except Exception as e:
        db.rollback()
        print(f"❌ User {user_no} FAILED: {e}")

    finally:
        db.close()


# =========================
# Run concurrent workload
# =========================
if __name__ == "__main__":
    threads = []
    start_time = time.time()

    for i in range(NUM_USERS):
        t = threading.Thread(target=simulate_user, args=(i + 1,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()

    print("===================================")
    print(f"Simulated {NUM_USERS} concurrent users")
    print(f"Total time: {end_time - start_time:.2f} seconds")
    print("===================================")
