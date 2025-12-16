from sqlalchemy import Column, Integer, String, DECIMAL, Boolean
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), nullable=False)
    unit_price = Column(DECIMAL(12, 2), nullable=False)
    status = Column(Boolean, default=True)
