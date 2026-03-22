from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import database
from app.routers import auth, students, companies, applications

# Initialize the FastAPI app
app = FastAPI(title="College Placement System API")

# Allow the frontend (plain HTML files) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect / disconnect database on app lifecycle
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ==========================================
# --- Mount all routers under /api ---
# ==========================================

# Auth endpoints: POST /api/auth/register  and  POST /api/auth/login
app.include_router(auth.router,         prefix="/api/auth",         tags=["Auth"])

# Student endpoints: GET/POST /api/students/  and  GET/PUT /api/students/{id}
app.include_router(students.router,     prefix="/api/students",     tags=["Students"])

# Company endpoints: GET/POST /api/companies/
app.include_router(companies.router,    prefix="/api/companies",    tags=["Companies"])

# Application endpoints: GET/POST /api/applications/  PUT /api/applications/{id}  GET /api/applications/student/{id}
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])

@app.get("/")
async def root():
    return {"message": "College Placement System API is running."}