from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from model import ReviewIn, ReviewOut
import os

from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client.UIowaBookShelf
reviewCollection = db.Reviews
textbookCollection = db.Textbooks

review_router = APIRouter()


# Create or update a review
@review_router.post("/reviews/", response_model=ReviewOut)
async def add_or_update_review(review: ReviewIn):
    # Validate review data
    if not review.isbn or not review.user or not review.review:
        raise HTTPException(status_code=400, detail="Invalid review data")

    # Check if the textbook exists
    if not textbook_collection.find_one({"isbn": review.isbn}):
        raise HTTPException(status_code=404, detail="Textbook not found")

    # Check if the user already has a review for this ISBN
    existing_review = review_collection.find_one(
        {"isbn": review.isbn, "user": review.user}
    )

    # If the review exists, update it; otherwise, create a new review
    if existing_review:
        review_collection.update_one(
            {"isbn": review.isbn, "user": review.user}, {"$set": review.dict()}
        )
        message = "Review updated successfully"
    else:
        review_id = review_collection.insert_one(review.dict()).inserted_id
        message = "Review added successfully"

    return {**review.dict(), "id": str(review_id), "message": message}


# Get reviews for a specific textbook
@review_router.get("/reviews/{isbn}")
async def get_reviews(isbn: str):
    reviews = list(reviewCollection.find({"isbn": isbn}, {"_id": 0}))
    if not reviews:
        raise HTTPException(
            status_code=404, detail="No reviews found for this textbook"
        )
    return {"reviews": reviews}


# Delete a specific review
@review_router.delete("/reviews/{isbn}/{user}")
async def delete_review(isbn: str, user: str):
    result = review_collection.delete_one({"isbn": isbn, "user": user})
    if result.deleted_count == 1:
        return {"message": "Review deleted successfully"}
    raise HTTPException(status_code=404, detail="Review not found")
