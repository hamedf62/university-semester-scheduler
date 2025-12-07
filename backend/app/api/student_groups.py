from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, func, col
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db import get_session
from app.models import (
    StudentGroup,
    StudentGroupCourseLink,
    Degree,
    ProjectStudentGroupLink,
)
from pydantic import BaseModel

router = APIRouter()


class StudentGroupRead(BaseModel):
    id: int
    name: str
    degree: Degree
    population: int
    allowed_days: Optional[str] = None
    course_ids: List[int] = []
    created_at: datetime
    updated_at: datetime


class PaginatedStudentGroups(BaseModel):
    items: List[StudentGroupRead]
    total: int
    page: int
    size: int


class StudentGroupCreate(BaseModel):
    name: str
    degree: Degree
    population: int
    allowed_days: Optional[str] = None
    course_ids: List[int] = []
    project_id: Optional[int] = None


class StudentGroupUpdate(BaseModel):
    name: Optional[str] = None
    degree: Optional[Degree] = None
    population: Optional[int] = None
    allowed_days: Optional[str] = None
    course_ids: Optional[List[int]] = None


@router.get("/student_groups/", response_model=PaginatedStudentGroups)
async def get_student_groups(
    project_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    offset = (page - 1) * size

    if project_id:
        query = (
            select(StudentGroup)
            .join(ProjectStudentGroupLink)
            .where(ProjectStudentGroupLink.project_id == project_id)
        )
    else:
        query = select(StudentGroup)

    if search:
        query = query.where(col(StudentGroup.name).contains(search))

    # Count total
    count_stmt = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_stmt)
    total = total_result.scalar_one()

    # Fetch items
    stmt = (
        query.options(selectinload(StudentGroup.course_links))
        .offset(offset)
        .limit(size)
    )

    result = await session.execute(stmt)
    groups = result.scalars().all()

    output = []
    for g in groups:
        c_ids = [link.course_id for link in g.course_links]
        output.append(
            StudentGroupRead(
                id=g.id,
                name=g.name,
                degree=g.degree,
                population=g.population,
                allowed_days=g.allowed_days,
                course_ids=c_ids,
                created_at=g.created_at,
                updated_at=g.updated_at,
            )
        )

    return PaginatedStudentGroups(items=output, total=total, page=page, size=size)


@router.post("/student_groups/", response_model=StudentGroupRead)
async def create_student_group(
    group_in: StudentGroupCreate, session: AsyncSession = Depends(get_session)
):
    group = StudentGroup(
        name=group_in.name,
        degree=group_in.degree,
        population=group_in.population,
        allowed_days=group_in.allowed_days,
    )
    session.add(group)
    await session.commit()
    await session.refresh(group)

    if group_in.course_ids:
        for c_id in group_in.course_ids:
            link = StudentGroupCourseLink(group_id=group.id, course_id=c_id)
            session.add(link)

    if group_in.project_id:
        link = ProjectStudentGroupLink(
            project_id=group_in.project_id, group_id=group.id
        )
        session.add(link)

    await session.commit()

    # Reload
    stmt = (
        select(StudentGroup)
        .where(StudentGroup.id == group.id)
        .options(selectinload(StudentGroup.course_links))
    )
    group = (await session.execute(stmt)).scalar_one()

    c_ids = [link.course_id for link in group.course_links]
    return StudentGroupRead(
        id=group.id,
        name=group.name,
        degree=group.degree,
        population=group.population,
        allowed_days=group.allowed_days,
        course_ids=c_ids,
    )


@router.put("/student_groups/{group_id}", response_model=StudentGroupRead)
async def update_student_group(
    group_id: int,
    group_in: StudentGroupUpdate,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(StudentGroup)
        .where(StudentGroup.id == group_id)
        .options(selectinload(StudentGroup.course_links))
    )
    group = (await session.execute(stmt)).scalar_one_or_none()

    if not group:
        raise HTTPException(status_code=404, detail="StudentGroup not found")

    if group_in.name is not None:
        group.name = group_in.name
    if group_in.degree is not None:
        group.degree = group_in.degree
    if group_in.population is not None:
        group.population = group_in.population
    if group_in.allowed_days is not None:
        group.allowed_days = group_in.allowed_days

    if group_in.course_ids is not None:
        # Clear existing
        for link in group.course_links:
            await session.delete(link)

        # Add new
        for c_id in group_in.course_ids:
            link = StudentGroupCourseLink(group_id=group.id, course_id=c_id)
            session.add(link)

    session.add(group)
    await session.commit()

    # Reload
    stmt = (
        select(StudentGroup)
        .where(StudentGroup.id == group_id)
        .options(selectinload(StudentGroup.course_links))
    )
    group = (await session.execute(stmt)).scalar_one()

    c_ids = [link.course_id for link in group.course_links]
    return StudentGroupRead(
        id=group.id,
        name=group.name,
        degree=group.degree,
        population=group.population,
        allowed_days=group.allowed_days,
        course_ids=c_ids,
    )


@router.delete("/student_groups/{group_id}")
async def delete_student_group(
    group_id: int, session: AsyncSession = Depends(get_session)
):
    group = await session.get(StudentGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="StudentGroup not found")
    await session.delete(group)
    await session.commit()
    return {"ok": True}


@router.post("/student_groups/{group_id}/link")
async def link_group_to_project(
    group_id: int, project_id: int, session: AsyncSession = Depends(get_session)
):
    stmt = select(ProjectStudentGroupLink).where(
        ProjectStudentGroupLink.project_id == project_id,
        ProjectStudentGroupLink.group_id == group_id,
    )
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        return {"ok": True, "message": "Already linked"}

    link = ProjectStudentGroupLink(project_id=project_id, group_id=group_id)
    session.add(link)
    await session.commit()
    return {"ok": True}
