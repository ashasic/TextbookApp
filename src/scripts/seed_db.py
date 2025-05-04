import sys, os
import datetime
import hashlib

# allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

from utils.db import get_collection
from services.book_service import fetch_book_info


def seed_textbooks():
    isbns = [
        "978-1-60309-511-2",
        "978-0-691-13907-2",
        "978-1-60309-501-3",
        "978-0-312-19843-4",
        "1119703611",
        "978-1-60309-502-0",
        "978-1-60309-527-3",
        "978-0-307-45525-7",
        "978-1-60309-492-4",
        "978-1-60309-520-4",
        "978-1-4000-9834-5",
        "978-1-60309-395-8",
        "978-0-06-443017-3",
        "978-1-60309-454-2",
        "978-1-60309-490-0",
        "978-1-60309-517-4",
        "978-1-60309-329-3",
        "1234567890",
    ]
    col = get_collection("Textbooks")
    count = 0
    for isbn in isbns:
        info = fetch_book_info(isbn)
        if not info:
            print(f"⚠️  No data for ISBN {isbn}")
            continue

        # upsert: insert only if isbn not already present
        res = col.update_one({"isbn": isbn}, {"$setOnInsert": info}, upsert=True)
        if res.upserted_id:
            count += 1

    print(f"Seeded {count} new textbooks.")


def seed_students():
    raw = [
        ("alice", "password123", "regular"),
        ("bob", "hunter2", "regular"),
        ("admin", "letmein", "admin"),
    ]
    col = get_collection("students")
    count = 0
    for username, pw, role in raw:
        hashed = hashlib.sha256(pw.encode()).hexdigest()
        doc = {"username": username, "password": hashed, "role": role}

        res = col.update_one({"username": username}, {"$setOnInsert": doc}, upsert=True)
        if res.upserted_id:
            count += 1

    print(f"Seeded {count} new users.")


def seed_reservations():
    items = [
        ("978-1-60309-511-2", "alice"),
        ("978-0-691-13907-2", "bob"),
    ]
    col = get_collection("Reservations")
    count = 0

    for isbn, user in items:
        doc = {
            "isbn": isbn,
            "title": "",
            "authors": "",
            "published_date": "",
            "description": "",
            "subject": "",
            "user": user,
            "timestamp": datetime.datetime.utcnow(),
        }
        res = col.update_one(
            {"isbn": isbn, "user": user}, {"$setOnInsert": doc}, upsert=True
        )
        if res.upserted_id:
            count += 1

    print(f"Seeded {count} new reservations.")


def seed_reviews():
    pts = [
        ("978-1-60309-511-2", "alice", "Loved it!"),
        ("978-0-691-13907-2", "bob", "Pretty good."),
        ("1234567890", "admin", "Test review."),
    ]
    col = get_collection("Reviews")
    count = 0

    for isbn, user, text in pts:
        doc = {
            "isbn": isbn,
            "user": user,
            "review": text,
            "timestamp": datetime.datetime.utcnow(),
        }
        res = col.update_one(
            {"isbn": isbn, "user": user}, {"$setOnInsert": doc}, upsert=True
        )
        if res.upserted_id:
            count += 1

    print(f"Seeded {count} new reviews.")


def seed_messages():
    msgs = [
        {
            "from_user": "alice",
            "to_user": "bob",
            "book_isbn": "978-1-60309-511-2",
            "content": "Is it still available?",
            "timestamp": datetime.datetime.utcnow(),
        },
        {
            "from_user": "bob",
            "to_user": "alice",
            "book_isbn": "978-1-60309-511-2",
            "content": "Yes—let me know!",
            "timestamp": datetime.datetime.utcnow(),
        },
    ]
    col = get_collection("Messages")
    count = 0

    for m in msgs:
        res = col.update_one(
            {
                "from_user": m["from_user"],
                "to_user": m["to_user"],
                "book_isbn": m["book_isbn"],
                "content": m["content"],
            },
            {"$setOnInsert": m},
            upsert=True,
        )
        if res.upserted_id:
            count += 1

    print(f"Seeded {count} new messages.")


def seed_payments():
    pays = [
        {
            "from_user": "alice",
            "to_user": "bob",
            "amount": 5.00,
            "book_isbn": "978-1-60309-511-2",
            "timestamp": datetime.datetime.utcnow(),
        },
        {
            "from_user": "charlie",
            "to_user": "alice",
            "amount": 3.50,
            "book_isbn": "978-0-691-13907-2",
            "timestamp": datetime.datetime.utcnow(),
        },
    ]
    col = get_collection("Payments")
    count = 0

    for p in pays:
        res = col.update_one(
            {
                "from_user": p["from_user"],
                "to_user": p["to_user"],
                "book_isbn": p["book_isbn"],
                "amount": p["amount"],
            },
            {"$setOnInsert": p},
            upsert=True,
        )
        if res.upserted_id:
            count += 1

    print(f"Seeded {count} new payments.")


def seed_trades():
    trades = [
        {
            "isbn": "978-1-60309-511-2",
            "other_user": "bob",
            "status": "pending",
            "timestamp": datetime.datetime.utcnow(),
        },
        {
            "isbn": "978-0-691-13907-2",
            "other_user": "charlie",
            "status": "completed",
            "timestamp": datetime.datetime.utcnow(),
        },
    ]
    col = get_collection("Trades")
    count = 0

    for t in trades:
        res = col.update_one(
            {"isbn": t["isbn"], "other_user": t["other_user"]},
            {"$setOnInsert": t},
            upsert=True,
        )
        if res.upserted_id:
            count += 1

    print(f"Seeded {count} new trades.")


def seed_all():
    seed_students()
    seed_textbooks()
    seed_reservations()
    seed_reviews()
    seed_messages()
    seed_payments()
    seed_trades()
    print("✅ Full database seeding complete.")


if __name__ == "__main__":
    seed_all()
