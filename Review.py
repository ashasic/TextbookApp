from fastapi import APIRouter, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from model import ReviewIn, ReviewOut
from pymongo import MongoClient
from bson import ObjectId
from fastapi_jwt_auth.exceptions import AuthJWTException

import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client.UIowaBookShelf
reviewCollection = db.Reviews
textbookCollection = db.Textbooks

review_router = APIRouter()

# Create or update a review
@review_router.post("/reviews/", response_model=ReviewOut)
async def add_or_update_review(review: ReviewIn, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
    except AuthJWTException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    # Validate review data
    if not review.isbn or not review.review:
        raise HTTPException(status_code=400, detail="Invalid review data")

    # Check if the textbook exists
    if not textbookCollection.find_one({"isbn": review.isbn}):
        raise HTTPException(status_code=404, detail="Textbook not found")

    # Check if the user already has a review for this ISBN
    existing_review = reviewCollection.find_one({"isbn": review.isbn, "user": current_user})

    review_dict = review.dict()
    review_dict["user"] = current_user  # Set the user as the current user

    if existing_review:
        # If the review exists, update it
        reviewCollection.update_one({"_id": existing_review["_id"]}, {"$set": review_dict})
        review_id = existing_review["_id"]
        message = "Review updated successfully"
    else:
        # Insert new review
        review_id = reviewCollection.insert_one(review_dict).inserted_id
        message = "Review added successfully"

    return {**review_dict, "id": str(review_id), "message": message}

# Get a specific review for a specific user and ISBN
@review_router.get("/reviews/{isbn}/{user}", response_model=ReviewOut)
async def get_specific_review(isbn: str, user: str):
    review = reviewCollection.find_one({"isbn": isbn, "user": user})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return {**review, "id": str(review["_id"])}

# Get reviews for a specific textbook
@review_router.get("/reviews/{isbn}")
async def get_reviews(isbn: str):
    reviews = list(reviewCollection.find({"isbn": isbn}))
    formatted_reviews = [{**review, "id": str(review["_id"])} for review in reviews]
    return {"reviews": formatted_reviews}

# Delete a specific review
@review_router.delete("/reviews/{isbn}/{user}")
async def delete_review(isbn: str, user: str, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        claims = Authorize.get_raw_jwt()
    except AuthJWTException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    # Find the review to be deleted
    review = reviewCollection.find_one({"isbn": isbn, "user": user})

    if review and (current_user == review["user"] or claims.get("role") == "admin"):
        result = reviewCollection.delete_one({"_id": review["_id"]})
        if result.deleted_count == 1:
            return {"message": "Review deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Review not found")
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this review")