import os
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

uri = os.getenv("MONGO_URI")
client = MongoClient(uri)

try:
    # Access the specific database
    db = client["UIowaBookShelf"]
    # Access the specific collection
    textbooks_collection = db["Textbooks"]

    # Example book data
    example_book = {
        "isbn": "1234567890",
        "title": "Example Book Title",
        "authors": ["John Doe"],
        "published_date": "2024-01-01",
        "description": "This is a sample description of an example book used for database connection testing.",
        "subject": "Sample Subject",
    }

    # Insert the example book into the collection
    insert_result = textbooks_collection.insert_one(example_book)
    print("Book inserted successfully. Document ID:", insert_result.inserted_id)

except Exception as e:
    print("An error occurred while trying to write to MongoDB:", e)
