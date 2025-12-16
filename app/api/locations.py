from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from enum import Enum

from app.db.session import get_db
from app.core.security import require_permission

from app.core.security import get_current_user_basic

router = APIRouter(
    prefix="/locations",
    tags=["Locations"],
    dependencies=[Depends(get_current_user_basic)]
)



# =====================================================
# Enums
# =====================================================
class LocationType(str, Enum):
    STORE = "STORE"
    WAREHOUSE = "WAREHOUSE"


class RegionEnum(str, Enum):
    North = "North"
    South = "South"


# =====================================================
# Request Models
# =====================================================
class LocationCreate(BaseModel):
    location_name: str
    location_type: LocationType
    address: str | None = None
    city: str | None = None
    region: RegionEnum | None = None
    email: str | None = None
    store_manager_id: int | None = None


class LocationUpdate(BaseModel):
    location_name: str | None = None
    address: str | None = None
    city: str | None = None
    region: RegionEnum | None = None
    email: str | None = None
    store_manager_id: int | None = None
    close_date: str | None = None


# =====================================================
# CREATE LOCATION (ADMIN only)
# Permission used: SYSTEM_CONFIG
# =====================================================
@router.post("", status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("SYSTEM_CONFIG")),
):
    db.execute(
        text("""
        INSERT INTO locations (
            location_name,
            location_type,
            address,
            city,
            region,
            email,
            store_manager_id
        )
        VALUES (:n, :t, :a, :c, :r, :e, :m)
        """),
        {
            "n": payload.location_name,
            "t": payload.location_type.value,
            "a": payload.address,
            "c": payload.city,
            "r": payload.region.value if payload.region else None,
            "e": payload.email,
            "m": payload.store_manager_id,
        },
    )
    db.commit()
    return {"message": "Location created successfully"}


# =====================================================
# LIST LOCATIONS (ADMIN only)
# =====================================================
@router.get("")
def list_locations(
    db: Session = Depends(get_db),
    _=Depends(require_permission("SYSTEM_CONFIG")),
):
    rows = db.execute(text("""
        SELECT
            location_id,
            location_name,
            location_type,
            city,
            region,
            isnull(close_date) = 1 AS is_active
        FROM locations
        ORDER BY location_id
    """)).fetchall()

    return [
        {
            "location_id": r.location_id,
            "location_name": r.location_name,
            "location_type": r.location_type,
            "city": r.city,
            "region": r.region,
            "is_active": bool(r.is_active),
        }
        for r in rows
    ]


# =====================================================
# UPDATE LOCATION (ADMIN only)
# =====================================================
@router.patch("/{location_id}")
def update_location(
    location_id: int,
    payload: LocationUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("SYSTEM_CONFIG")),
):
    fields = payload.dict(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=400, detail="Nothing to update")

    set_clause = ", ".join(f"{k}=:{k}" for k in fields)
    fields["id"] = location_id

    db.execute(
        text(f"UPDATE locations SET {set_clause} WHERE location_id=:id"),
        fields,
    )
    db.commit()
    return {"message": "Location updated successfully"}


# =====================================================
# SOFT CLOSE LOCATION (ADMIN only)
# =====================================================
@router.patch("/{location_id}/close")
def close_location(
    location_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("SYSTEM_CONFIG")),
):
    db.execute(
        text("""
        UPDATE locations
        SET close_date = CURRENT_DATE
        WHERE location_id = :id
        """),
        {"id": location_id},
    )
    db.commit()
    return {"message": "Location closed"}
