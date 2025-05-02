import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env once
load_dotenv()

# Single MongoClient instance for the whole app
_client = MongoClient(os.getenv("MONGO_URI"))

# Default database
_db = _client.UIowaBookShelf


# Expose the bits you need
def get_client() -> MongoClient:
    return _client


def get_db():
    return _db


def get_collection(name: str):
    return _db[name]
