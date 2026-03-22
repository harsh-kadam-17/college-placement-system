from fastapi import APIRouter, HTTPException
from app.config.database import database
from pydantic import BaseModel
from datetime import date

router = APIRouter()


class CompanyIn(BaseModel):
    company_name: str
    job_role: str
    package_min: float
    package_max: float
    min_cgpa: float
    visit_date: date


@router.delete("/{company_id}")
async def delete_company(company_id: int):
    existing = await database.fetch_one(
        "SELECT company_id FROM Companies WHERE company_id = :id", {"id": company_id}
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Company not found.")
    await database.execute("DELETE FROM Companies WHERE company_id = :id", {"id": company_id})
    return {"message": "Company deleted successfully."}


@router.get("/")
async def get_all_companies():
    query = "SELECT * FROM Companies"
    return await database.fetch_all(query=query)


@router.post("/")
async def add_company(company: CompanyIn):
    # Validate package range
    if company.package_max < company.package_min:
        raise HTTPException(status_code=400, detail="Maximum package cannot be less than minimum package.")

    # Case-insensitive duplicate check
    dup = await database.fetch_one(
        "SELECT company_id FROM Companies WHERE LOWER(company_name) = LOWER(:name) AND LOWER(job_role) = LOWER(:role)",
        {"name": company.company_name, "role": company.job_role}
    )
    if dup:
        raise HTTPException(
            status_code=400,
            detail=f"'{company.company_name}' already has a listing for '{company.job_role}'. A company can only post one listing per role."
        )

    query = """
        INSERT INTO Companies (company_name, job_role, package_min, package_max, min_cgpa, visit_date)
        VALUES (:company_name, :job_role, :package_min, :package_max, :min_cgpa, :visit_date)
    """
    try:
        last_record_id = await database.execute(query=query, values=company.model_dump())
        return {"message": "Company added successfully!", "company_id": last_record_id}
    except Exception as e:
        # Handle duplicate company+role constraint
        if "Duplicate entry" in str(e):
            raise HTTPException(
                status_code=400,
                detail=f"'{company.company_name}' has already been listed for the role '{company.job_role}'. A company can only post one listing per role."
            )
        raise HTTPException(status_code=500, detail=str(e))