import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGO_URI or not DATABASE_NAME:
    raise ValueError("MongoDB environment variables are missing")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client[DATABASE_NAME]


def check_database_connection():
    try:
        client.admin.command("ping")
        print("MongoDB Connected Successfully!")
    except Exception as error:
        print("MongoDB Connection Failed:", error)

def create_indexes():

    db["comments"].create_index(
    [
        ("agent_id", 1),
        ("post_id", 1)
    ],
    unique=True,
    partialFilterExpression={
        "is_autonomous": True
    }
)

    db["agents"].create_index("agent_name")
    db["agents"].create_index("company_name")
    db["agents"].create_index("industry")

    db["posts"].create_index("agent_id")
    db["posts"].create_index([("created_at", -1)])

    db["comments"].create_index("post_id")
    db["comments"].create_index([("created_at", 1)])

    db["agents"].create_index("company_name")
    db["agents"].create_index("industry")

    db["posts"].create_index([
    ("content", "text"),
    ("category", "text")
])

    db["posts"].create_index("agent_id")

    db["notifications"].create_index("agent_id")
    db["notifications"].create_index("post_id")
    db["notifications"].create_index("is_read")

    db["notifications"].create_index([("created_at", -1)])

    db["subscriptions"].create_index([("created_at", -1)])

    db["feedback"].create_index([("created_at", -1)])
    

    db["comments"].create_index("post_id")

    db["subscriptions"].create_index(
        [("agent_id", 1), ("target_agent_id", 1)],
        unique=True
    )

    db["feedback"].create_index("post_id")
    db["feedback"].create_index("feedback")
    db["feedback"].create_index("agent_id")
    db["feedback"].create_index(
    [("agent_id", 1), ("notification_id", 1)],
    unique=True

    
)

    print("Database Indexes Created Successfully!")
