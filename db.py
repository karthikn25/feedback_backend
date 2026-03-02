import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

try:
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME")

    client = MongoClient(MONGO_URI)

    db = client[DB_NAME]

    print("✅ MongoDB Connected Successfully")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")

