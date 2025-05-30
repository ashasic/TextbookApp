import os
import uvicorn
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from utils.logger import setup_logger
from utils.templates import templates

# Routers
from routers.review import review_router
from routers.student import student_router
from routers.textbook import textbook_router
from routers.isbn_manager import isbn_router
from routers.dashboard import dashboard_router
from routers.reservation import reservation_router
from routers.payments import payment_router
from routers.messages import messages_router
from routers.users import users_router

logger = setup_logger(__name__)
logger.info("Starting application")

load_dotenv()
app = FastAPI()

# Mount static files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_path = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include routers
app.include_router(dashboard_router)
app.include_router(isbn_router, prefix="/textbooks")
app.include_router(reservation_router)
app.include_router(review_router)
app.include_router(student_router)
app.include_router(textbook_router)
app.include_router(payment_router)
app.include_router(messages_router)
app.include_router(users_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Exception Handler
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

# Public Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/browse", response_class=HTMLResponse)
async def browse(request: Request):
    return templates.TemplateResponse("browse.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Protected Routes
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/dashboard/messages", response_class=HTMLResponse)
async def messages_page(request: Request, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return templates.TemplateResponse("messages.html", {"request": request})

@app.get("/dashboard/payments", response_class=HTMLResponse)
async def payments_page(request: Request, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return templates.TemplateResponse("payments.html", {"request": request})

@app.get("/reviews.html", response_class=HTMLResponse)
async def reviews_page(request: Request):
    return templates.TemplateResponse("reviews.html", {"request": request})

@app.get("/review-form.html", response_class=HTMLResponse)
async def review_form_page(request: Request):
    return templates.TemplateResponse("review-form.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
