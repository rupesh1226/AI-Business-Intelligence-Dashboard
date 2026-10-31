
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routes.upload import router as upload_router
from app.routes.dashboard import router as dashboard_router

# Database imports
from app.database import Base, engine
from app import models


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="AI Business Intelligence API",
    version="1.0.0"
)


# =====================================================
# DATABASE TABLE CREATION
# =====================================================

@app.on_event("startup")
def create_database_tables():

    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully!")


# =====================================================
# PROJECT DIRECTORIES
# =====================================================

# main.py is here:
# backend/app/main.py
#
# parents:
# app -> backend -> AI-Business-Intelligence

BASE_DIR = Path(__file__).resolve().parents[2]

FRONTEND_DIR = BASE_DIR / "frontend"

CSS_DIR = FRONTEND_DIR / "css"

JS_DIR = FRONTEND_DIR / "js"


print("BASE_DIR:", BASE_DIR)
print("FRONTEND_DIR:", FRONTEND_DIR)
print("CSS_DIR:", CSS_DIR)
print("JS_DIR:", JS_DIR)


# =====================================================
# API ROUTES
# =====================================================

app.include_router(
    upload_router,
    prefix="/api"
)

app.include_router(
    dashboard_router,
    prefix="/api"
)


# =====================================================
# STATIC FILES
# =====================================================

# CSS
if CSS_DIR.exists():

    app.mount(
        "/css",
        StaticFiles(directory=str(CSS_DIR)),
        name="css"
    )

else:

    print("WARNING: CSS folder not found:", CSS_DIR)


# JavaScript
if JS_DIR.exists():

    app.mount(
        "/js",
        StaticFiles(directory=str(JS_DIR)),
        name="js"
    )

else:

    print("WARNING: JS folder not found:", JS_DIR)


# =====================================================
# FRONTEND PAGES
# =====================================================

@app.get("/")
def home():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


@app.get("/index.html")
def index_page():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


@app.get("/login.html")
def login_page():

    return FileResponse(
        FRONTEND_DIR / "login.html"
    )


@app.get("/dashboard.html")
def dashboard_page():

    return FileResponse(
        FRONTEND_DIR / "dashboard.html"
    )


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "message": "AI Business Intelligence API is running"
    }
