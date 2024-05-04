from fastapi import FastAPI, APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi_jwt_auth import AuthJWT
from pymongo import MongoClient
from pydantic import BaseModel
import os
import hashlib

from dotenv import load_dotenv
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.UIowaBookShelf
students_collection = db.students

# FastAPI Router
student_router = APIRouter()

# Creating an instance of Jinja2Templates
templates = Jinja2Templates(directory="templates")

# Pydantic models
class Register(BaseModel):
    username: str
    password: str
    role: str

class LoginSchema(BaseModel):
    username: str
    password: str

class Settings(BaseModel):
    authjwt_secret_key: str = "IowaRocks"  # Change this to your secret key

# Configuration for JWT tokens
@AuthJWT.load_config
def get_config():
    return Settings()


@student_router.post("/login/")
async def login(username: str = Form(...), password: str = Form(...), Authorize: AuthJWT = Depends()):
    user = students_collection.find_one({"username": username})
    if not user or user["password"] != hashlib.sha256(password.encode()).hexdigest():
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = Authorize.create_access_token(subject=username)

    # Return user information along with the access token
    user_data = user(username=user["username"], role=user["role"])
    return JSONResponse(content={"message": "Login successful", "access_token": access_token, "user": user_data.dict()}, status_code=200)

@student_router.get("/login/")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@student_router.post("/register/")
async def register(register_data: Register):
    if register_data.role not in ['admin', 'regular']:
        raise HTTPException(status_code=400, detail="Invalid role specified")

    hashed_password = hashlib.sha256(register_data.password.encode()).hexdigest()
    user = {"username": register_data.username, "password": hashed_password, "role": register_data.role}
    result = students_collection.insert_one(user)
    if result.inserted_id:
        return {"message": "User registered successfully"}
    raise HTTPException(status_code=500, detail="Failed to register user")

@student_router.get("/register/")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})