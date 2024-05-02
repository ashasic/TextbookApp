from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from pydantic import BaseModel
import os
import hashlib

from dotenv import load_dotenv
load_dotenv()

class Register(BaseModel):
    username: str
    password: str

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.UIowaBookShelf
students_collection = db.students

router = APIRouter()
student_router = router

# Creating an instance of Jinja2Templates
templates = Jinja2Templates(directory="templates")

@router.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    user = students_collection.find_one({"username": username})
    if user and user["password"] == hashlib.sha256(password.encode()).hexdigest():
        return JSONResponse(content={"message": "Login successful"}, status_code=200)
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

@router.get("/login/")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

from fastapi import Form

@router.post("/register/")
async def register(register_data: Register):
    hashed_password = hashlib.sha256(register_data.password.encode()).hexdigest()  # Always hash passwords
    user = {"username": register_data.username, "password": hashed_password}
    result = students_collection.insert_one(user)
    if result.inserted_id:
        return {"message": "User registered successfully"}
    raise HTTPException(status_code=500, detail="Failed to register user")


@router.get("/register/")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
    return FileResponse("templates/register.html")  # Return the HTML file

