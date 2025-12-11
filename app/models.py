from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Input Models
class OrgCreate(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrgUpdate(BaseModel):
    organization_name: str
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

# Response Models
class OrgResponse(BaseModel):
    organization_name: str
    collection_name: str
    admin_email: str

class Token(BaseModel):
    access_token: str
    token_type: str
    org_name: str