from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from utils.db import get_collection
from utils.logger import setup_logger
from fastapi.templating import Jinja2Templates
from utils.templates import templates

logger = setup_logger(__name__)
messages_router = APIRouter()


# serve the HTML page
@messages_router.get("/dashboard/messages", response_class=HTMLResponse)
async def messages_page(request: Request):
    return templates.TemplateResponse("messages.html", {"request": request})


# list all conversation partners
@messages_router.get("/api/conversations")
async def list_conversations(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=401, detail="Not authorized")

    user = Authorize.get_jwt_subject()
    col = get_collection("Messages")
    # find all distinct other_user/from_user
    raw = col.find(
        {"$or": [{"from_user": user}, {"to_user": user}]},
        {"from_user": 1, "to_user": 1},
    )
    partners = set()
    for m in raw:
        partners.add(m["from_user"] if m["from_user"] != user else m["to_user"])
    return JSONResponse(content=sorted(list(partners)))


# fetch the conversation with one user
@messages_router.get("/api/messages/{other_user}")
async def get_conversation(other_user: str, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=401, detail="Not authorized")
    user = Authorize.get_jwt_subject()
    if other_user == user:
        raise HTTPException(400, "Cannot message yourself")

    col = get_collection("Messages")
    raw = list(
        col.find(
            {
                "$or": [
                    {"from_user": user, "to_user": other_user},
                    {"from_user": other_user, "to_user": user},
                ]
            },
            sort=[("timestamp", 1)],
        )
    )
    out = []
    for m in raw:
        out.append(
            {
                "id": str(m["_id"]),
                "from_user": m["from_user"],
                "to_user": m["to_user"],
                "content": m["content"],
                "timestamp": m["timestamp"].isoformat(),
            }
        )
    return JSONResponse(content=out)


# send a new message
@messages_router.post("/api/messages")
async def post_message(payload: dict, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=401, detail="Not authorized")

    user = Authorize.get_jwt_subject()
    to_user = payload.get("to_user")
    content = payload.get("content", "").strip()
    if not to_user or not content:
        raise HTTPException(400, "Recipient and content required")

    col = get_collection("Messages")
    doc = {
        "from_user": user,
        "to_user": to_user,
        "content": content,
        "timestamp": datetime.utcnow(),
    }
    result = col.insert_one(doc)
    return JSONResponse(
        content={
            "id": str(result.inserted_id),
            **{k: v for k, v in doc.items() if k != "timestamp"},
            "timestamp": doc["timestamp"].isoformat(),
        },
        status_code=201,
    )
