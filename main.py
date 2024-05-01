import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient

from dotenv import load_dotenv

load_dotenv()

import os
import requests

app = FastAPI()
client = MongoClient(os.getenv("MONGO_URI"))
db = client.UIowaBookShelf
textbooks_collection = db.Textbooks

from textbook import textbook_router

app.mount("/static", StaticFiles(directory="static"), name="static")


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


# Make HTML file the root route
@app.get("/")
async def root():
    return FileResponse("templates/index.html")


# Route to get all textbooks
@app.get("/textbooks/")
async def get_textbooks():
    try:
        books = list(textbooks_collection.find({}, {"_id": 0}))
        return JSONResponse(content={"books": books})
    except Exception as e:
        print("Failed to fetch textbooks:", e)
        raise HTTPException(
            status_code=500, detail="Failed to fetch textbooks due to an internal error"
        )


# Route to add or update a textbook entry
@app.post("/textbooks/")
async def add_or_update_textbook(textbook_data: dict):
    isbn = textbook_data.get("isbn")
    if not isbn:
        raise HTTPException(status_code=400, detail="ISBN is required")

    # Fetch additional book info from an external API
    book_data = fetch_book_info(isbn)
    if not book_data:
        raise HTTPException(status_code=404, detail="No textbook found with this ISBN")

    # Merge the data from the API with any additional data provided in the request
    book_data.update(textbook_data)

    # Update the MongoDB document
    result = textbooks_collection.update_one(
        {"isbn": isbn}, {"$set": book_data}, upsert=True
    )

    print(f"Received ISBN: {isbn}")  # Debug print, now correctly placed before return
    print(f"MongoDB update result: {result.raw_result}")  # Debug print

    if result.upserted_id or result.modified_count > 0:
        return {
            "message": "Textbook data added/updated successfully",
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


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
