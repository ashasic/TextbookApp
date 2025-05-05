from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# Data models for the textbook.py
class TextbookEntry(BaseModel):
    isbn: str
    title: str
    authors: list
    published_date: str
    description: str
    subject: str


class ISBN(BaseModel):
    isbn: str


# Data models for the student.py
class Register(BaseModel):
    username: str
    password: str
    role: str


class LoginSchema(BaseModel):
    username: str
    password: str


class Settings(BaseModel):
    authjwt_secret_key: str = "IowaRocks"  # Secret key


# Data models for the review.py
class ReviewIn(BaseModel):
    isbn: str
    user: str
    review: str


class ReviewOut(ReviewIn):
    id: str


# Data models for the reservation.py
class ReservationEntry(BaseModel):
    title: str
    isbn: str
    authors: str
    published_date: str
    description: str
    subject: str
    user: str


# Data models for dashboard.py
class Message(BaseModel):
    id: str
    from_user: str
    to_user: str
    book_isbn: str
    content: str
    timestamp: datetime


class Payment(BaseModel):
    id: str
    from_user: str
    to_user: str
    amount: float
    book_isbn: str
    timestamp: datetime


class Trade(BaseModel):
    id: str
    isbn: str
    other_user: str
    status: str
    timestamp: datetime
    title: str
    thumbnail: str
