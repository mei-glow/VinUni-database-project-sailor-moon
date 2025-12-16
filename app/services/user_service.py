from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    role_name: str,
):
    hashed_password = pwd_context.hash(password)

    # 1. Create user
    result = db.execute(
        text("""
        INSERT INTO users (username, email, password_hash, is_active)
        VALUES (:u, :e, :p, 1)
        """),
        {"u": username, "e": email, "p": hashed_password},
    )

    user_id = result.lastrowid

    # 2. Assign role
    db.execute(
        text("""
        INSERT INTO user_roles (user_id, role_id)
        SELECT :uid, role_id FROM roles WHERE role_name = :r
        """),
        {"uid": user_id, "r": role_name},
    )

    return user_id
