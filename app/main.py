from fastapi import FastAPI
from app.database import db
from app.routers import organization, auth
from fastapi.responses import RedirectResponse

app = FastAPI(title="Org Management Service")

@app.on_event("startup")
async def startup():
    db.connect()

@app.on_event("shutdown")
async def shutdown():
    db.close()

@app.get("/")
async def read_root():
    return {"message": "Server is up and running!"}

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


app.include_router(auth.router)
app.include_router(organization.router)

