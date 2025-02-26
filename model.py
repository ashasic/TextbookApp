from datetime import date
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


# Data models for the Student.py
class Register(BaseModel):
    username: str
    password: str
    role: str


class LoginSchema(BaseModel):
    username: str
    password: str


class Settings(BaseModel):
    authjwt_secret_key: str = "IowaRocks"  # Secret key


# Data models for the Review.py
class ReviewIn(BaseModel):
    isbn: str
    user: str
    review: str


class ReviewOut(ReviewIn):
    id: str


# Data models for the Reservation.py
class ReservationEntry(BaseModel):
    title: str
    isbn: str
    authors: str
    published_date: str
    description: str
    subject: str
    user: str
