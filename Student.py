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
students_collection = db.Students

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
async def register(username: str = Form(...), password: str = Form(...)):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Always hash passwords
    user = {"username": username, "password": hashed_password}
    db.students.insert_one(user)
    return {"message": "User registered successfully"}


@router.get("/register/")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
#   return FileResponse("templates/register.html")  # Return the HTML file

