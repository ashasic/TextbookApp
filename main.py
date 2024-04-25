from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI

app = FastAPI()
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.textbook_exchange

@app.get("/books")
async def read_books():
    books = await db.books.find().to_list(100)
    return books
