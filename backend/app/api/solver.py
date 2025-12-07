from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_session, engine as db_engine
from sqlalchemy.orm import sessionmaker, selectinload
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
    SolverRun,
    ProjectClassroomLink,
    ProjectTeacherLink,
    ProjectCourseLink,
    ProjectStudentGroupLink,
)
from app.solver.engine import SolverEngine
import uuid
import asyncio
import json
from datetime import datetime
from pydantic import BaseModel
from typing import List

router = APIRouter()


# Global state for progress tracking (simple in-memory for now)
solver_status = {}


class SolveRequest(BaseModel):
    project_id: int
    weights: dict
    max_stagnant_generations: int = 150


async def run_solver_task(
    run_id: str, project_id: int, weights: dict, max_stagnant_generations: int = 150
):
    solver_status[run_id] = {
        "status": "running",
        "progress": 0,
        "best_cost": float("inf"),
    }

    # Create a new session for the background task
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print(f"Starting solver run {run_id} for project {project_id}...")

        # Create SolverRun record
        solver_run = SolverRun(
            project_id=project_id,
            run_id=run_id,
            status="running",
            start_time=datetime.utcnow(),
            config_weights=json.dumps(weights),
        )
        session.add(solver_run)
        await session.commit()

        # Fetch Data
        lessons = (
            (
                await session.execute(
                    select(Lesson).where(Lesson.project_id == project_id)
                )
            )
            .scalars()
            .all()
        )

        classrooms = (
            (
                await session.execute(
                    select(Classroom)
                    .join(ProjectClassroomLink)
                    .where(ProjectClassroomLink.project_id == project_id)
                )
            )
            .scalars()
            .all()
        )

        timeslots = (await session.execute(select(TimeSlot))).scalars().all()

        courses = (
            (
                await session.execute(
                    select(Course)
                    .join(ProjectCourseLink)
                    .where(ProjectCourseLink.project_id == project_id)
                )
            )
            .scalars()
            .all()
        )

        # Load teachers with availability
        teachers = (
            (
                await session.execute(
                    select(Teacher)
                    .join(ProjectTeacherLink)
                    .where(ProjectTeacherLink.project_id == project_id)
                    .options(selectinload(Teacher.availability_links))
                )
            )
            .scalars()
            .all()
        )

        groups = (
            (
                await session.execute(
                    select(StudentGroup)
                    .join(ProjectStudentGroupLink)
                    .where(ProjectStudentGroupLink.project_id == project_id)
                )
            )
            .scalars()
            .all()
        )

        t_c_links = (await session.execute(select(TeacherCourseLink))).scalars().all()
        t_e_links = (await session.execute(select(TeacherEntranceLink))).scalars().all()

        if not lessons or not classrooms or not timeslots:
            print("Missing data to run solver.")
            solver_status[run_id]["status"] = "failed"
            solver_status[run_id]["error"] = "Missing data"

            solver_run.status = "failed"
            solver_run.end_time = datetime.utcnow()
            session.add(solver_run)
            await session.commit()
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

        # Callback to update progress
        def progress_callback(gen, best_cost):
            solver_status[run_id]["progress"] = gen
            solver_status[run_id]["best_cost"] = best_cost

        # Pass callback to solver (need to update SolverEngine to support this)
        results, best_cost = await solver.run(
            generations=1000, max_stagnant_generations=max_stagnant_generations
        )

        if results:
            print(f"Solver finished. Saving {len(results)} assignments...")
            for res in results:
                db_res = ScheduleResult(
                    run_id=run_id,
                    lesson_id=res["lesson_id"],
                    room_id=res["room_id"],
                    timeslot_id=res["timeslot_id"],
                    week_parity=res["week_parity"],
                    teacher_id=res["teacher_id"],
                )
                session.add(db_res)

            # Update SolverRun
            solver_run.status = "completed"
            solver_run.end_time = datetime.utcnow()
            solver_run.fitness_score = best_cost
            import math

            solver_run.satisfaction_percentage = min(
                100.0, 100.0 * math.exp(-best_cost / 50.0)
            )

            session.add(solver_run)
            await session.commit()
            print("Done!")
            solver_status[run_id]["status"] = "completed"
        else:
            print("No solution found.")
            solver_status[run_id]["status"] = "failed"

            solver_run.status = "failed"
            solver_run.end_time = datetime.utcnow()
            session.add(solver_run)
            await session.commit()


@router.get("/status/{run_id}")
async def get_status(run_id: str):
    return solver_status.get(run_id, {"status": "not_found"})


@router.post("/solve")
async def start_solver(request: SolveRequest, background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())
    background_tasks.add_task(
        run_solver_task,
        run_id,
        request.project_id,
        request.weights,
        request.max_stagnant_generations,
    )
    return {"run_id": run_id, "status": "started"}


@router.get("/results/{run_id}")
async def get_results(run_id: str, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(ScheduleResult)
        .where(ScheduleResult.run_id == run_id)
        .options(
            selectinload(ScheduleResult.lesson).selectinload(Lesson.course),
            selectinload(ScheduleResult.lesson).selectinload(Lesson.group),
            selectinload(ScheduleResult.room),
            selectinload(ScheduleResult.timeslot),
            selectinload(ScheduleResult.teacher),
        )
    )
    results = (await session.execute(stmt)).scalars().all()

    output = []
    slot_map = {"08:00": 0, "10:00": 1, "12:00": 2, "14:00": 3, "16:00": 4}

    for r in results:
        start_time = r.timeslot.start_time if r.timeslot else "08:00"
        slot_idx = slot_map.get(start_time, 0)

        output.append(
            {
                "id": r.id,
                "week_parity": r.week_parity,
                "course_name": (
                    r.lesson.course.name if r.lesson and r.lesson.course else "Unknown"
                ),
                "teacher_name": (r.teacher.name if r.teacher else "Unknown"),
                "group_name": (
                    r.lesson.group.name if r.lesson and r.lesson.group else "Unknown"
                ),
                "room_name": r.room.name if r.room else "Unknown",
                "day": r.timeslot.day_of_week if r.timeslot else 0,
                "slot": slot_idx,
            }
        )
    return output


@router.get("/projects/{project_id}/runs", response_model=List[SolverRun])
async def get_project_runs(
    project_id: int, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(SolverRun)
        .where(SolverRun.project_id == project_id)
        .order_by(SolverRun.start_time.desc())
    )
    return result.scalars().all()
