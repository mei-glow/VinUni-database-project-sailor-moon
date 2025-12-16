from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.session import SessionLocal
from app.models.user import User
from app.core.templates import templates

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# ---------- DB DEP ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================================================
# 1️⃣ API LOGIN (JSON) — dùng cho Swagger / test
# =====================================================
@router.post("/api/login")
def api_login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user or not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    return {
        "user_id": user.user_id,
        "username": user.username,
        "message": "Login success"
    }

# =====================================================
# 2️⃣ WEB LOGIN PAGE (HTML)
# =====================================================
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

# =====================================================
# 3️⃣ WEB LOGIN SUBMIT (FORM)
# =====================================================
@router.post("/login")
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()

    if not user or not pwd_context.verify(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid credentials"
            }
        )

    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie("user_id", str(user.user_id), httponly=True)
    return response
