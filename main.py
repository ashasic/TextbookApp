import os
import uvicorn
import logging
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from fastapi.templating import Jinja2Templates
from logging.handlers import RotatingFileHandler
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, HTTPException, Depends, Query


# routers
from Review import review_router
from Student import student_router
from textbook import textbook_router
from isbn_manager import isbn_router
from isbn_manager import isbn_router
from Reservation import reservation_router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
)
logger = logging.getLogger(__name__)
log_file_path = os.path.join(os.getcwd(), "application.log")
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=1024 * 1024 * 5, backupCount=5
)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
)
logger.addHandler(file_handler)
logger.info("Starting application")

load_dotenv()
app = FastAPI()

app.include_router(reservation_router)
app.include_router(review_router)
app.include_router(student_router)
app.include_router(textbook_router)
app.include_router(isbn_router, prefix="/textbooks")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Exception handler for JWT errors
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


origins = ["http://localhost:8000", "http://127.0.0.1:8000"]

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Make HTML file the root route
@app.get("/")
async def root():
    return FileResponse("templates/index.html")


@app.get("/browse")
async def browse():
    return FileResponse("templates/browse.html")


@app.get("/login")
async def login():
    return FileResponse("templates/login.html")


@app.get("/reviews.html")
async def reviews_page():
    return FileResponse("templates/reviews.html")


@app.get("/review-form.html")
async def review_form_page():
    return FileResponse("templates/review-form.html")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
