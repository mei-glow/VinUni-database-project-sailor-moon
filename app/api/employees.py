from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text
from enum import Enum

from app.db.session import get_db
from app.core.security import require_permission

from app.core.security import get_current_user_basic

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
    dependencies=[Depends(get_current_user_basic)]
)


# =====================================================
# Enums
# =====================================================
class Gender(str, Enum):
    M = "M"
    F = "F"
    OTHER = "OTHER"


class EmployeeRole(str, Enum):
    Staff = "Staff"
    Warehouse = "Warehouse"
    Manager = "Manager"
    Delivery = "Delivery"
    Admin = "Admin"


# =====================================================
# Request Models
# =====================================================
class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    gender: Gender
    department_id: int
    role: EmployeeRole
    phone: str | None = None
    supervisor_id: int | None = None


class EmployeeUpdate(BaseModel):
    email: EmailStr | None = None
    role: EmployeeRole | None = None
    phone: str | None = None
    supervisor_id: int | None = None
    is_inactive: bool | None = None


# =====================================================
# CREATE EMPLOYEE (ADMIN only)
# Permission: SYSTEM_CONFIG
# =====================================================
@router.post("", status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("SYSTEM_CONFIG")),
):
    db.execute(
        text("""
        INSERT INTO employees (
            first_name,
            last_name,
            email,
            gender,
            department_id,
            role,
            phone,
            supervisor_id
        )
        VALUES (
            :first_name,
            :last_name,
            :email,
            :gender,
            :department_id,
            :role,
            :phone,
            :supervisor_id
        )
        """),
        payload.dict(),
    )
    db.commit()
    return {"message": "Employee created successfully"}


# =====================================================
# LIST EMPLOYEES (ADMIN only)
# =====================================================
@router.get("")
def list_employees(
    db: Session = Depends(get_db),
    _=Depends(require_permission("SYSTEM_CONFIG")),
):
    rows = db.execute(text("""
        SELECT
            e.employee_id,
            e.first_name,
            e.last_name,
            e.email,
            e.gender,
            e.role,
            e.is_inactive,
            d.department_name,
            s.first_name AS supervisor_first_name,
            s.last_name AS supervisor_last_name
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.department_id
        LEFT JOIN employees s ON e.supervisor_id = s.employee_id
        ORDER BY e.employee_id
    """)).fetchall()

    return [
        {
            "employee_id": r.employee_id,
            "first_name": r.first_name,
            "last_name": r.last_name,
            "email": r.email,
            "gender": r.gender,
            "role": r.role,
            "is_inactive": bool(r.is_inactive),
            "department": r.department_name,
            "supervisor": (
                f"{r.supervisor_first_name} {r.supervisor_last_name}"
                if r.supervisor_first_name else None
            ),
        }
        for r in rows
    ]


# =====================================================
# UPDATE EMPLOYEE (ADMIN only)
# =====================================================
@router.patch("/{employee_id}")
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("SYSTEM_CONFIG")),
):
    fields = payload.dict(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=400, detail="Nothing to update")

    set_clause = ", ".join(f"{k}=:{k}" for k in fields)
    fields["id"] = employee_id

    db.execute(
        text(f"""
        UPDATE employees
        SET {set_clause}
        WHERE employee_id = :id
        """),
        fields,
    )
    db.commit()
    return {"message": "Employee updated successfully"}


# =====================================================
# DISABLE EMPLOYEE (ADMIN only)
# =====================================================
@router.patch("/{employee_id}/disable")
def disable_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("SYSTEM_CONFIG")),
):
    db.execute(
        text("""
        UPDATE employees
        SET is_inactive = 1
        WHERE employee_id = :id
        """),
        {"id": employee_id},
    )
    db.commit()
    return {"message": "Employee disabled successfully"}
