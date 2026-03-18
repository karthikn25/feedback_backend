from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from bson import ObjectId
import asyncio
import sys
import os

# ─── Fix module path ─────────────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Models.feedback_models import Feedback
from db import db                              # ← now it will find it

router = APIRouter(prefix="/feedback", tags=["Feedback"])

feedback_collection = db["feedback"]

# ─── Auto Delete Scheduler ───────────────────────────────────────────────────

scheduler = BackgroundScheduler()

def delete_old_feedback():
    async def _delete():
        try:
            # one_month_ago = datetime.utcnow() - timedelta(days=30)
            threshold = datetime.utcnow() - timedelta(minutes=3)
            result = await feedback_collection.delete_many({"created_at": {"$lt": threshold}})
            print(f"[Scheduler] Deleted {result.deleted_count} old feedback at {datetime.utcnow()}")
        except Exception as e:
            print(f"[Scheduler] Error: {e}")
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.run_coroutine_threadsafe(_delete(), loop)
    else:
        loop.run_until_complete(_delete())

# scheduler.add_job(delete_old_feedback, "interval", days=1)
scheduler.add_job(delete_old_feedback, "interval", minutes=3)
scheduler.start()

# ─── Routes ──────────────────────────────────────────────────────────────────

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_feedback(payload: Feedback):
    user = await db["users"].find_one({
        "name": payload.name,
        "userId": payload.userId
    })

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    feedback_data = {
        "name": user["name"],
        "userId": user["userId"],
        "rating": payload.rating.value,
        "feedbackMessage": payload.feedbackMessage,
        "created_at": datetime.utcnow(),
        # "expires_at": datetime.utcnow() + timedelta(days=30),
        "expires_at": datetime.utcnow() + timedelta(minutes=3),
    }

    result = await feedback_collection.insert_one(feedback_data)
    feedback_data["_id"] = str(result.inserted_id)
    return feedback_data


@router.get("/getall")
async def get_all_feedback():
    feedbacks = []
    async for feedback in feedback_collection.find():
        feedback["_id"] = str(feedback["_id"])
        feedbacks.append(feedback)
    return feedbacks


@router.get("/{feedback_id}")
async def get_feedback(feedback_id: str):
    try:
        feedback = await feedback_collection.find_one({"_id": ObjectId(feedback_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid feedback ID format")

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    feedback["_id"] = str(feedback["_id"])
    return feedback


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(feedback_id: str):
    try:
        result = await feedback_collection.delete_one({"_id": ObjectId(feedback_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid feedback ID format")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Feedback not found")

# ─── Get feedback by userId ───────────────────────────────────────────────────
@router.get("/user/{userId}")
async def get_feedback_by_userId(userId: str):
    feedbacks = []
    async for feedback in feedback_collection.find({"userId": userId}):
        feedback["_id"] = str(feedback["_id"])
        feedbacks.append(feedback)

    if not feedbacks:
        raise HTTPException(status_code=404, detail="No feedback found for this userId")

    return feedbacks


# ─── Get feedback by name ─────────────────────────────────────────────────────
@router.get("/name/{name}")
async def get_feedback_by_name(name: str):
    feedbacks = []
    async for feedback in feedback_collection.find({"name": name}):
        feedback["_id"] = str(feedback["_id"])
        feedbacks.append(feedback)

    if not feedbacks:
        raise HTTPException(status_code=404, detail="No feedback found for this name")

    return feedbacks 