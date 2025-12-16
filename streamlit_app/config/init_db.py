from pathlib import Path
import re
from sqlalchemy import text
from config.session import engine
from config.seed_admin import create_admin_if_not_exists

BASE_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BASE_DIR / "sql"


# =========================
# CHECK INIT
# =========================

def database_is_initialized() -> bool:
    sql = """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
          AND table_name = 'users'
    """
    with engine.connect() as conn:
        return (conn.execute(text(sql)).scalar() or 0) > 0


# =========================
# RUN NORMAL SQL (SPLIT ;)
# =========================

def run_plain_sql(path: Path):
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
    raw = re.sub(r"^\s*--.*$", "", raw, flags=re.M)

    statements = [s.strip() for s in raw.split(";") if s.strip()]

    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))


# =========================
# RUN TRIGGERS (ONE BY ONE)
# =========================

def run_triggers(path: Path):
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
    raw = re.sub(r"^\s*--.*$", "", raw, flags=re.M)

    # split by END;
    parts = re.split(r"\bEND\s*;\s*", raw, flags=re.I)

    with engine.begin() as conn:
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if "CREATE TRIGGER" not in part.upper():
                continue

            sql = part + "\nEND;"
            conn.exec_driver_sql(sql)


# =========================
# INIT DB
# =========================

def init_db():
    try:
        if database_is_initialized():
            print("⏭️ DB already initialized")
            return     


        print("🚀 Initializing DB...")

        run_plain_sql(SQL_DIR / "01_ddl.sql")
        run_plain_sql(SQL_DIR / "02_rbac.sql")
        run_plain_sql(SQL_DIR / "03_sample_data.sql")

        run_triggers(SQL_DIR / "04_triggers.sql")

        run_plain_sql(SQL_DIR / "05_generate_tran_data.sql")
        # run_plain_sql(SQL_DIR / "06_views.sql")

        create_admin_if_not_exists()

        print("🎉 DB INIT DONE")

        return True, "OK"
    except Exception as e:
        return False, str(e)
    