from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymysql.constants import CLIENT

from app.core.config import DATABASE_URL

# --------------------------------------------------
# SQLAlchemy Engine
# --------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    echo=True,
    isolation_level="AUTOCOMMIT",
    connect_args={
        "client_flag": CLIENT.MULTI_STATEMENTS
    }
)

# --------------------------------------------------
# Session factory
# --------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# --------------------------------------------------
# FastAPI dependency
# --------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
