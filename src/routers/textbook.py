import os
import requests
from utils.db import get_db, get_collection
from fastapi import FastAPI, APIRouter, Request, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from utils.logger import setup_logger
from services.book_service import fetch_book_info
from models.model import TextbookEntry, ISBN, Settings
from utils.templates import templates

logger = setup_logger(__name__)

app = FastAPI()

# configure JWT
@AuthJWT.load_config
def get_config():
    return Settings()

# common exception handler for AuthJWT errors
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

# router and DB handles
textbook_router = APIRouter()
db = get_db()
textbooks_collection = db.Textbooks
trades_collection    = get_collection("Trades")  # for the view/trades feature

# --- REST Endpoints for Textbooks CRUD --- #

@textbook_router.get("/textbooks/", tags=["textbooks"])
async def get_textbooks():
    logger.info("Fetching all textbooks")
    try:
        books = list(textbooks_collection.find({}, {"_id": 0}))
        return {"books": books}
    except Exception as e:
        logger.error("Failed to fetch textbooks", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error fetching textbooks")

@textbook_router.post("/textbooks/", tags=["textbooks"])
async def add_or_update_textbook(textbook_data: dict, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        username = Authorize.get_jwt_subject()
    except AuthJWTException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    isbn = textbook_data.get("isbn")
    if not isbn:
        raise HTTPException(status_code=400, detail="ISBN is required")

    existing = textbooks_collection.find_one({"isbn": isbn})
    if existing:
        return {"message": "Textbook already added"}

    book_info = fetch_book_info(isbn)
    if not book_info:
        raise HTTPException(status_code=404, detail="No textbook found with this ISBN")

    # merge and annotate
    book_info.update(textbook_data)
    book_info["added_by"] = username

    result = textbooks_collection.update_one(
        {"isbn": isbn},
        {"$set": book_info},
        upsert=True
    )

    if result.upserted_id or result.modified_count > 0:
        return {"message": "Textbook added/updated", "data": book_info}
    return {"message": "No changes made"}

@textbook_router.get("/textbooks/search/", tags=["textbooks"])
async def search_textbooks(query: str = Query(..., description="Search by ISBN, title, or author")):
    regex = {"$regex": query, "$options": "i"}
    books = list(textbooks_collection.find(
        {"$or": [{"isbn": regex}, {"title": regex}, {"authors": regex}]},
        {"_id": 0}
    ))
    return {"books": books}

@textbook_router.delete("/textbooks/{isbn}", tags=["textbooks"])
async def delete_textbook(isbn: str):
    result = textbooks_collection.delete_one({"isbn": isbn})
    if result.deleted_count == 1:
        return {"message": "Deleted successfully"}
    raise HTTPException(status_code=404, detail="Textbook not found")

# --- HTML Endpoints for detail & view pages --- #

@textbook_router.get(
    "/textbooks/{isbn}/detail",
    response_class=HTMLResponse,
    tags=["textbooks"],
    summary="Show the textbook detail & listing form"
)
async def textbook_detail(request: Request, isbn: str):
    book = textbooks_collection.find_one({"isbn": isbn}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Textbook not found")
    return templates.TemplateResponse(
        "textbook_detail.html",
        {"request": request, "book": book},
    )

@textbook_router.get(
    "/textbooks/{isbn}/view",
    response_class=HTMLResponse,
    tags=["textbooks"],
    summary="Show the textbook view page"
)
async def textbook_view(request: Request, isbn: str):
    book = textbooks_collection.find_one({"isbn": isbn}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Textbook not found")

    # load listing metadata
    listing = textbooks_collection.find_one(
        {"isbn": isbn},
        {"_id": 0, "added_by": 1, "comments": 1, "location": 1, "price": 1, "condition": 1}
    )
    return templates.TemplateResponse(
        "textbook_view.html",
        {"request": request, "book": book, "listing": listing},
    )

@textbook_router.get(
    "/textbooks/{isbn}/trades",
    response_class=JSONResponse,
    tags=["textbooks"],
    summary="Fetch interested traders for a textbook"
)
async def get_trades(isbn: str):
    trades = list(trades_collection.find(
        {"isbn": isbn},
        {"_id": 0, "user": 1, "comment": 1}
    ))
    return {"trades": trades}

