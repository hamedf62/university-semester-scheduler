from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlmodel import col
from app.db import get_session
from app.models import Classroom, ClassroomType, ProjectClassroomLink
from pydantic import BaseModel

router = APIRouter()


class ClassroomCreate(BaseModel):
    name: str
    faculty: str
    capacity: int
    type: ClassroomType
    project_id: Optional[int] = None


class PaginatedClassrooms(BaseModel):
    items: List[Classroom]
    total: int
    page: int
    size: int


@router.get("/classrooms", response_model=PaginatedClassrooms)
async def get_classrooms(
    project_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    offset = (page - 1) * size

    if project_id:
        query = (
            select(Classroom)
            .join(ProjectClassroomLink)
            .where(ProjectClassroomLink.project_id == project_id)
        )
    else:
        query = select(Classroom)

    if search:
        query = query.where(col(Classroom.name).contains(search))

    # Count total
    count_stmt = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_stmt)
    total = total_result.scalar_one()

    # Fetch items
    stmt = query.offset(offset).limit(size)
    result = await session.execute(stmt)
    classrooms = result.scalars().all()

    return PaginatedClassrooms(items=classrooms, total=total, page=page, size=size)


@router.post("/classrooms", response_model=Classroom)
async def create_classroom(
    classroom_in: ClassroomCreate, session: AsyncSession = Depends(get_session)
):
    classroom = Classroom(
        name=classroom_in.name,
        faculty=classroom_in.faculty,
        capacity=classroom_in.capacity,
        type=classroom_in.type,
    )
    session.add(classroom)
    await session.commit()
    await session.refresh(classroom)

    if classroom_in.project_id:
        link = ProjectClassroomLink(
            project_id=classroom_in.project_id, classroom_id=classroom.id
        )
        session.add(link)
        await session.commit()

    return classroom


@router.delete("/classrooms/{classroom_id}")
async def delete_classroom(
    classroom_id: int, session: AsyncSession = Depends(get_session)
):
    classroom = await session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    await session.delete(classroom)
    await session.commit()
    return {"ok": True}


@router.put("/classrooms/{classroom_id}", response_model=Classroom)
async def update_classroom(
    classroom_id: int,
    classroom_data: ClassroomCreate,
    session: AsyncSession = Depends(get_session),
):
    classroom = await session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    classroom_data_dict = classroom_data.dict(
        exclude_unset=True, exclude={"project_id"}
    )
    for key, value in classroom_data_dict.items():
        setattr(classroom, key, value)

    session.add(classroom)
    await session.commit()
    await session.refresh(classroom)
    return classroom


@router.post("/classrooms/{classroom_id}/link")
async def link_classroom_to_project(
    classroom_id: int, project_id: int, session: AsyncSession = Depends(get_session)
):
    stmt = select(ProjectClassroomLink).where(
        ProjectClassroomLink.project_id == project_id,
        ProjectClassroomLink.classroom_id == classroom_id,
    )
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        return {"ok": True, "message": "Already linked"}

    link = ProjectClassroomLink(project_id=project_id, classroom_id=classroom_id)
    session.add(link)
    await session.commit()
    return {"ok": True}
