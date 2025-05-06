from datetime import datetime
from bson import ObjectId
from fastapi import Body
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from utils.db import get_collection
from utils.logger import setup_logger

dashboard_router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = setup_logger(__name__)


# --- Dashboard page ---
@dashboard_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# --- List trades (GET) ---
@dashboard_router.get("/api/trades")
async def list_trades(Authorize: AuthJWT = Depends()):
    # 1) enforce login
    try:
        Authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=401, detail="Not authorized")

    user = Authorize.get_jwt_subject()
    trades_col = get_collection("Trades")
    books_col = get_collection("Textbooks")

    raw = list(trades_col.find({"other_user": user}))
    out = []
    for t in raw:
        # 2) look up the textbook record
        book = books_col.find_one(
            {"isbn": t["isbn"]}, {"_id": 0, "title": 1, "thumbnail": 1}
        )

        title = book["title"] if book and book.get("title") else "No Title"
        thumbnail = (
            book["thumbnail"]
            if book and book.get("thumbnail")
            else "/static/images/default_book_cover.jpg"
        )

        out.append(
            {
                "id": str(t["_id"]),
                "isbn": t["isbn"],
                "other_user": t["other_user"],
                "status": t["status"],
                "title": title,
                "thumbnail": thumbnail,
                "timestamp": t["timestamp"].isoformat(),
            }
        )

    return JSONResponse(content=out)


# --- Create trade (POST) ---
@dashboard_router.post("/api/trades")
async def create_trade(payload: dict, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=401, detail="Not authorized")

    user = Authorize.get_jwt_subject()
    isbn = payload.get("isbn")
    if not isbn:
        raise HTTPException(status_code=400, detail="ISBN is required")

    col = get_collection("Trades")
    if col.find_one({"isbn": isbn, "status": "pending"}):
        raise HTTPException(
            status_code=400, detail="Someone else is already trading for this book."
        )

    trade_doc = {
        "isbn": isbn,
        "other_user": user,
        "status": "pending",
        "timestamp": datetime.utcnow(),
        # optional: populate title/thumbnail here if you want
    }
    result = col.insert_one(trade_doc)

    response = {
        "id": str(result.inserted_id),
        "isbn": isbn,
        "other_user": user,
        "status": "pending",
        "timestamp": trade_doc["timestamp"].isoformat(),
    }
    return JSONResponse(status_code=201, content=response)


# --- Update trade (PUT) ---
@dashboard_router.put("/api/trades/{trade_id}")
async def update_trade(trade_id: str, payload: dict, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=401, detail="Not authorized")

    user = Authorize.get_jwt_subject()
    col = get_collection("Trades")
    oid = ObjectId(trade_id)

    trade = col.find_one({"_id": oid, "other_user": user})
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    updates = {}
    if "status" in payload:
        updates["status"] = payload["status"]

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    col.update_one({"_id": oid}, {"$set": updates})
    return JSONResponse(content={"message": "Trade updated"})


# --- Delete trade (DELETE) ---
@dashboard_router.delete("/api/trades/{trade_id}")
async def delete_trade(trade_id: str, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=401, detail="Not authorized")

    user = Authorize.get_jwt_subject()
    col = get_collection("Trades")
    oid = ObjectId(trade_id)

    res = col.delete_one({"_id": oid, "other_user": user})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Trade not found")

    return JSONResponse(content={"message": "Trade deleted"})


# ─── Messages Page (HTML) ──────────────────────────────────
@dashboard_router.get("/dashboard/messages", response_class=HTMLResponse)
async def messages_page(request: Request):
    return templates.TemplateResponse("messages.html", {"request": request})


# ─── Fetch conversation with a peer ────────────────────────
@dashboard_router.get("/api/messages/{peer}")
async def get_conversation(peer: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    me = Authorize.get_jwt_subject()
    col = get_collection("Messages")
    # fetch both directions
    raw = col.find(
        {
            "$or": [
                {"from_user": me, "to_user": peer},
                {"from_user": peer, "to_user": me},
            ]
        }
    ).sort("timestamp", 1)
    msgs = []
    for m in raw:
        msgs.append(
            {
                "id": str(m["_id"]),
                "from_user": m["from_user"],
                "to_user": m["to_user"],
                "content": m["content"],
                "timestamp": m["timestamp"].isoformat(),
            }
        )
    return JSONResponse(msgs)


# ─── Send a new message ────────────────────────────────────
class NewMessage(BaseModel):
    to_user: str
    content: str


@dashboard_router.post("/api/messages", status_code=201)
async def post_message(payload: NewMessage, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    me = Authorize.get_jwt_subject()
    col = get_collection("Messages")
    doc = {
        "from_user": me,
        "to_user": payload.to_user,
        "content": payload.content,
        "timestamp": datetime.utcnow(),
    }
    result = col.insert_one(doc)
    return JSONResponse(
        {
            "id": str(result.inserted_id),
            "from_user": me,
            "to_user": payload.to_user,
            "content": payload.content,
            "timestamp": doc["timestamp"].isoformat(),
        }
    )
