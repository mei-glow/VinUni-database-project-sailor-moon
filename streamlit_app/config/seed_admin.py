import os
from sqlalchemy import text
from passlib.context import CryptContext
from config.session import engine
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def create_admin_if_not_exists():
    username = os.getenv("ADMIN_USERNAME")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not all([username, email, password]):
        print("⚠️ ADMIN credentials not set — skipping admin creation")
        return

    password = password.strip()
    hashed_password = pwd_context.hash(password)

    with engine.begin() as conn:
        # 1️⃣ Check if admin already exists
        exists = conn.execute(
            text("SELECT 1 FROM users WHERE username = :u"),
            {"u": username}
        ).fetchone()

        if exists:
            print("✅ Admin user already exists — skipping")
            return

        # 2️⃣ Create admin user
        conn.execute(
            text("""
                INSERT INTO users (username, email, password_hash, is_active, created_at)
                VALUES (:u, :e, :p, 1, NOW())
            """),
            {"u": username, "e": email, "p": hashed_password}
        )

        # 3️⃣ Assign ADMIN role
        conn.execute(
            text("""
                INSERT INTO user_roles (user_id, role_id)
                SELECT u.user_id, r.role_id
                FROM users u
                JOIN roles r ON r.role_name = 'ADMIN'
                WHERE u.username = :u
            """),
            {"u": username}
        )

    print("🚀 Admin user ensured successfully")
