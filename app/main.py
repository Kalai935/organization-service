from fastapi import FastAPI
from app.database import db
from app.routers import organization, auth

app = FastAPI(title="Org Management Service")

@app.on_event("startup")
async def startup():
    db.connect()

@app.on_event("shutdown")
async def shutdown():
    db.close()

app.include_router(auth.router)
app.include_router(organization.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)