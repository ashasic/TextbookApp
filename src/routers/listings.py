import os
from typing import List
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, Form, File, UploadFile, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from utils.db import get_db, get_collection
from utils.logger import setup_logger
from models.model import ListingEntry, Settings

# Initialize logger and router
glogger = setup_logger(__name__)
listing_router = APIRouter()

# Ensure upload directory exists
UPLOAD_DIR = os.path.join("static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load JWT settings
@AuthJWT.load_config
def get_config():
    return Settings()

# Dependency: get current user from JWT
def get_current_user(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except AuthJWTException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return Authorize.get_jwt_subject()

# Database collections
db = get_db()
listings_collection = get_collection("Listings")
textbooks_collection = db.Textbooks

# POST /api/listings/ - create a new listing
@listing_router.post("/api/listings/", response_model=ListingEntry)
async def create_listing(
    isbn: str = Form(...),
    condition: str = Form(...),
    price: float = Form(...),
    images: List[UploadFile] = File(default=[]),  # always a list, even if empty
    user: str = Depends(get_current_user),
):
    # Verify textbook exists
    if not textbooks_collection.find_one({"isbn": isbn}):
        raise HTTPException(status_code=404, detail="Textbook not found")

    # Save uploaded images and collect URLs
    saved_urls: List[str] = []
    for img in images:
        ext = os.path.splitext(img.filename)[1] or ".jpg"
        fname = f"{uuid4().hex}{ext}"
        fpath = os.path.join(UPLOAD_DIR, fname)
        with open(fpath, "wb") as f:
            f.write(await img.read())
        saved_urls.append(f"/static/uploads/{fname}")

    # Build the listing object
    listing = ListingEntry(
        isbn=isbn,
        condition=condition,
        price=price,
        images=saved_urls,
        user=user,
        created_at=datetime.now(timezone.utc)
    )

    # Persist to the database
    result = listings_collection.insert_one(listing.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to save listing")

    glogger.info(f"User {user} created listing for ISBN {isbn}")
    return listing