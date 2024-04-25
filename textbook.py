from fastapi import APIRouter, HTTPException, status
from model import Textbook, TextbookRequest
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

textbook_router = APIRouter()

# Dummy data storage for simplicity; CHANGE THIS TO USE MONGODB DATA STORAGE
textbook_list = []
max_id: int = 0


# Add a textbook
@textbook_router.post("/textbooks", status_code=status.HTTP_201_CREATED)
async def add_textbook(textbook: TextbookRequest):
    global max_id
    max_id += 1
    new_textbook = Textbook(id=max_id, **textbook.dict())
    textbook_list.append(new_textbook)
    return JSONResponse(content=jsonable_encoder(new_textbook))


# List all textbooks
@textbook_router.get("/textbooks")
async def list_textbooks():
    return JSONResponse(content=jsonable_encoder(textbook_list))


# Implement remaining CRUD, login, database stuff, etc below
