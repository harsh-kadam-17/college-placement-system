from fastapi import APIRouter, HTTPException
from app.config.database import database
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class StudentIn(BaseModel):
    full_name: str
    email: str
    department: str
    cgpa_year1: float = 0.0
    cgpa_year2: float = 0.0
    cgpa_year3: float = 0.0
    cgpa_year4: float = 0.0
    aggregate_cgpa: float = 0.0
    resume_link: Optional[str] = None
    marksheet_link: Optional[str] = None


class StudentUpdate(BaseModel):
    full_name: str
    department: str
    cgpa_year1: float = 0.0
    cgpa_year2: float = 0.0
    cgpa_year3: float = 0.0
    cgpa_year4: float = 0.0
    aggregate_cgpa: float = 0.0
    resume_link: Optional[str] = None
    marksheet_link: Optional[str] = None


@router.get("/")
async def get_all_students():
    query = "SELECT * FROM Students"
    return await database.fetch_all(query=query)


@router.get("/{student_id}")
async def get_student(student_id: int):
    query = "SELECT * FROM Students WHERE student_id = :student_id"
    result = await database.fetch_one(query=query, values={"student_id": student_id})
    if not result:
        raise HTTPException(status_code=404, detail="Student not found.")
    return result


@router.post("/")
async def add_student(student: StudentIn):
    query = """
        INSERT INTO Students (full_name, email, department,
            cgpa_year1, cgpa_year2, cgpa_year3, cgpa_year4,
            aggregate_cgpa, resume_link, marksheet_link)
        VALUES (:full_name, :email, :department,
            :cgpa_year1, :cgpa_year2, :cgpa_year3, :cgpa_year4,
            :aggregate_cgpa, :resume_link, :marksheet_link)
    """
    try:
        last_record_id = await database.execute(query=query, values=student.model_dump())
        return {"message": "Student added successfully!", "student_id": last_record_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{student_id}")
async def delete_student(student_id: int):
    existing = await database.fetch_one(
        "SELECT student_id FROM Students WHERE student_id = :id", {"id": student_id}
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Student not found.")
    await database.execute("DELETE FROM Students WHERE student_id = :id", {"id": student_id})
    return {"message": "Student deleted successfully."}


@router.put("/{student_id}")
async def update_student(student_id: int, student: StudentUpdate):
    query = """
        UPDATE Students
        SET full_name = :full_name, department = :department,
            cgpa_year1 = :cgpa_year1, cgpa_year2 = :cgpa_year2,
            cgpa_year3 = :cgpa_year3, cgpa_year4 = :cgpa_year4,
            aggregate_cgpa = :aggregate_cgpa,
            resume_link = :resume_link, marksheet_link = :marksheet_link
        WHERE student_id = :student_id
    """
    try:
        await database.execute(query=query, values={"student_id": student_id, **student.model_dump()})
        return {"message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))