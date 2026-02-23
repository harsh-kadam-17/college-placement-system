# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import database

# 1. Import all your routers here
from app.routers import students, companies, applications , auth

app = FastAPI(title="College Placement Management Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# 2. Register the routers with your main app
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

@app.get("/")
def read_root():
    return {"message": "FastAPI Placement Server is running!"}