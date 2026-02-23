from fastapi import APIRouter, HTTPException
from app.config.database import database
from pydantic import BaseModel
from datetime import date

router = APIRouter()

# Data Validation Model for Companies
class CompanyIn(BaseModel):
    company_name: str
    job_role: str
    package_lpa: float
    visit_date: date

# GET: Fetch all companies
@router.get("/")
async def get_all_companies():
    query = "SELECT * FROM Companies"
    return await database.fetch_all(query=query)

# POST: Add a new company
@router.post("/")
async def add_company(company: CompanyIn):
    query = """
        INSERT INTO Companies (company_name, job_role, package_lpa, visit_date)
        VALUES (:company_name, :job_role, :package_lpa, :visit_date)
    """
    try:
        last_record_id = await database.execute(query=query, values=company.model_dump())
        return {"message": "Company added successfully!", "company_id": last_record_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))