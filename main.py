import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import requests

load_dotenv()

from textbook import textbook_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB client setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client.UIowaBookShelf
textbooks_collection = db.Textbooks

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
    return FileResponse('templates/index.html')

# Route to get all textbooks
@app.get("/textbooks/")
async def get_textbooks():
    books = list(textbooks_collection.find({}, {'_id': 0}))  
    return JSONResponse(content={"books": books})

# Route to add or update a textbook entry
@app.post("/textbooks/")
async def add_or_update_textbook(isbn_data: ISBN):
    isbn = isbn_data.isbn
    print(f"Received ISBN: {isbn}")  # Debug print
    book_data = fetch_book_info(isbn)
    if book_data:
        result = textbooks_collection.update_one({"isbn": isbn}, {"$set": book_data}, upsert=True)
        print(f"MongoDB update result: {result.raw_result}")  # Debug print
        return {"message": "Textbook data added/updated successfully", "data": book_data}
    else:
        raise HTTPException(status_code=404, detail="No textbook found with this ISBN")


# Function to fetch book information from Google Books API
def fetch_book_info(isbn):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {'q': f'isbn:{isbn}', 'key': os.getenv("GOOGLE_BOOKS_API_KEY")}
    response = requests.get(url, params=params)
    if response.status_code == 200 and response.json()['totalItems'] > 0:
        item = response.json()['items'][0]['volumeInfo']
        return {
            "isbn": isbn,
            "title": item.get("title", ""),
            "authors": item.get("authors", []),
            "published_date": item.get("publishedDate", ""),
            "description": item.get("description", ""),
            "subject": ', '.join(item.get("categories", [])),
            "thumbnail": item.get("imageLinks", {}).get("thumbnail", "No cover image available")
        }
    return None

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
