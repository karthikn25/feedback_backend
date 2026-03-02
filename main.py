from fastapi import FastAPI
from dotenv import load_dotenv
import os
import uvicorn   # ✅ Add this

from routers.userRouter import router as auth_router

load_dotenv()

app = FastAPI()

# Include only auth router
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])

@app.get("/")
def home():
    return {"message": "Hii Karthik 🚀 Backend is running successfully!"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # ✅ Use uppercase PORT
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)