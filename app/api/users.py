from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext
from enum import Enum

from app.db.session import get_db
from app.core.security import require_permission

from app.core.security import get_current_user_basic

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_user_basic)]
)

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
# CREATE USER
# Permission: USER_CREATE
# =====================================================
@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(
    payload: CreateUserRequest,
    db: Session = Depends(get_db),
    _=Depends(require_permission("USER_CREATE")),
):
    exists = db.execute(
        text("SELECT 1 FROM users WHERE username=:u"),
        {"u": payload.username},
    ).fetchone()

    if exists:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed = pwd_context.hash(payload.password)

    db.execute(
        text("""
        INSERT INTO users (username, email, password_hash, is_active)
        VALUES (:u, :e, :p, 1)
        """),
        {"u": payload.username, "e": payload.email, "p": hashed},
    )

    db.execute(
        text("""
        INSERT INTO user_roles (user_id, role_id)
        SELECT u.user_id, r.role_id
        FROM users u
        JOIN roles r ON r.role_name=:r
        WHERE u.username=:u
        """),
        {"u": payload.username, "r": payload.role.value},
    )

    db.commit()
    return {"message": "User created successfully"}


# =====================================================
# LIST USERS
# Permission: USER_VIEW
# =====================================================
@router.get("")
def list_users(
    db: Session = Depends(get_db),
    _=Depends(require_permission("USER_VIEW")),
):
    rows = db.execute(text("""
        SELECT u.user_id, u.username, u.email, u.is_active,
               GROUP_CONCAT(r.role_name) AS roles
        FROM users u
        LEFT JOIN user_roles ur ON u.user_id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.role_id
        GROUP BY u.user_id
        ORDER BY u.user_id
    """)).fetchall()

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
# UPDATE USER (email / role)
# Permission: USER_UPDATE
# =====================================================
@router.patch("/{user_id}")
def update_user(
    user_id: int,
    payload: UpdateUserRequest,
    db: Session = Depends(get_db),
    _=Depends(require_permission("USER_UPDATE")),
):
    updated = False

    if payload.email:
        db.execute(
            text("UPDATE users SET email=:e WHERE user_id=:id"),
            {"e": payload.email, "id": user_id},
        )
        updated = True

    if payload.role:
        role = db.execute(
            text("SELECT role_id FROM roles WHERE role_name=:r"),
            {"r": payload.role.value},
        ).fetchone()

        if not role:
            raise HTTPException(400, "Role does not exist")

        db.execute(text("DELETE FROM user_roles WHERE user_id=:id"), {"id": user_id})
        db.execute(
            text("""
            INSERT INTO user_roles (user_id, role_id)
            VALUES (:uid, :rid)
            """),
            {"uid": user_id, "rid": role.role_id},
        )
        updated = True

    if not updated:
        raise HTTPException(400, "No changes provided")

    db.commit()
    return {"message": "User updated successfully"}


# =====================================================
# DISABLE USER
# Permission: USER_DISABLE
# =====================================================
@router.patch("/{user_id}/disable")
def disable_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("USER_DISABLE")),
):
    db.execute(
        text("UPDATE users SET is_active=0 WHERE user_id=:id"),
        {"id": user_id},
    )
    db.commit()
    return {"message": "User disabled successfully"}


# =====================================================
# VIEW ROLES & PERMISSIONS
# Permission: ROLE_VIEW
# =====================================================
@router.get("/roles")
def list_roles_and_permissions(
    db: Session = Depends(get_db),
    _=Depends(require_permission("ROLE_VIEW")),
):
    rows = db.execute(text("""
        SELECT r.role_name, p.permission_code
        FROM roles r
        LEFT JOIN role_permissions rp ON r.role_id = rp.role_id
        LEFT JOIN permissions p ON rp.permission_id = p.permission_id
        ORDER BY r.role_name, p.permission_code
    """)).fetchall()

    result: dict[str, list[str]] = {}
    for r in rows:
        result.setdefault(r.role_name, []).append(r.permission_code)

    return result
