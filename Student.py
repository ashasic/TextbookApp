from fastapi import FastAPI, APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
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

# FastAPI and FastAPI Login Manager
student_router = APIRouter()
SECRET_KEY = "IowaRocks"
manager = LoginManager(SECRET_KEY, token_url="/login")

# Creating an instance of Jinja2Templates
templates = Jinja2Templates(directory="templates")

# Pydantic model for registration
class Register(BaseModel):
    username: str
    password: str
    role: str  # Added a role field

# Load user function for fastapi-login
@manager.user_loader
def load_user(username: str):
    return students_collection.find_one({"username": username})

@student_router.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    user = students_collection.find_one({"username": username})
    if user and user["password"] == hashlib.sha256(password.encode()).hexdigest():
        token = manager.create_access_token(data={"sub": username})
        return JSONResponse(content={"message": "Login successful", "token": token}, status_code=200)
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

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
