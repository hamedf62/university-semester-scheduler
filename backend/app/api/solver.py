from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_session, engine as db_engine
from sqlalchemy.orm import sessionmaker
from app.models import (
    Lesson,
    Classroom,
    TimeSlot,
    Course,
    Teacher,
    StudentGroup,
    TeacherCourseLink,
    TeacherEntranceLink,
    ScheduleResult,
)
from app.solver.engine import SolverEngine
import uuid
import asyncio

router = APIRouter()


async def run_solver_task(run_id: str, weights: dict):
    # Create a new session for the background task
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print(f"Starting solver run {run_id}...")

        # Fetch Data
        lessons = (await session.execute(select(Lesson))).scalars().all()
        classrooms = (await session.execute(select(Classroom))).scalars().all()
        timeslots = (await session.execute(select(TimeSlot))).scalars().all()
        courses = (await session.execute(select(Course))).scalars().all()
        teachers = (await session.execute(select(Teacher))).scalars().all()
        groups = (await session.execute(select(StudentGroup))).scalars().all()
        t_c_links = (await session.execute(select(TeacherCourseLink))).scalars().all()
        t_e_links = (await session.execute(select(TeacherEntranceLink))).scalars().all()

        if not lessons or not classrooms or not timeslots:
            print("Missing data to run solver.")
            return

        solver = SolverEngine(
            lessons=lessons,
            classrooms=classrooms,
            timeslots=timeslots,
            courses=courses,
            teachers=teachers,
            groups=groups,
            teacher_course_links=t_c_links,
            teacher_entrance_links=t_e_links,
            weights=weights,
        )

        # Run Solver
        # Note: SolverEngine.run is async but CPU bound.
        # In production, run in a separate process/worker (Celery).
        # Here we await it, which might block the event loop if not careful.
        # But since we are in a background task, it's okay for now.
        results = await solver.run(generations=100)  # Reduced generations for demo

        if results:
            print(f"Solver finished. Saving {len(results)} assignments.")
            for res in results:
                schedule_entry = ScheduleResult(
                    run_id=run_id,
                    lesson_id=res["lesson_id"],
                    room_id=res["room_id"],
                    timeslot_id=res["timeslot_id"],
                )
                session.add(schedule_entry)
            await session.commit()
        else:
            print("Solver failed to find a valid schedule.")


@router.post("/solve")
async def start_solver(weights: dict, background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())
    background_tasks.add_task(run_solver_task, run_id, weights)
    return {"run_id": run_id, "status": "started"}


@router.get("/results/{run_id}")
async def get_results(run_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(ScheduleResult).where(ScheduleResult.run_id == run_id)
    )
    return result.scalars().all()
