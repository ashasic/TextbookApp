import os
import requests
from dotenv import load_dotenv


load_dotenv()


def fetch_book_info(isbn: str) -> dict | None:
    """Retrieve book metadata from Google Books API."""
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": f"isbn:{isbn}", "key": os.getenv("GOOGLE_BOOKS_API_KEY")}
    resp = requests.get(url, params=params)
    if resp.status_code == 200 and resp.json().get("totalItems", 0) > 0:
        info = resp.json()["items"][0]["volumeInfo"]
        return {
            "isbn": isbn,
            "title": info.get("title", ""),
            "authors": info.get("authors", []),
            "published_date": info.get("publishedDate", ""),
            "description": info.get("description", ""),
            "subject": ", ".join(info.get("categories", [])),
            "thumbnail": info.get("imageLinks", {}).get("thumbnail", ""),
        }
    return None
