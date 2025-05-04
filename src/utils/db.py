import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

# Load .env once
load_dotenv()

# Build a MongoClient that forces TLS and points at certifi's CA bundle:
_client = MongoClient(
    os.getenv("MONGO_URI"),      # e.g. "mongodb+srv://user:pass@cluster0…"
    tls=True,                    # ensure we use TLS
    tlsCAFile=certifi.where(),   # use certifi’s trusted CAs
    serverSelectionTimeoutMS=20000  # optional: adjust how long to wait for the handshake
)

# Default database
_db = _client.UIowaBookShelf

def get_client() -> MongoClient:
    return _client

def get_db():
    return _db

def get_collection(name: str):
    return _db[name]
