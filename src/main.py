import uvicorn
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi_jwt_auth import AuthJWT
from utils.logger import setup_logger
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.staticfiles import StaticFiles
import os


# routers
from routers.review import review_router
from routers.student import student_router
from routers.textbook import textbook_router
from routers.isbn_manager import isbn_router
from routers.isbn_manager import isbn_router
from routers.reservation import reservation_router


logger = setup_logger(__name__)


logger.info("Starting application")


load_dotenv()
app = FastAPI()


app.include_router(reservation_router)
app.include_router(review_router)
app.include_router(student_router)
app.include_router(textbook_router)
app.include_router(isbn_router, prefix="/textbooks")

static_path = os.path.join(os.path.dirname(__file__), '..', 'static')
app.mount("/static", StaticFiles(directory=static_path), name="static")
templates_path = os.path.join(os.path.dirname(__file__), '..', 'templates')
templates = Jinja2Templates(directory=templates_path)


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
    return FileResponse(os.path.join(templates_path, "index.html"))

@app.get("/browse")
async def browse():
    return FileResponse(os.path.join(templates_path, "browse.html"))

@app.get("/login")
async def login():
    return FileResponse(os.path.join(templates_path, "login.html"))

@app.get("/reviews.html")
async def reviews_page():
    return FileResponse(os.path.join(templates_path, "reviews.html"))

@app.get("/review-form.html")
async def review_form_page():
    return FileResponse(os.path.join(templates_path, "review-form.html"))


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
