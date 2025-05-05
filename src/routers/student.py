import os
import hashlib
from fastapi_jwt_auth import AuthJWT
from utils.logger import setup_logger
from fastapi.responses import JSONResponse, HTMLResponse
from utils.db import get_db, get_collection
from models.model import Register, LoginSchema, Settings
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import APIRouter, Form, HTTPException, Request, Depends
from utils.templates import templates

student_router = APIRouter()
db = get_db()
students_collection = get_collection("students")

logger = setup_logger(__name__)


# Configuration for JWT tokens
@AuthJWT.load_config
def get_config():
    return Settings()


@student_router.post("/login/")
async def login_action(
    username: str = Form(...), password: str = Form(...), Authorize: AuthJWT = Depends()
):
    """Process login form and return token."""
    user = students_collection.find_one({"username": username})
    hashed = hashlib.sha256(password.encode()).hexdigest()
    if not user or user["password"] != hashed:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = Authorize.create_access_token(subject=username)
    return JSONResponse(content={"access_token": token}, status_code=200)


@student_router.post("/register/")
async def register_action(register_data: Register):
    """Process registration form."""
    if register_data.role not in ["admin", "regular"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    hashed = hashlib.sha256(register_data.password.encode()).hexdigest()
    doc = {
        "username": register_data.username,
        "password": hashed,
        "role": register_data.role,
    }
    result = students_collection.insert_one(doc)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Registration failed")
    return JSONResponse(content={"message": "Registered successfully"}, status_code=201)


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
