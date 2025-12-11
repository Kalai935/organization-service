from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from app.models import OrgCreate, OrgUpdate, OrgResponse
from app.services import OrgService
from app.config import settings

router = APIRouter()
security = HTTPBearer() 

# Dependency to verify token and get current Org
async def get_current_org(token_auth=Depends(security)): 
    token = token_auth.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        org_name: str = payload.get("org")
        if org_name is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return org_name
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@router.post("/org/create", response_model=OrgResponse)
async def create_org(data: OrgCreate):
    service = OrgService()
    return await service.create_organization(data)

@router.get("/org/get")
async def get_org(organization_name: str):
    # Usually strictly secured, but keeping open as per spec for GET.
    service = OrgService()
    return await service.get_organization(organization_name)

@router.put("/org/update")
async def update_org(data: OrgUpdate, current_org: str = Depends(get_current_org)):
    service = OrgService()
    # current_org comes from JWT. 
    return await service.update_organization(data, current_org)

@router.delete("/org/delete")
async def delete_org(organization_name: str, current_org: str = Depends(get_current_org)):
    # Validate user only deletes their own org
    if organization_name != current_org:
        raise HTTPException(status_code=403, detail="You can only delete your own organization")
    
    service = OrgService()
    return await service.delete_organization(organization_name)