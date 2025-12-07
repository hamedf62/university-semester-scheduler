from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db import get_session
from app.models import Lesson, Project
from pydantic import BaseModel

router = APIRouter()


class LessonRead(BaseModel):
    id: int
    course_name: str
    group_name: str
    teacher_name: Optional[str]
    duration_slots: int


@router.get("/lessons/", response_model=List[LessonRead])
async def get_lessons(
    project_id: int = Query(..., description="Project ID is required"),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Lesson)
        .where(Lesson.project_id == project_id)
        .options(
            selectinload(Lesson.course),
            selectinload(Lesson.group),
            selectinload(Lesson.teacher),
        )
    )
    result = await session.execute(stmt)
    lessons = result.scalars().all()

    output = []
    for l in lessons:
        output.append(
            LessonRead(
                id=l.id,
                course_name=l.course.name if l.course else "Unknown",
                group_name=l.group.name if l.group else "Unknown",
                teacher_name=l.teacher.name if l.teacher else None,
                duration_slots=l.duration_slots,
            )
        )
    return output
