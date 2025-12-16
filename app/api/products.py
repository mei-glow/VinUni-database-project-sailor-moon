from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from enum import Enum

from app.db.session import get_db
from app.core.security import require_permission

from app.core.security import get_current_user_basic

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(get_current_user_basic)]
)



# =====================================================
# Enums
# =====================================================
class ProductStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DISCONTINUED = "DISCONTINUED"


# =====================================================
# Request Models
# =====================================================
class ProductCreate(BaseModel):
    product_name: str
    class_id: int
    unit_price: float
    cost: float
    status: ProductStatus = ProductStatus.ACTIVE


class ProductUpdate(BaseModel):
    product_name: str | None = None
    unit_price: float | None = None
    cost: float | None = None
    status: ProductStatus | None = None


# =====================================================
# CREATE PRODUCT
# Permission: PRODUCT_CREATE
# =====================================================
@router.post("", status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("PRODUCT_CREATE")),
):
    db.execute(
        text("""
        INSERT INTO products (product_name, class_id, unit_price, cost, status)
        VALUES (:n, :c, :p, :cost, :s)
        """),
        {
            "n": payload.product_name,
            "c": payload.class_id,
            "p": payload.unit_price,
            "cost": payload.cost,
            "s": payload.status.value,
        },
    )
    db.commit()
    return {"message": "Product created successfully"}


# =====================================================
# LIST PRODUCTS
# Permission: PRODUCT_VIEW
# =====================================================
@router.get("")
def list_products(
    db: Session = Depends(get_db),
    _=Depends(require_permission("PRODUCT_VIEW")),
):
    rows = db.execute(text("""
        SELECT
            p.product_id,
            p.product_name,
            p.unit_price,
            p.cost,
            p.status,
            pc.class_name,
            pc.product_group
        FROM products p
        JOIN product_class pc ON p.class_id = pc.class_id
        ORDER BY p.product_id
    """)).fetchall()

    return [
        {
            "product_id": r.product_id,
            "product_name": r.product_name,
            "unit_price": float(r.unit_price),
            "cost": float(r.cost),
            "status": r.status,
            "class_name": r.class_name,
            "product_group": r.product_group,
        }
        for r in rows
    ]


# =====================================================
# UPDATE PRODUCT
# Permission: PRODUCT_UPDATE
# =====================================================
@router.patch("/{product_id}")
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("PRODUCT_UPDATE")),
):
    fields = payload.dict(exclude_none=True)
    if not fields:
        raise HTTPException(400, "Nothing to update")

    set_clause = ", ".join(f"{k}=:{k}" for k in fields)
    fields["id"] = product_id

    db.execute(
        text(f"""
        UPDATE products
        SET {set_clause}
        WHERE product_id=:id
        """),
        fields,
    )

    db.commit()
    return {"message": "Product updated successfully"}


# =====================================================
# DELETE PRODUCT (Hard delete)
# Permission: PRODUCT_DELETE
# =====================================================
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("PRODUCT_DELETE")),
):
    db.execute(
        text("DELETE FROM products WHERE product_id=:id"),
        {"id": product_id},
    )
    db.commit()
    return {"message": "Product deleted successfully"}


# =====================================================
# LIST PRODUCT CLASSES (for UI dropdowns)
# Permission: PRODUCT_VIEW
# =====================================================
@router.get("/classes")
def list_product_classes(
    db: Session = Depends(get_db),
    _=Depends(require_permission("PRODUCT_VIEW")),
):
    rows = db.execute(text("""
        SELECT class_id, class_name, product_group
        FROM product_class
        ORDER BY class_name
    """)).fetchall()

    return [
        {
            "class_id": r.class_id,
            "class_name": r.class_name,
            "product_group": r.product_group,
        }
        for r in rows
    ]
