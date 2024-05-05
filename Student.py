import os
import logging
import hashlib
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from logging.handlers import RotatingFileHandler
from model import Register, LoginSchema, Settings
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, APIRouter, Form, HTTPException, Request, Depends


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


load_dotenv()
student_router = APIRouter()

# Establish database connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.UIowaBookShelf
students_collection = db.students


# Creating an instance of Jinja2Templates
templates = Jinja2Templates(directory="templates")


# Configuration for JWT tokens
@AuthJWT.load_config
def get_config():
    return Settings()


@student_router.post("/login/")
async def login(
    username: str = Form(...), password: str = Form(...), Authorize: AuthJWT = Depends()
):
    user = students_collection.find_one({"username": username})
    if not user or user["password"] != hashlib.sha256(password.encode()).hexdigest():
        logger.warning(f"Login attempt failed for username: {username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = Authorize.create_access_token(subject=username)
    return JSONResponse(
        content={"message": "Login successful", "access_token": access_token},
        status_code=200,
    )
    logger.info(f"User {username} logged in successfully")
    return JSONResponse(
        content={"message": "Login successful", "access_token": access_token},
        status_code=200,
    )

    # Return user information along with the access token
    user_data = user(username=user["username"], role=user["role"])
    return JSONResponse(
        content={
            "message": "Login successful",
            "access_token": access_token,
            "user": user_data.dict(),
        },
        status_code=200,
    )


@student_router.get("/login/")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@student_router.post("/register/")
async def register(register_data: Register):
    if register_data.role not in ["admin", "regular"]:
        logger.warning("Attempt to register with invalid role")
        raise HTTPException(status_code=400, detail="Invalid role specified")

    hashed_password = hashlib.sha256(register_data.password.encode()).hexdigest()
    user = {
        "username": register_data.username,
        "password": hashed_password,
        "role": register_data.role,
    }
    result = students_collection.insert_one(user)
    if result.inserted_id:
        logger.info(f"User {register_data.username} registered successfully")
        return {"message": "User registered successfully"}
    raise HTTPException(status_code=500, detail="Failed to register user")


@student_router.get("/register/")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# New Endpoint to Get Current User
@student_router.get("/user")
async def get_current_user(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
    except AuthJWTException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    user = students_collection.find_one({"username": current_user})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"username": user["username"], "role": user["role"]}
