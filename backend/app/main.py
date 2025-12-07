from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db import init_db
from app.api import upload, classrooms, solver


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan, title="University Semester Scheduler API")

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(classrooms.router, prefix="/api", tags=["Classrooms"])
app.include_router(solver.router, prefix="/api", tags=["Solver"])


@app.get("/")
async def root():
    return {"message": "University Semester Scheduler API is running"}
