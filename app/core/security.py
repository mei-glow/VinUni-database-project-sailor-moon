from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext

from app.db.session import get_db

security = HTTPBasic()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_current_user_basic(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = db.execute(
        text("""
        SELECT user_id, username, password_hash, is_active
        FROM users
        WHERE username = :u
        """),
        {"u": credentials.username},
    ).fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not pwd_context.verify(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")

    return user


def require_permission(permission_code: str):
    def _checker(
        current_user=Depends(get_current_user_basic),
        db: Session = Depends(get_db),
    ):
        has_perm = db.execute(
            text("""
            SELECT 1
            FROM user_roles ur
            JOIN role_permissions rp ON ur.role_id = rp.role_id
            JOIN permissions p ON rp.permission_id = p.permission_id
            WHERE ur.user_id = :uid
              AND p.permission_code = :perm
            LIMIT 1
            """),
            {"uid": current_user.user_id, "perm": permission_code},
        ).fetchone()

        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission_code}",
            )

        return current_user

    return _checker
