from datetime import datetime
from fastapi import HTTPException
from app.database import db
from app.security import get_password_hash
from app.models import OrgCreate, OrgUpdate
from app.config import settings 

class OrgService:
    def __init__(self):
        self.master_db = db.get_master_db()
        self.client = db.get_client()

    async def create_organization(self, data: OrgCreate):
        org_coll = self.master_db["organizations"]
        admin_coll = self.master_db["admins"]

        # 1. Validate Org Name
        if await org_coll.find_one({"organization_name": data.organization_name}):
            raise HTTPException(status_code=400, detail="Organization already exists")

        # 2. Dynamic Collection Creation
        dynamic_coll_name = f"org_{data.organization_name}"
        
        # 3. Create Admin User
        hashed_pwd = get_password_hash(data.password)
        admin_doc = {
            "email": data.email,
            "password": hashed_pwd,
            "organization_name": data.organization_name,
            "role": "admin"
        }
        await admin_coll.insert_one(admin_doc)

        # 4. Store Metadata
        # Fixed: Use Python datetime instead of complicated DB call
        org_metadata = {
            "organization_name": data.organization_name,
            "collection_name": dynamic_coll_name,
            "created_at": datetime.utcnow().isoformat() 
        }
        await org_coll.insert_one(org_metadata)

        # Initialize the dynamic collection
        dynamic_db = self.client[settings.DB_NAME] 
        await dynamic_db[dynamic_coll_name].insert_one({
            "info": "Collection Initialized", 
            "created_at": org_metadata["created_at"]
        })

        return {
            "organization_name": data.organization_name,
            "collection_name": dynamic_coll_name,
            "admin_email": data.email
        }

    async def get_organization(self, name: str):
        org = await self.master_db["organizations"].find_one({"organization_name": name})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        admin = await self.master_db["admins"].find_one({"organization_name": name})
        return {
            "organization_name": org["organization_name"],
            "collection_name": org["collection_name"],
            "admin_email": admin["email"] if admin else "Unknown"
        }

    async def update_organization(self, data: OrgUpdate, current_org: str):
        org_coll = self.master_db["organizations"]
        admin_coll = self.master_db["admins"]
        
        existing_org = await org_coll.find_one({"organization_name": current_org})
        
        if not existing_org:
             raise HTTPException(status_code=404, detail="Organization not found")

        # If renaming organization
        if data.organization_name != current_org:
            if await org_coll.find_one({"organization_name": data.organization_name}):
                raise HTTPException(status_code=400, detail="New organization name already exists")
            
            old_coll_name = existing_org["collection_name"]
            new_coll_name = f"org_{data.organization_name}"
            
            database = self.client[settings.DB_NAME]
            
            try:
                await database[old_coll_name].rename(new_coll_name)
            except Exception:
                pass

            await org_coll.update_one(
                {"organization_name": current_org},
                {"$set": {
                    "organization_name": data.organization_name,
                    "collection_name": new_coll_name
                }}
            )
            
            await admin_coll.update_one(
                {"organization_name": current_org},
                {"$set": {"organization_name": data.organization_name}}
            )

        update_fields = {}
        if data.email: update_fields["email"] = data.email
        if data.password: update_fields["password"] = get_password_hash(data.password)
        
        if update_fields:
            target_org = data.organization_name 
            await admin_coll.update_one({"organization_name": target_org}, {"$set": update_fields})

        return {"status": "updated", "new_name": data.organization_name}

    async def delete_organization(self, org_name: str):
        org_coll = self.master_db["organizations"]
        admin_coll = self.master_db["admins"]

        org = await org_coll.find_one({"organization_name": org_name})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        coll_name = org["collection_name"]
        await self.client[settings.DB_NAME].drop_collection(coll_name)

        await org_coll.delete_one({"organization_name": org_name})
        await admin_coll.delete_many({"organization_name": org_name})

        return {"status": "Organization and data deleted"}