import os
from pydantic import BaseModel
from utils.logger import setup_logger
from models.model import ReservationEntry
from utils.db import get_db, get_collection
from fastapi import APIRouter, HTTPException, Depends


logger = setup_logger(__name__)
reservation_router = APIRouter()
db = get_db()
textbooks_collection = db.Textbooks
reservations_collection = get_collection("Reservations")


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


