from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uvicorn   # ✅ Add this

from routers.userRouter import router as auth_router
from routers.feedbackRouter import router as feedback_router  # ← add this

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # add your production URL here later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only auth router
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])

# Feedback routes → /api/feedback
app.include_router(feedback_router, prefix="/api", tags=["Feedback"])

@app.get("/")
def home():
    return {"message": "Hii Karthik 🚀 Backend is running successfully!"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # ✅ Use uppercase PORT
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)