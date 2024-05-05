import os
import logging
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from logging.handlers import RotatingFileHandler
from fastapi.responses import FileResponse, JSONResponse
from fastapi import APIRouter, File, UploadFile, HTTPException


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
)
logger = logging.getLogger(__name__)
log_file_path = os.path.join(os.getcwd(), "application.log")
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=1024 * 1024 * 5, backupCount=5
)  # 5 MB per file, max 5 files
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
)
logger.addHandler(file_handler)

load_dotenv()
isbn_router = APIRouter()

# Setup MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.UIowaBookShelf
textbooks_collection = db.Textbooks


def fetch_book_info(isbn):
    """Fetches book information from Google Books API"""
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


@isbn_router.get("/download-isbns")
async def download_isbns():
    logger.info("Downloading all ISBNs")
    try:
        # Fetch all ISBNs from MongoDB
        cursor = textbooks_collection.find({}, {"_id": 0, "isbn": 1})
        isbns = [textbook["isbn"] for textbook in cursor]

        # Create a temporary file to write ISBNs
        filename = "isbn_list.txt"
        with open(filename, "w") as file:
            for isbn in isbns:
                file.write(f"{isbn}\n")

        return FileResponse(
            path=filename, filename="isbn_list.txt", media_type="text/plain"
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Error retrieving ISBNs from database",
                "error": str(e),
            },
        )


@isbn_router.post("/upload-isbns")
async def upload_isbns(file: UploadFile = File(...)):
    logger.info(f"Processing file upload for ISBNs")
    """Processes an uploaded file of ISBNs and adds or updates textbooks"""
    content = await file.read()
    isbns = content.decode().splitlines()
    for isbn in isbns:
        book_data = fetch_book_info(isbn)
        if book_data:
            result = textbooks_collection.update_one(
                {"isbn": isbn}, {"$set": book_data}, upsert=True
            )
            logger.info(f"Updated or inserted textbook with ISBN {isbn}")
            print(
                f"Processed ISBN: {isbn}, MongoDB update result: {result.upserted_id or result.modified_count}"
            )
        else:
            logger.warning(f"No data found for ISBN {isbn}")
            print(f"No data found for ISBN: {isbn}")
    return {"message": f"Processed {len(isbns)} ISBNs"}
