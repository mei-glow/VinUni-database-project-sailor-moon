from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.templates import templates
from app.core.deps import get_current_user
from app.db.session import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    row = db.execute(text("SELECT * FROM vw_dashboard_kpi")).fetchone()

    kpi = {
        "total_sales": row.total_sales if row else 0,
        "total_revenue": row.total_revenue if row else 0,
        "total_products": row.total_products if row else 0,
    }

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "kpi": kpi}
    )
