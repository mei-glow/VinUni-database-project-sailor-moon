from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.role import role_permissions

class Permission(Base):
    __tablename__ = "permissions"

    permission_id = Column(Integer, primary_key=True)
    permission_code = Column(String(100), unique=True, nullable=False)

    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions"
    )
