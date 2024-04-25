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
