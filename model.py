from datetime import date
from typing import Optional
from pydantic import BaseModel


# Data model for the Textbook entry
class TextbookEntry(BaseModel):
    isbn: str
    title: str
    authors: list
    published_date: str
    description: str
    subject: str


class ISBN(BaseModel):
    isbn: str


class Register(BaseModel):
    username: str
    password: str


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
