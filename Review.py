from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from model import Review
import os

review_router = APIRouter()

from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
# Specify the database name
db = client.UIowaBookShelf
# Specify the collection names
reviewCollection = db.Reviews
textbookCollection = db.Textbooks

# Create or update a review
@review_router.post("/reviews/")
async def add_or_update_review(review: Review):
    # Validate review data
    if not review.isbn or not review.user or not review.review:
        raise HTTPException(status_code=400, detail="Invalid review data")

    # Check if the ISBN exists in the textbooks collection
    textbook_exists = textbookCollection.find_one({"isbn": review.isbn})
    if not textbook_exists:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    # Check if the user already has a review for this ISBN
    existing_review = reviewCollection.find_one({"isbn": review.isbn, "user": review.user})

    review_data = review.dict()

    if existing_review:
        # Update the existing review
        reviewCollection.update_one({"isbn": review.isbn, "user": review.user}, {"$set": review_data})
        message = "Review updated successfully"
    else:
        # Add a new review
        reviewCollection.insert_one(review_data)
        message = "Review added successfully"

    return {"message": message}

# Get reviews for a specific textbook
@review_router.get("/reviews/{isbn}")
async def get_reviews(isbn: str):
    reviews = list(reviewCollection.find({"isbn": isbn}, {"_id": 0}))
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this textbook")

    return {"reviews": reviews}

# Delete a specific review
@review_router.delete("/reviews/{isbn}/{user}")
async def delete_review(isbn: str, user: str):
    result = reviewCollection.delete_one({"isbn": isbn, "user": user})

    if result.deleted_count > 0:
        return {"message": "Review deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Review not found")