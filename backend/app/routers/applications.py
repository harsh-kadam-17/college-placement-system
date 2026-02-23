from fastapi import APIRouter, HTTPException
from app.config.database import database
from pydantic import BaseModel
from enum import Enum

router = APIRouter()

# Enforce strict status values matching our MySQL ENUM
class ApplicationStatus(str, Enum):
    Applied = 'Applied'
    Interviewing = 'Interviewing'
    Selected = 'Selected'
    Rejected = 'Rejected'

class ApplicationIn(BaseModel):
    student_id: int
    company_id: int
    status: ApplicationStatus = ApplicationStatus.Applied

class ApplicationUpdate(BaseModel):
    status: ApplicationStatus

# GET: Fetch all applications (The Dashboard View)
@router.get("/")
async def get_all_applications():
    # This SQL JOIN grabs the readable names instead of just showing IDs
    query = """
        SELECT a.application_id, s.full_name, c.company_name, c.job_role, a.status, a.application_date 
        FROM Applications a
        JOIN Students s ON a.student_id = s.student_id
        JOIN Companies c ON a.company_id = c.company_id
        ORDER BY a.application_date DESC;
    """
    return await database.fetch_all(query=query)

# POST: A student applies to a company
@router.post("/")
async def add_application(application: ApplicationIn):
    query = """
        INSERT INTO Applications (student_id, company_id, status)
        VALUES (:student_id, :company_id, :status)
    """
    try:
        last_record_id = await database.execute(query=query, values=application.model_dump())
        return {"message": "Application submitted successfully!", "application_id": last_record_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT: Update an application status (e.g., from Interviewing to Selected)
@router.put("/{application_id}")
async def update_application_status(application_id: int, app_update: ApplicationUpdate):
    query = "UPDATE Applications SET status = :status WHERE application_id = :application_id"
    try:
        await database.execute(query=query, values={"status": app_update.status, "application_id": application_id})
        return {"message": f"Application status updated to {app_update.status}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # Add this at the bottom of applications.py!
@router.get("/student/{student_id}")
async def get_student_applications(student_id: int):
    query = """
        SELECT a.application_id, c.company_name, c.job_role, a.status, a.application_date 
        FROM Applications a
        JOIN Companies c ON a.company_id = c.company_id
        WHERE a.student_id = :student_id
        ORDER BY a.application_date DESC;
    """
    return await database.fetch_all(query=query, values={"student_id": student_id})