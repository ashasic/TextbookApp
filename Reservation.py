from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

# Establish database connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.UIowaBookShelf
reservations_collection = db.Reservations

# Define the API router
reservation_router = APIRouter()


# Pydantic model for reservation data
class ReservationEntry(BaseModel):
    title: str
    isbn: str
    authors: str
    published_date: str
    description: str
    subject: str
    user: str


# Helper function to check existing reservation
def check_reservation(isbn, user):
    return reservations_collection.find_one({"isbn": isbn, "user": user})


# Route to create a reservation
@reservation_router.post("/reservations/", response_description="Create a reservation")
async def create_reservation(reservation: ReservationEntry):
    logger.info(f"Attempting to create a reservation")
    print(f"Received reservation request for: {reservation.title}")
    if reservations_collection.find_one(
        {"isbn": reservation.isbn, "user": reservation.user}
    ):
        logger.warning("Reservation already exists for this user and ISBN")
        raise HTTPException(
            status_code=400, detail="You have already reserved this book."
        )
    result = reservations_collection.insert_one(reservation.dict())
    if result.inserted_id:
        logger.info("Reservation created successfully")
        return {"message": "Reservation successful", "id": str(result.inserted_id)}
    raise HTTPException(status_code=500, detail="Failed to create reservation")
