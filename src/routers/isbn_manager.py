import os
import requests
from utils.db import get_db
from utils.logger import setup_logger
from services.book_service import fetch_book_info
from fastapi.responses import FileResponse, JSONResponse
from fastapi import APIRouter, File, UploadFile, HTTPException


logger = setup_logger(__name__)
isbn_router = APIRouter()
db = get_db()
textbooks_collection = db.Textbooks


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
