from fastapi import APIRouter, HTTPException, Depends
from app.models import AdminLogin, Token
from app.database import db
from app.security import verify_password, create_access_token
from app.config import settings

router = APIRouter()

@router.post("/admin/login", response_model=Token)
async def login(login_data: AdminLogin):
    admin = await db.get_master_db()["admins"].find_one({"email": login_data.email})
    
    if not admin or not verify_password(login_data.password, admin["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT
    access_token = create_access_token(
        data={"sub": admin["email"], "org": admin["organization_name"]}
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "org_name": admin["organization_name"]
    }