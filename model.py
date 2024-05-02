from pydantic import BaseModel
from datetime import date
from typing import Optional


# Textbook model for database records
class Textbook(BaseModel):
    id: int
    isbn: str
    title: str
    description: str


# Textbook request model for incoming data
class TextbookRequest(BaseModel):
    isbn: str
    title: str
    description: Optional[str] = None


class ReviewIn(BaseModel):
    isbn: str
    user: str
    review: str


class ReviewOut(ReviewIn):
    id: str


class Register(BaseModel):
    username: str
    password: str


class ReservationEntry(BaseModel):
    title: str
    isbn: str
    authors: str
    published_date: str
    description: str
    subject: str
    user: str
