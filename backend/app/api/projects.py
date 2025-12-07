from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db import get_session
from app.models import (
    Project,
    ScheduleResult,
    Lesson,
    Course,
    Teacher,
    StudentGroup,
    Classroom,
    TimeSlot,
)
from sqlalchemy import desc
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.post("/projects/", response_model=Project)
async def create_project(
    project: Project, session: AsyncSession = Depends(get_session)
):
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.get("/projects/", response_model=List[Project])
async def read_projects(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Project))
    return result.scalars().all()


@router.get("/projects/{project_id}", response_model=Project)
async def read_project(project_id: int, session: AsyncSession = Depends(get_session)):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: int, project_data: Project, session: AsyncSession = Depends(get_session)
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_data_dict = project_data.dict(exclude_unset=True)
    for key, value in project_data_dict.items():
        setattr(project, key, value)

    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.get("/projects/{project_id}/results")
async def read_project_results(
    project_id: int, session: AsyncSession = Depends(get_session)
):
    # Find the latest run_id for this project
    stmt = (
        select(ScheduleResult.run_id)
        .join(Lesson)
        .where(Lesson.project_id == project_id)
        .order_by(desc(ScheduleResult.id))
        .limit(1)
    )
    result = await session.execute(stmt)
    latest_run_id = result.scalar_one_or_none()

    if not latest_run_id:
        return []

    # Fetch results for this run_id
    stmt = (
        select(ScheduleResult)
        .where(ScheduleResult.run_id == latest_run_id)
        .options(
            selectinload(ScheduleResult.lesson).selectinload(Lesson.course),
            selectinload(ScheduleResult.lesson).selectinload(Lesson.teacher),
            selectinload(ScheduleResult.lesson).selectinload(Lesson.group),
            selectinload(ScheduleResult.room),
            selectinload(ScheduleResult.timeslot),
        )
    )
    results = (await session.execute(stmt)).scalars().all()

    output = []
    # Map times to slots (0-based index)
    # Assuming standard slots: 08:00, 10:00, 12:00, 14:00, 16:00, 18:00, 20:00
    slot_map = {
        "08:00": 0,
        "10:00": 1,
        "12:00": 2,
        "14:00": 3,
        "16:00": 4,
        "18:00": 5,
        "20:00": 6,
    }

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
                "teacher_name": (
                    r.lesson.teacher.name
                    if r.lesson and r.lesson.teacher
                    else "Unknown"
                ),
                "group_name": (
                    r.lesson.group.name if r.lesson and r.lesson.group else "Unknown"
                ),
                "room_name": r.room.name if r.room else "Unknown",
                "day": r.timeslot.day_of_week if r.timeslot else 0,
                "slot": slot_idx,
                "run_id": r.run_id,
            }
        )
    return output
