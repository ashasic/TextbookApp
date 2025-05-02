import os
import requests
from utils.db import get_db
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT
from utils.logger import setup_logger
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from fastapi.templating import Jinja2Templates
from models.model import TextbookEntry, ISBN
from fastapi.middleware.cors import CORSMiddleware
from services.book_service import fetch_book_info
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import APIRouter, FastAPI, HTTPException, Depends, Query


logger = setup_logger(__name__)


app = FastAPI()
textbook_router = APIRouter()


db = get_db()
textbooks_collection = db.Textbooks


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


async def delete_textbook(isbn: str):
    result = textbooks_collection.delete_one({"isbn": isbn})
    if result.deleted_count == 1:
        return {"message": "Textbook deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Textbook not found")


# Route to get all textbooks
@textbook_router.get("/textbooks/")
async def get_textbooks():
    logger.info("Fetching all textbooks")
    try:
        books = list(textbooks_collection.find({}, {"_id": 0}))
        logger.info(f"Number of textbooks fetched: {len(books)}")
        return JSONResponse(content={"books": books})
    except Exception as e:
        logger.error(f"Failed to fetch textbooks: {e}")
        print("Failed to fetch textbooks:", e)
        raise HTTPException(
            status_code=500, detail="Failed to fetch textbooks due to an internal error"
        )


# Route to add or update a textbook entry
@textbook_router.post("/textbooks/")
async def add_or_update_textbook(textbook_data: dict, Authorize: AuthJWT = Depends()):
    logger.info(f"Attempting to add or update textbook")
    # Check the current user's username from the JWT token
    try:
        Authorize.jwt_required()
        username = Authorize.get_jwt_subject()
    except AuthJWTException as e:
        logger.warning(f"Request failed")
        raise HTTPException(status_code=e.status_code, detail=e.message)

    isbn = textbook_data.get("isbn")
    if not isbn:
        raise HTTPException(status_code=400, detail="ISBN is required")
    logger.info(f"Received textbook data: {textbook_data}")

    # Check if the textbook already exists in the database
    existing_book = textbooks_collection.find_one({"isbn": isbn})
    if existing_book:
        # If the book exists and no new data is given to update, return an error
        return {"message": "Textbook already added.."}

    # Fetch additional book info from an external API
    book_data = fetch_book_info(isbn)
    if not book_data:
        raise HTTPException(status_code=404, detail="No textbook found with this ISBN")

    # Merge the data from the API with any additional data provided in the request
    book_data.update(textbook_data)

    # Add the username to the textbook data
    book_data["added_by"] = username

    # Update the MongoDB document
    result = textbooks_collection.update_one(
        {"isbn": isbn}, {"$set": book_data}, upsert=True
    )

    if result.upserted_id or result.modified_count > 0:
        return {
            "message": "Textbook data added successfully",
            "data": book_data,
        }
    else:
        return {"message": "No changes made to the textbook"}


@textbook_router.get("/textbooks/search/")
async def search_textbooks(
    query: str = Query(
        None, title="Search Query", description="Search by ISBN, title, or author"
    )
):
    regex_query = {"$regex": query, "$options": "i"}  # Case-insensitive search
    books = list(
        textbooks_collection.find(
            {
                "$or": [
                    {"isbn": regex_query},
                    {"title": regex_query},
                    {"authors": regex_query},
                ]
            },
            {"_id": 0},
        )
    )
    return {"books": books}
    regex_query = {"$regex": query, "$options": "i"}  # Case-insensitive search
    books = list(
        textbooks_collection.find(
            {
                "$or": [
                    {"isbn": regex_query},
                    {"title": regex_query},
                    {"authors": regex_query},
                ]
            },
            {"_id": 0},
        )
    )
    return {"books": books}


@textbook_router.delete("/textbooks/{isbn}")
async def delete_textbook(isbn: str):
    result = textbooks_collection.delete_one({"isbn": isbn})
    if result.deleted_count == 1:
        return {"message": "Textbook deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Textbook not found")
