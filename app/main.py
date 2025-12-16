# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles

# from app.api import auth, dashboard
# from app.api import users, products, employees, locations
# from app.db.init_db import init_db

# app = FastAPI(title="VinRetail")

# @app.on_event("startup")
# def startup():
#     init_db()

# app.mount("/static", StaticFiles(directory="app/static"), name="static")

# # 🔐 Auth & dashboards
# app.include_router(auth.router)
# app.include_router(dashboard.router)

# # 🔥 Core business APIs
# app.include_router(users.router)
# app.include_router(products.router)
# app.include_router(employees.router)
# app.include_router(locations.router)

# @app.get("/health")
# def health():
#     return {"status": "ok"}


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, dashboard
from app.api import users, products, employees, locations
from app.db.init_db import init_db

app = FastAPI(
    title="VinRetail Admin System",
    description="Hệ thống quản trị VinRetail với RBAC",
    version="1.0.0"
)

# CORS middleware (if needed for API calls)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")
    print("✅ VinRetail Admin System started")

# Mount static files BEFORE routes
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 🔐 Auth & dashboards (UI routes)
app.include_router(auth.router, tags=["Authentication"])
app.include_router(dashboard.router, tags=["Dashboard"])

# 🔥 Core business APIs
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(products.router, prefix="/api", tags=["Products"])
app.include_router(employees.router, prefix="/api", tags=["Employees"])
app.include_router(locations.router, prefix="/api", tags=["Locations"])

@app.get("/", tags=["Health"])
def root():
    """Redirect to login"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/login")

@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "app": "VinRetail Admin",
        "version": "1.0.0"
    }