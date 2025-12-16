from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext
from enum import Enum

from app.db.session import get_db
from app.core.security import require_permission

router = APIRouter(prefix="/admin", tags=["Admin"])

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# =====================================================
# Role Enum (Swagger dropdown)
# =====================================================
class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    SALES = "SALES"
    WAREHOUSE = "WAREHOUSE"
    DELIVERY = "DELIVERY"
    HR = "HR"
    MANAGER = "MANAGER"
    ANALYST = "ANALYST"


# =====================================================
# Request Models
# =====================================================
class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleEnum


class UpdateUserRequest(BaseModel):
    email: EmailStr | None = None
    role: RoleEnum | None = None


# =====================================================
# Create User (USER_CREATE)
# =====================================================
@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(
    payload: CreateUserRequest,
    db: Session = Depends(get_db),
    _=Depends(require_permission("USER_CREATE")),
):
    # Check duplicate username
    exists = db.execute(
        text("SELECT 1 FROM users WHERE username = :u"),
        {"u": payload.username},
    ).fetchone()

    if exists:
        raise HTTPException(400, "Username already exists")

    # Check role exists
    role = db.execute(
        text("SELECT role_id FROM roles WHERE role_name = :r"),
        {"r": payload.role.value},
    ).fetchone()

    if not role:
        raise HTTPException(400, "Role does not exist")

    # Hash password
    hashed_password = pwd_context.hash(payload.password)

    # Create user
    db.execute(
        text("""
        INSERT INTO users (username, email, password_hash, is_active)
        VALUES (:u, :e, :p, 1)
        """),
        {
            "u": payload.username,
            "e": payload.email,
            "p": hashed_password,
        },
    )

    # Assign role
    db.execute(
        text("""
        INSERT INTO user_roles (user_id, role_id)
        SELECT u.user_id, r.role_id
        FROM users u
        JOIN roles r ON r.role_name = :r
        WHERE u.username = :u
        """),
        {
            "u": payload.username,
            "r": payload.role.value,
        },
    )

    db.commit()

    return {
        "message": "User created successfully",
        "username": payload.username,
        "role": payload.role.value,
    }


# =====================================================
# List Users (USER_VIEW)
# =====================================================
@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    _=Depends(require_permission("USER_VIEW")),
):
    rows = db.execute(
        text("""
        SELECT u.user_id, u.username, u.email, u.is_active,
               GROUP_CONCAT(r.role_name) AS roles
        FROM users u
        LEFT JOIN user_roles ur ON u.user_id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.role_id
        GROUP BY u.user_id
        ORDER BY u.user_id
        """)
    ).fetchall()

    return [
        {
            "user_id": r.user_id,
            "username": r.username,
            "email": r.email,
            "is_active": bool(r.is_active),
            "roles": r.roles.split(",") if r.roles else [],
        }
        for r in rows
    ]


# =====================================================
# Update User (USER_UPDATE)
# =====================================================
@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    payload: UpdateUserRequest,
    db: Session = Depends(get_db),
    _=Depends(require_permission("USER_UPDATE")),
):
    if payload.email:
        db.execute(
            text("UPDATE users SET email=:e WHERE user_id=:id"),
            {"e": payload.email, "id": user_id},
        )

    if payload.role:
        role = db.execute(
            text("SELECT role_id FROM roles WHERE role_name=:r"),
            {"r": payload.role.value},
        ).fetchone()

        if not role:
            raise HTTPException(400, "Role does not exist")

        db.execute(
            text("DELETE FROM user_roles WHERE user_id=:id"),
            {"id": user_id},
        )

        db.execute(
            text("""
            INSERT INTO user_roles (user_id, role_id)
            VALUES (:uid, :rid)
            """),
            {"uid": user_id, "rid": role.role_id},
        )

    db.commit()
    return {"message": "User updated successfully"}


# =====================================================
# View Roles & Permissions (ROLE_VIEW)
# =====================================================
@router.get("/roles")
def list_roles(
    db: Session = Depends(get_db),
    _=Depends(require_permission("ROLE_VIEW")),
):
    rows = db.execute(
        text("""
        SELECT r.role_name, p.permission_code
        FROM roles r
        LEFT JOIN role_permissions rp ON r.role_id = rp.role_id
        LEFT JOIN permissions p ON rp.permission_id = p.permission_id
        ORDER BY r.role_name
        """)
    ).fetchall()

    result = {}
    for row in rows:
        result.setdefault(row.role_name, []).append(row.permission_code)

    return result
