from fastapi import APIRouter, HTTPException
from Models.user_models import UserCreate, UserResponse, UserLogin, UserUpdate
from db import db
from passlib.context import CryptContext
from datetime import datetime
import uuid
from typing import List

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_collection = db["users"]


# ✅ Helper: validate password
def validate_password(password: str):
    if password.startswith("$2b$"):
        raise HTTPException(status_code=400, detail="Do not send hashed password")

    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password too long (max 72 characters)")


# ✅ SIGNUP
@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    try:
        existing_user = await users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # 🔥 Validate password
        validate_password(user.password)

        hashed_password = pwd_context.hash(user.password)

        new_user = {
            "clientId": str(uuid.uuid4()),
            "name": user.name,
            "userId": user.userId,
            "email": user.email,
            "password": hashed_password,
            "role": user.role,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        await users_collection.insert_one(new_user)

        return UserResponse(**new_user)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ LOGIN
@router.post("/login", response_model=UserResponse)
async def login(user: UserLogin):

    existing_user = await users_collection.find_one({
        "userId": user.userId,
        "email": user.email
    })

    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid userId, email, or password")

    if not pwd_context.verify(user.password, existing_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid userId, email, or password")

    return UserResponse(**existing_user)


# ✅ GET USERS BY USERID
@router.get("/users/by-userid/{userId}", response_model=List[UserResponse])
async def get_users_by_userId(userId: str):
    users_cursor = users_collection.find({"userId": userId})
    users_list = await users_cursor.to_list(length=100)

    if not users_list:
        raise HTTPException(status_code=404, detail="No users found with this userId")

    return [UserResponse(**user) for user in users_list]


# ✅ GET USER BY CLIENTID
@router.get("/users/by-clientid/{clientId}", response_model=UserResponse)
async def get_user_by_clientId(clientId: str):
    user = await users_collection.find_one({"clientId": clientId})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(**user)


# ✅ DELETE USER
@router.delete("/users/remove/{clientId}")
async def delete_user_by_clientId(clientId: str):
    result = await users_collection.delete_one({"clientId": clientId})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully"}


# ✅ UPDATE USER
@router.put("/users/update/{clientId}", response_model=UserResponse)
async def update_user_by_clientId(clientId: str, user_update: UserUpdate):

    existing_user = await users_collection.find_one({"clientId": clientId})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)

    # 🔥 Handle password safely
    if "password" in update_data:
        validate_password(update_data["password"])
        update_data["password"] = pwd_context.hash(update_data["password"])

    update_data["updated_at"] = datetime.utcnow()

    await users_collection.update_one(
        {"clientId": clientId},
        {"$set": update_data}
    )

    updated_user = await users_collection.find_one({"clientId": clientId})

    return UserResponse(**updated_user)