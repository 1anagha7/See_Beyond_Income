from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router
import database

# Initialize database tables and seed data
database.init_db()

app = FastAPI(title="SBI See Beyond Income Platform API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include database-backed LangGraph-integrated API router
app.include_router(api_router)