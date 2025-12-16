from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# GET CURRENT USER FROM COOKIE
# =========================
def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.cookies.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.user_id == int(user_id)).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid user")

    return user

# =========================
# PERMISSION CHECK
# =========================
def require_permission(permission_code: str):
    def checker(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        permissions = (
            db.query(Permission.permission_code)
            .join(Role.permissions)
            .join(User.roles)
            .filter(User.user_id == user.user_id)
            .all()
        )

        permission_codes = {p[0] for p in permissions}

        if permission_code not in permission_codes:
            raise HTTPException(status_code=403, detail="Forbidden")

        return user

    return checker
