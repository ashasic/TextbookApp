from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from pymongo import MongoClient
import os
from dotenv import load_dotenv

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
    if check_reservation(reservation.isbn, reservation.user):
        raise HTTPException(status_code=400, detail="You have already reserved this book.")
    reservation_dict = reservation.dict()
    reservations_collection.insert_one(reservation_dict)
    return {"message": "Reservation successful"}