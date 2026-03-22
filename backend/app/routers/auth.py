import hashlib
from fastapi import APIRouter, HTTPException
from app.config.database import database
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Educational note: We use hashlib here to prevent Windows installation errors. 
# In production apps, always use a library like 'passlib' with 'bcrypt'.
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# Data Models
class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register_user(user: RegisterRequest):
    # 1. Check if the email is already in use
    check_query = "SELECT * FROM Users WHERE email = :email"
    existing_user = await database.fetch_one(query=check_query, values={"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered!")

    hashed_pw = hash_password(user.password)
    student_id = None

    # 2. If student, create a blank student profile using only the original base columns
    if user.role == "Student":
        student_query = """
            INSERT INTO Students (full_name, email, department)
            VALUES (:full_name, :email, 'Please Update Profile')
        """
        try:
            student_id = await database.execute(query=student_query, values={
                "full_name": user.full_name,
                "email": user.email
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create student profile: {str(e)}")

    # 3. Create the User account and link it
    user_query = """
        INSERT INTO Users (email, password, role, student_id)
        VALUES (:email, :password, :role, :student_id)
    """
    try:
        await database.execute(query=user_query, values={
            "email": user.email,
            "password": hashed_pw,
            "role": user.role,
            "student_id": student_id
        })
        return {"message": "Account created successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user account: {str(e)}")



@router.post("/login")
async def login_user(user: LoginRequest):
    hashed_pw = hash_password(user.password)
    
    # Check if the user exists with that email AND password
    query = "SELECT user_id, email, role, student_id FROM Users WHERE email = :email AND password = :password"
    db_user = await database.fetch_one(query=query, values={
        "email": user.email, 
        "password": hashed_pw
    })
    
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    # Return the user data so the frontend knows where to redirect them!
    return dict(db_user)