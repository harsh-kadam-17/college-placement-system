from fastapi import APIRouter, HTTPException
from app.config.database import database
from pydantic import BaseModel

router = APIRouter()

class StudentIn(BaseModel):
    full_name: str
    email: str
    department: str
    cgpa: float
    resume_link: str | None = None

class StudentUpdate(BaseModel):
    full_name: str
    department: str
    cgpa: float
    resume_link: str | None = None

@router.get("/")
async def get_all_students():
    query = "SELECT * FROM Students"
    return await database.fetch_all(query=query)

@router.get("/{student_id}")
async def get_student(student_id: int):
    query = "SELECT * FROM Students WHERE student_id = :student_id"
    return await database.fetch_one(query=query, values={"student_id": student_id})

@router.post("/")
async def add_student(student: StudentIn):
    query = """
        INSERT INTO Students (full_name, email, department, cgpa, resume_link)
        VALUES (:full_name, :email, :department, :cgpa, :resume_link)
    """
    try:
        last_record_id = await database.execute(query=query, values=student.model_dump())
        return {"message": "Student added successfully!", "student_id": last_record_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{student_id}")
async def update_student(student_id: int, student: StudentUpdate):
    query = """
        UPDATE Students 
        SET full_name = :full_name, department = :department, cgpa = :cgpa, resume_link = :resume_link
        WHERE student_id = :student_id
    """
    try:
        await database.execute(query=query, values={"student_id": student_id, **student.model_dump()})
        return {"message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))