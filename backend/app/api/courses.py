from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, func, col
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session
from app.models import Course, ClassroomType, ProjectCourseLink
from pydantic import BaseModel

router = APIRouter()


class CourseCreate(BaseModel):
    name: str
    required_room_type: ClassroomType
    units: int = 2
    min_population: Optional[int] = 20
    max_population: Optional[int] = 40
    project_id: Optional[int] = None


class PaginatedCourses(BaseModel):
    items: List[Course]
    total: int
    page: int
    size: int


@router.get("/courses/", response_model=PaginatedCourses)
async def get_courses(
    project_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    offset = (page - 1) * size

    if project_id:
        query = (
            select(Course)
            .join(ProjectCourseLink)
            .where(ProjectCourseLink.project_id == project_id)
        )
    else:
        query = select(Course)

    if search:
        query = query.where(col(Course.name).contains(search))

    # Count total
    count_stmt = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_stmt)
    total = total_result.scalar_one()

    # Fetch items
    stmt = query.offset(offset).limit(size)
    result = await session.execute(stmt)
    courses = result.scalars().all()

    return PaginatedCourses(items=courses, total=total, page=page, size=size)


@router.post("/courses/", response_model=Course)
async def create_course(
    course_in: CourseCreate, session: AsyncSession = Depends(get_session)
):
    course = Course(
        name=course_in.name,
        required_room_type=course_in.required_room_type,
        units=course_in.units,
        min_population=course_in.min_population,
        max_population=course_in.max_population,
    )
    session.add(course)
    await session.commit()
    await session.refresh(course)

    if course_in.project_id:
        link = ProjectCourseLink(project_id=course_in.project_id, course_id=course.id)
        session.add(link)
        await session.commit()

    return course


@router.put("/courses/{course_id}", response_model=Course)
async def update_course(
    course_id: int,
    course_data: CourseCreate,
    session: AsyncSession = Depends(get_session),
):
    course = await session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course_data_dict = course_data.dict(exclude_unset=True, exclude={"project_id"})
    for key, value in course_data_dict.items():
        setattr(course, key, value)

    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


@router.delete("/courses/{course_id}")
async def delete_course(course_id: int, session: AsyncSession = Depends(get_session)):
    course = await session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    await session.delete(course)
    await session.commit()
    return {"ok": True}


@router.post("/courses/{course_id}/link")
async def link_course_to_project(
    course_id: int, project_id: int, session: AsyncSession = Depends(get_session)
):
    stmt = select(ProjectCourseLink).where(
        ProjectCourseLink.project_id == project_id,
        ProjectCourseLink.course_id == course_id,
    )
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        return {"ok": True, "message": "Already linked"}

    link = ProjectCourseLink(project_id=project_id, course_id=course_id)
    session.add(link)
    await session.commit()
    return {"ok": True}
