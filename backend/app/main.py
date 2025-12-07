from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db import init_db
from app.api import (
    upload,
    classrooms,
    solver,
    projects,
    teachers,
    courses,
    student_groups,
    terms,
    timeslots,
    lessons,
)
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan, title="University Semester Scheduler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(projects.router, prefix="/api", tags=["Projects"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(classrooms.router, prefix="/api", tags=["Classrooms"])
app.include_router(teachers.router, prefix="/api", tags=["Teachers"])
app.include_router(courses.router, prefix="/api", tags=["Courses"])
app.include_router(student_groups.router, prefix="/api", tags=["Student Groups"])
app.include_router(terms.router, prefix="/api", tags=["Terms"])
app.include_router(timeslots.router, prefix="/api", tags=["TimeSlots"])
app.include_router(lessons.router, prefix="/api", tags=["Lessons"])
app.include_router(solver.router, prefix="/api", tags=["Solver"])


@app.get("/")
async def root():
    return {"message": "University Semester Scheduler API is running"}
