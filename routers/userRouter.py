from fastapi import APIRouter, HTTPException
from Models.user_models import UserCreate, UserResponse, UserLogin
from db import db
from passlib.context import CryptContext
from datetime import datetime
import uuid
from typing import List

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_collection = db["users"]


@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate):
    try:
        # Check if email already exists
        existing_user = users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash password
        hashed_password = pwd_context.hash(user.password)

        # Create user object
        new_user = {
            "clientId": str(uuid.uuid4()),
            "name": user.name,
            "userId": user.userId ,
            "email": user.email,
            "password": hashed_password,
            "role": user.role,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        users_collection.insert_one(new_user)

        return UserResponse(
            clientId=new_user["clientId"],
            userId=new_user["userId"] if "userId" in new_user else None,
            name=new_user["name"],
            email=new_user["email"],
            role=new_user["role"],
            created_at=new_user["created_at"],
            updated_at=new_user["updated_at"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/login", response_model=UserResponse)
def login(user: UserLogin):
    # Check if user exists with both userId and email
    existing_user = users_collection.find_one({"userId": user.userId, "email": user.email})
    
    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid userId, email, or password")

    # Verify password
    if not pwd_context.verify(user.password, existing_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid userId, email, or password")

    return UserResponse(
        userId=existing_user["userId"],
        clientId=existing_user["clientId"],
        name=existing_user["name"],
        email=existing_user["email"],
        role=existing_user["role"],
        created_at=existing_user["created_at"],
        updated_at=existing_user["updated_at"]
    )

@router.get("/users/{userId}", response_model=List[UserResponse])
def get_users_by_userId(userId: str):
    users_cursor = users_collection.find({"userId": userId})
    users_list = list(users_cursor)
    
    if not users_list:
        raise HTTPException(status_code=404, detail="No users found with this userId")
    
    return [
        UserResponse(
            userId=user["userId"],
            clientId=user["clientId"],
            name=user["name"],
            email=user["email"],
            role=user["role"],
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )
        for user in users_list
    ]