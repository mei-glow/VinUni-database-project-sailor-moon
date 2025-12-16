from sqlalchemy import text
from app.db.session import engine
from app.db.seed_admin import create_admin_if_not_exists

def run_sql_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()

    with engine.begin() as conn:
        conn.exec_driver_sql(
            sql,
            execution_options={"no_parameters": True}
        )


def init_db():
    # run_sql_file("sql/01_ddl.sql")
    # run_sql_file("sql/02_rbac.sql")
    # run_sql_file("sql/03_sample_data.sql")
    # run_sql_file("sql/04_triggers.sql")
    # run_sql_file("sql/05_generate_tran_data.sql")



    
    # run_sql_file("sql/06_views.sql")
    # run_sql_file("sql/06_sample_data.sql")

    create_admin_if_not_exists()
