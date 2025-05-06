from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from utils.db import get_collection

users_router = APIRouter()


@users_router.get("/api/users", response_model=list[str])
async def list_users(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(401, "Missing or invalid token")
    me = Authorize.get_jwt_subject()
    col = get_collection("students")
    docs = col.find({"username": {"$ne": me}}, {"_id": 0, "username": 1})
    return JSONResponse(content=[d["username"] for d in docs])
