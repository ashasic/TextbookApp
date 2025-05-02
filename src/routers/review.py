import os
from dotenv import load_dotenv
from pymongo import MongoClient
from fastapi_jwt_auth import AuthJWT
from utils.logger import setup_logger
from utils.db import get_db, get_collection
from models.model import ReviewIn, ReviewOut
from fastapi import APIRouter, HTTPException, Depends
from fastapi_jwt_auth.exceptions import AuthJWTException


logger = setup_logger(__name__)


review_router = APIRouter()


db = get_db()
textbookCollection = db.Textbooks
reviewCollection = get_collection("Reviews")


# Create or update a review
@review_router.post("/reviews/", response_model=ReviewOut)
async def add_or_update_review(data: dict, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        isbn = data.get("isbn")
        review_text = data.get("review")
        logger.info(f"Adding or updating review by {current_user} for ISBN: {isbn}")
    except AuthJWTException as e:
        logger.error("JWT authorization failed", exc_info=True)
        raise HTTPException(status_code=e.status_code, detail=e.message)

    # Validate review data
    if not isbn or not review_text:
        logger.error("Invalid review data provided")
        raise HTTPException(status_code=400, detail="Invalid review data")

    # Check if the textbook exists
    if not textbookCollection.find_one({"isbn": isbn}):
        logger.error("Textbook not found for ISBN: %s", isbn)
        raise HTTPException(status_code=404, detail="Textbook not found")

    # Set the review dictionary
    review_dict = {"isbn": isbn, "user": current_user, "review": review_text}

    # Check if the user already has a review for this ISBN
    existing_review = reviewCollection.find_one({"isbn": isbn, "user": current_user})

    if existing_review:
        # If the review exists, update it
        reviewCollection.update_one(
            {"_id": existing_review["_id"]}, {"$set": review_dict}
        )
        review_id = existing_review["_id"]
        message = "Review updated successfully"
        logger.info("Review updated successfully")
    else:
        # Insert new review
        review_id = reviewCollection.insert_one(review_dict).inserted_id
        message = "Review added successfully"
        logger.info("Review added successfully")

    return {**review_dict, "id": str(review_id), "message": message}


# Get a specific review for a specific user and ISBN
@review_router.get("/reviews/{isbn}/{user}", response_model=ReviewOut)
async def get_specific_review(isbn: str, user: str):
    review = reviewCollection.find_one({"isbn": isbn, "user": user})
    if not review:
        logger.error("Review not found for ISBN: %s and user: %s", isbn, user)
        raise HTTPException(status_code=404, detail="Review not found")
    return {**review, "id": str(review["_id"])}


@review_router.get("/reviews/{isbn}")
async def get_reviews(isbn: str):
    try:
        logger.info(f"Fetching reviews for ISBN: {isbn}")

        # Fetch the reviews for the provided ISBN
        reviews = list(reviewCollection.find({"isbn": isbn}))

        # Log a warning if no reviews are found
        if not reviews:
            logger.warning(f"No reviews found for ISBN: {isbn}")
            return {"reviews": []}

        # Format reviews and log success
        formatted_reviews = []
        for review in reviews:
            review["_id"] = str(review["_id"])  # Convert ObjectId to string
            formatted_reviews.append(review)

        logger.info(f"Retrieved {len(formatted_reviews)} reviews for ISBN: {isbn}")

        return {"reviews": formatted_reviews}

    except Exception as e:
        logger.error(f"Error retrieving reviews for ISBN: {isbn}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving reviews")


# Delete a specific review
@review_router.delete("/reviews/{isbn}/{user}")
async def delete_review(isbn: str, user: str, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        claims = Authorize.get_raw_jwt()
    except AuthJWTException as e:
        logger.error("JWT authorization failed", exc_info=True)
        raise HTTPException(status_code=e.status_code, detail=e.message)

    # Find the review to be deleted
    review = reviewCollection.find_one({"isbn": isbn, "user": user})

    if review and (current_user == review["user"] or claims.get("role") == "admin"):
        result = reviewCollection.delete_one({"_id": review["_id"]})
        if result.deleted_count == 1:
            logger.info("Review deleted successfully")
            return {"message": "Review deleted successfully"}
        else:
            logger.error("Review not found for deletion")
            raise HTTPException(status_code=404, detail="Review not found")
    else:
        logger.error("User does not have permission to delete this review")
        raise HTTPException(
            status_code=403, detail="You do not have permission to delete this review"
        )
