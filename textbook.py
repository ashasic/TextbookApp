from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from model import Textbook, TextbookRequest
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pymongo import MongoClient
import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI




load_dotenv()

textbook_router = APIRouter()


app = FastAPI()
client = MongoClient(os.getenv("MONGO_URI"))
db = client.UIowaBookShelf
textbooks_collection = db.Textbooks

class TextbookEntry(BaseModel):
    isbn: str
    title: str
    authors: list
    published_date: str
    description: str
    subject: str

class ISBN(BaseModel):
    isbn: str

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

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
@app.post("/textbooks/")
async def add_or_update_textbook(textbook_data: dict, Authorize: AuthJWT = Depends()):
    # Check the current user's username from the JWT token
    try:
        Authorize.jwt_required()
        username = Authorize.get_jwt_subject()
    except AuthJWTException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    isbn = textbook_data.get("isbn")
    if not isbn:
        raise HTTPException(status_code=400, detail="ISBN is required")

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
    book_data['added_by'] = username

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
# Dummy data storage for simplicity; CHANGE THIS TO USE MONGODB DATA STORAGE
textbook_list = []
max_id: int = 0


# Add a textbook
@textbook_router.post("/textbooks", status_code=status.HTTP_201_CREATED)
async def add_textbook(textbook: TextbookRequest):
    global max_id
    max_id += 1
    new_textbook = Textbook(id=max_id, **textbook.dict())
    textbook_list.append(new_textbook)
    return JSONResponse(content=jsonable_encoder(new_textbook))


# List all textbooks
@textbook_router.get("/textbooks")
async def list_textbooks():
    return JSONResponse(content=jsonable_encoder(textbook_list))




# Implement remaining CRUD, login, database stuff, etc below
