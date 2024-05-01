import uuid
from pymongo import MongoClient
from dotenv import load_dotenv
import os

from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.UIowaBookShelf  # Specify the database name
collection = db.students   # Specify the collection name

# Generate a unique identifier (UUID)
unique_id = str(uuid.uuid4())

# Example user data with the unique_id as _id
example_user = {
    "_id": unique_id,
    "username": "example_user",
    "email": "example@example.com",
    "password": "example_password",
    "role": "student"  # Assuming all registered users are students
}

print("Unique ID:", unique_id)
print("Example User Data:", example_user)

try:
    # Insert example user into MongoDB
    collection.insert_one(example_user)
    print("Example user registered successfully!")
except Exception as e:
    print("Error:", e)
