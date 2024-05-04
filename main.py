import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import os
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
import requests
import logging

# routers
from Student import student_router
from Reservation import reservation_router
from textbook import textbook_router
from Review import review_router
from isbn_manager import isbn_router

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.info("Starting application")


load_dotenv()

app = FastAPI()
client = MongoClient(os.getenv("MONGO_URI"))
db = client.UIowaBookShelf
textbooks_collection = db.Textbooks

app.include_router(reservation_router)
app.include_router(review_router)
app.include_router(student_router)
app.include_router(isbn_router, prefix="/textbooks")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Exception handler for JWT errors
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


origins = ["http://localhost:8000", "http://127.0.0.1:8000"]

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Data model for the Textbook entry
class TextbookEntry(BaseModel):
    isbn: str
    title: str
    authors: list
    published_date: str
    description: str
    subject: str


class ISBN(BaseModel):
    isbn: str


class Register(BaseModel):
    username: str
    password: str


# Make HTML file the root route
@app.get("/")
async def root():
    return FileResponse("templates/index.html")


@app.get("/reviews.html")
async def reviews_page():
    return FileResponse("templates/reviews.html")


@app.get("/review-form")
async def review_form_page():
    return FileResponse("templates/review-form.html")


# Route to get all textbooks
@app.get("/textbooks/")
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
@app.post("/textbooks/")
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


# Function to fetch book information from Google Books API
def fetch_book_info(isbn):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": f"isbn:{isbn}", "key": os.getenv("GOOGLE_BOOKS_API_KEY")}
    response = requests.get(url, params=params)
    if response.status_code == 200 and response.json()["totalItems"] > 0:
        item = response.json()["items"][0]["volumeInfo"]
        return {
            "isbn": isbn,
            "title": item.get("title", ""),
            "authors": item.get("authors", []),
            "published_date": item.get("publishedDate", ""),
            "description": item.get("description", ""),
            "subject": ", ".join(item.get("categories", [])),
            "thumbnail": item.get("imageLinks", {}).get(
                "thumbnail", "No cover image available"
            ),
        }
    return None


@app.delete("/textbooks/{isbn}")
async def delete_textbook(isbn: str):
    result = textbooks_collection.delete_one({"isbn": isbn})
    if result.deleted_count == 1:
        return {"message": "Textbook deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Textbook not found")


@app.get("/textbooks/search/")
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


@app.get("/login")
async def login():
    return FileResponse("templates/login.html")


@app.get("/browse")
async def browse():
    return FileResponse("templates/browse.html")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
