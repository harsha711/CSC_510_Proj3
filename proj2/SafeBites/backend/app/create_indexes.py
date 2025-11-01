# backend/app/create_indexes.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from .config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def create_indexes():
    db.users.create_index("username", unique=True)
    db.dishes.create_index([("restaurant", 1), ("name", 1)], unique=True)
    print("Indexes created")

if __name__ == "__main__":
    create_indexes()
