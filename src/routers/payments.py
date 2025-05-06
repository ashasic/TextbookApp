from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from utils.db import get_db

# Mount all routes under /payments
payment_router = APIRouter(prefix="/payments", tags=["payments"])
templates = Jinja2Templates(directory="templates")

db = get_db()
textbooks = db.Textbooks

@payment_router.get(
    "/{username}/{isbn}",
    response_class=HTMLResponse,
    summary="Show payment page for a given user & book"
)
async def payment_page(request: Request, username: str, isbn: str):
    # Look up the book
    book = textbooks.find_one({"isbn": isbn}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # For now we hardcode; replace with real logic later
    amount = 12.50
    location = "Campus Library"

    # Note: template filename must match exactly
    return templates.TemplateResponse("payments.html", {
        "request": request,
        "username": username,
        "book": book,
        "amount": f"{amount:.2f}",
        "location": location
    })


@payment_router.post(
    "/confirm",
    summary="Receive confirmation of a completed payment"
)
async def confirm_payment(payload: dict):
    """
    Expects JSON:
    {
      "orderID": "...",
      "username": "...",
      "isbn": "...",
      "amount": "12.50"
    }
    """
    # TODO: record payment in your DB, e.g. db.Payments.insert_one(payload)
    return JSONResponse({"status": "success"})
