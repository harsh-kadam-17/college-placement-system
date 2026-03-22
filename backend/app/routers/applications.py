from fastapi import APIRouter, HTTPException
from app.config.database import database
from pydantic import BaseModel
from enum import Enum

router = APIRouter()


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


# GET: All applications (Admin dashboard)
@router.get("/")
async def get_all_applications():
    query = """
        SELECT a.application_id, s.full_name, c.company_name, c.job_role,
               c.package_min, c.package_max, c.min_cgpa,
               s.aggregate_cgpa, a.status, a.application_date
        FROM Applications a
        JOIN Students s ON a.student_id = s.student_id
        JOIN Companies c ON a.company_id = c.company_id
        ORDER BY a.application_date DESC;
    """
    return await database.fetch_all(query=query)


# GET: Applications for a specific student
@router.get("/student/{student_id}")
async def get_student_applications(student_id: int):
    query = """
        SELECT a.application_id, c.company_name, c.job_role,
               c.package_min, c.package_max, a.status, a.application_date
        FROM Applications a
        JOIN Companies c ON a.company_id = c.company_id
        WHERE a.student_id = :student_id
        ORDER BY a.application_date DESC;
    """
    return await database.fetch_all(query=query, values={"student_id": student_id})


# GET: Map of company_id → status for a student (used to toggle Apply/View Details)
@router.get("/student/{student_id}/status-map")
async def get_student_status_map(student_id: int):
    query = """
        SELECT company_id, status FROM Applications
        WHERE student_id = :student_id
    """
    rows = await database.fetch_all(query=query, values={"student_id": student_id})
    # Return as dict {company_id: status}
    return {row["company_id"]: row["status"] for row in rows}


# POST: Apply for a job (with all validation)
@router.post("/")
async def add_application(application: ApplicationIn):
    # 1. Fetch student profile
    student = await database.fetch_one(
        "SELECT * FROM Students WHERE student_id = :id",
        {"id": application.student_id}
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    # 2. Resume is compulsory
    if not student["resume_link"]:
        raise HTTPException(
            status_code=400,
            detail="Resume link is compulsory. Please update your profile with a valid Google Docs resume link before applying."
        )

    # 3. Fetch company
    company = await database.fetch_one(
        "SELECT * FROM Companies WHERE company_id = :id",
        {"id": application.company_id}
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    # 4. CGPA eligibility check
    if student["aggregate_cgpa"] < company["min_cgpa"]:
        raise HTTPException(
            status_code=400,
            detail=f"Eligibility check failed: Your aggregate CGPA ({student['aggregate_cgpa']}) is below the minimum required CGPA ({company['min_cgpa']}) for {company['company_name']}."
        )

    # 5. Duplicate application check
    existing = await database.fetch_one(
        "SELECT application_id FROM Applications WHERE student_id = :sid AND company_id = :cid",
        {"sid": application.student_id, "cid": application.company_id}
    )
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied to this company for this role.")

    # 6. All checks passed — insert application
    query = """
        INSERT INTO Applications (student_id, company_id, status)
        VALUES (:student_id, :company_id, :status)
    """
    try:
        last_record_id = await database.execute(query=query, values=application.model_dump())
        return {"message": f"Successfully applied to {company['company_name']}!", "application_id": last_record_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# PUT: Update application status (Admin only)
@router.put("/{application_id}")
async def update_application_status(application_id: int, app_update: ApplicationUpdate):
    query = "UPDATE Applications SET status = :status WHERE application_id = :application_id"
    try:
        await database.execute(query=query, values={"status": app_update.status, "application_id": application_id})
        return {"message": f"Application status updated to {app_update.status}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# GET: Trigger Audit Logs (auto-populated by MySQL triggers)
@router.get("/logs")
async def get_application_logs():
    query = """
        SELECT al.log_id, s.full_name AS student_name, c.company_name,
               al.action, al.old_status, al.new_status, al.logged_at
        FROM ApplicationLogs al
        JOIN Students s ON al.student_id = s.student_id
        JOIN Companies c ON al.company_id = c.company_id
        ORDER BY al.logged_at DESC
    """
    return await database.fetch_all(query=query)