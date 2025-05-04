from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from utils.db import get_collection, get_db
from models.model import Message, Payment, Trade
from utils.logger import setup_logger
from utils.templates import templates
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
logger = setup_logger(__name__)
dashboard_router = APIRouter()


# serve the HTML page
@dashboard_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# API endpoints
@dashboard_router.get("/api/messages")
async def list_messages():
    col = get_collection("Messages")
    raw = list(
        col.find(
            {},
            {
                "_id": 1,
                "from_user": 1,
                "to_user": 1,
                "book_isbn": 1,
                "content": 1,
                "timestamp": 1,
            },
        )
    )
    msgs = [Message(**{**m, "id": str(m["_id"])}) for m in raw]
    return JSONResponse(content=jsonable_encoder([m.dict() for m in msgs]))


@dashboard_router.get("/api/payments")
async def list_payments():
    col = get_collection("Payments")
    raw = list(
        col.find(
            {},
            {
                "_id": 1,
                "from_user": 1,
                "to_user": 1,
                "amount": 1,
                "book_isbn": 1,
                "timestamp": 1,
            },
        )
    )
    pays = [Payment(**{**p, "id": str(p["_id"])}) for p in raw]
    return JSONResponse(content=jsonable_encoder([p.dict() for p in pays]))


@dashboard_router.get("/api/trades")
async def list_trades(Authorize: AuthJWT = Depends()):
    # require login
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db = get_db()
    trades_col = db.Trades
    books_col = db.Textbooks

    raw_trades = list(
        trades_col.find(
            {"other_user": current_user},  # only this user’s trades
            {"_id": 1, "isbn": 1, "status": 1, "timestamp": 1},
        )
    )

    out = []
    for t in raw_trades:
        # lookup book metadata
        book = books_col.find_one({"isbn": t["isbn"]}, {"title": 1, "thumbnail": 1})
        out.append(
            Trade(
                id=str(t["_id"]),
                isbn=t["isbn"],
                other_user=current_user,
                status=t["status"],
                timestamp=t["timestamp"],
                title=book.get("title", "Unknown Title") if book else "Unknown Title",
                thumbnail=(
                    book.get("thumbnail")
                    if book
                    else "/static/images/default_book_cover.png"
                ),
            ).dict()
        )

    return JSONResponse(content=jsonable_encoder(out))
