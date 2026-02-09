"""Database configuration and utilities"""

from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Optional

# MongoDB connection
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "cuba_payment"

client: Optional[MongoClient] = None
db = None


def connect_db():
    """Connect to MongoDB"""
    global client, db
    client = MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    print(f"Connected to MongoDB database: {DATABASE_NAME}")


def close_db():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")


def get_users_collection() -> Collection:
    """Get users collection"""
    return db["users"]
