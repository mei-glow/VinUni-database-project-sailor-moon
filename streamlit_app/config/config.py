# import os
# from dotenv import load_dotenv

# load_dotenv()  # đọc file .env

# DB_HOST = os.getenv("DB_HOST")
# DB_PORT = os.getenv("DB_PORT")
# DB_NAME = os.getenv("DB_NAME")
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")

# DATABASE_URL = (
#     f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
#     f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# )


# config/config.py
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# URL-encode password to handle special characters like @
DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""

# --------------------------------------------------
# Server-level engine (NO database)
# --------------------------------------------------
SERVER_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD_ENCODED}"
    f"@{DB_HOST}:{DB_PORT}/"
)

# --------------------------------------------------
# App-level database URL
# --------------------------------------------------
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD_ENCODED}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def ensure_database_exists():
    """
    Create database if it does not exist.
    Safe to call multiple times.
    """
    server_engine = create_engine(
        SERVER_DATABASE_URL,
        isolation_level="AUTOCOMMIT"
    )

    with server_engine.connect() as conn:
        conn.execute(
            text(
                f"""
                CREATE DATABASE IF NOT EXISTS {DB_NAME}
                CHARACTER SET utf8mb4
                COLLATE utf8mb4_unicode_ci
                """
            )
        )

    server_engine.dispose()
