from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, func, col
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db import get_session
from app.models import (
    Teacher,
    TeacherAvailability,
    ProjectTeacherLink,
    TeacherCourseLink,
)
from pydantic import BaseModel

router = APIRouter()


class TeacherRead(BaseModel):
    id: int
    name: str
    available_slots: List[int] = []
    course_ids: List[int] = []
    created_at: datetime
    updated_at: datetime


class PaginatedTeachers(BaseModel):
    items: List[TeacherRead]
    total: int
    page: int
    size: int


class TeacherCreate(BaseModel):
    name: str
    available_slots: List[int] = []
    course_ids: List[int] = []
    project_id: Optional[int] = None


class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    available_slots: Optional[List[int]] = None
    course_ids: Optional[List[int]] = None
    project_id: Optional[int] = None


@router.get("/teachers/", response_model=PaginatedTeachers)
async def get_teachers(
    project_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    offset = (page - 1) * size

    if project_id:
        # Fetch teachers linked to project
        query = (
            select(Teacher)
            .join(ProjectTeacherLink)
            .where(ProjectTeacherLink.project_id == project_id)
        )
    else:
        query = select(Teacher)

    if search:
        query = query.where(col(Teacher.name).contains(search))

    # Count total
    count_stmt = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_stmt)
    total = total_result.scalar_one()

    # Fetch items
    stmt = (
        query.options(
            selectinload(Teacher.availability_links),
            selectinload(Teacher.course_links),
        )
        .offset(offset)
        .limit(size)
    )

    result = await session.execute(stmt)
    teachers = result.scalars().all()

    output = []
    for t in teachers:
        if project_id:
            slots = [
                link.timeslot_id
                for link in t.availability_links
                if link.project_id == project_id
            ]
        else:
            slots = []  # Global view doesn't show project-specific availability

        c_ids = [link.course_id for link in t.course_links]
        output.append(
            TeacherRead(
                id=t.id,
                name=t.name,
                available_slots=slots,
                course_ids=c_ids,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
        )

    return PaginatedTeachers(items=output, total=total, page=page, size=size)


@router.post("/teachers/", response_model=TeacherRead)
async def create_teacher(
    teacher_in: TeacherCreate, session: AsyncSession = Depends(get_session)
):
    teacher = Teacher(name=teacher_in.name)
    session.add(teacher)
    await session.commit()
    await session.refresh(teacher)

    if teacher_in.available_slots and teacher_in.project_id:
        for ts_id in teacher_in.available_slots:
            link = TeacherAvailability(
                teacher_id=teacher.id,
                timeslot_id=ts_id,
                project_id=teacher_in.project_id,
            )
            session.add(link)

    if teacher_in.course_ids:
        for c_id in teacher_in.course_ids:
            link = TeacherCourseLink(teacher_id=teacher.id, course_id=c_id)
            session.add(link)

    if teacher_in.project_id:
        link = ProjectTeacherLink(
            project_id=teacher_in.project_id, teacher_id=teacher.id
        )
        session.add(link)

    await session.commit()

    # Reload with links
    stmt = (
        select(Teacher)
        .where(Teacher.id == teacher.id)
        .options(
            selectinload(Teacher.availability_links), selectinload(Teacher.course_links)
        )
    )
    teacher = (await session.execute(stmt)).scalar_one()

    if teacher_in.project_id:
        slots = [
            link.timeslot_id
            for link in teacher.availability_links
            if link.project_id == teacher_in.project_id
        ]
    else:
        slots = []

    c_ids = [link.course_id for link in teacher.course_links]
    return TeacherRead(
        id=teacher.id, name=teacher.name, available_slots=slots, course_ids=c_ids
    )


@router.put("/teachers/{teacher_id}", response_model=TeacherRead)
async def update_teacher(
    teacher_id: int,
    teacher_in: TeacherUpdate,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Teacher)
        .where(Teacher.id == teacher_id)
        .options(
            selectinload(Teacher.availability_links), selectinload(Teacher.course_links)
        )
    )
    teacher = (await session.execute(stmt)).scalar_one_or_none()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if teacher_in.name is not None:
        teacher.name = teacher_in.name

    if teacher_in.available_slots is not None and teacher_in.project_id:
        # Clear existing for THIS project
        # Note: modifying the list in place while iterating is dangerous, so we collect to delete first
        to_delete = [
            link
            for link in teacher.availability_links
            if link.project_id == teacher_in.project_id
        ]
        for link in to_delete:
            await session.delete(link)

        # Add new
        for ts_id in teacher_in.available_slots:
            link = TeacherAvailability(
                teacher_id=teacher.id,
                timeslot_id=ts_id,
                project_id=teacher_in.project_id,
            )
            session.add(link)

    if teacher_in.course_ids is not None:
        # Clear existing
        for link in teacher.course_links:
            await session.delete(link)

        # Add new
        for c_id in teacher_in.course_ids:
            link = TeacherCourseLink(teacher_id=teacher.id, course_id=c_id)
            session.add(link)

    session.add(teacher)
    await session.commit()

    # Reload
    stmt = (
        select(Teacher)
        .where(Teacher.id == teacher_id)
        .options(
            selectinload(Teacher.availability_links), selectinload(Teacher.course_links)
        )
    )
    teacher = (await session.execute(stmt)).scalar_one()

    if teacher_in.project_id:
        slots = [
            link.timeslot_id
            for link in teacher.availability_links
            if link.project_id == teacher_in.project_id
        ]
    else:
        slots = []

    c_ids = [link.course_id for link in teacher.course_links]
    return TeacherRead(
        id=teacher.id, name=teacher.name, available_slots=slots, course_ids=c_ids
    )


@router.get("/teachers/", response_model=List[TeacherRead])
async def get_teachers(
    project_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    if project_id:
        # Fetch teachers linked to project
        stmt = (
            select(Teacher)
            .join(ProjectTeacherLink)
            .where(ProjectTeacherLink.project_id == project_id)
            .options(
                selectinload(Teacher.availability_links),
                selectinload(Teacher.course_links),
            )
        )
    else:
        stmt = select(Teacher).options(
            selectinload(Teacher.availability_links), selectinload(Teacher.course_links)
        )

    result = await session.execute(stmt)
    teachers = result.scalars().all()

    output = []
    for t in teachers:
        slots = [link.timeslot_id for link in t.availability_links]
        c_ids = [link.course_id for link in t.course_links]
        output.append(
            TeacherRead(id=t.id, name=t.name, available_slots=slots, course_ids=c_ids)
        )
    return output


@router.post("/teachers/", response_model=TeacherRead)
async def create_teacher(
    teacher_in: TeacherCreate, session: AsyncSession = Depends(get_session)
):
    teacher = Teacher(name=teacher_in.name)
    session.add(teacher)
    await session.commit()
    await session.refresh(teacher)

    if teacher_in.available_slots:
        for ts_id in teacher_in.available_slots:
            link = TeacherAvailability(teacher_id=teacher.id, timeslot_id=ts_id)
            session.add(link)

    if teacher_in.course_ids:
        for c_id in teacher_in.course_ids:
            link = TeacherCourseLink(teacher_id=teacher.id, course_id=c_id)
            session.add(link)

    if teacher_in.project_id:
        link = ProjectTeacherLink(
            project_id=teacher_in.project_id, teacher_id=teacher.id
        )
        session.add(link)

    await session.commit()

    # Reload with links
    stmt = (
        select(Teacher)
        .where(Teacher.id == teacher.id)
        .options(
            selectinload(Teacher.availability_links), selectinload(Teacher.course_links)
        )
    )
    teacher = (await session.execute(stmt)).scalar_one()

    slots = [link.timeslot_id for link in teacher.availability_links]
    c_ids = [link.course_id for link in teacher.course_links]
    return TeacherRead(
        id=teacher.id, name=teacher.name, available_slots=slots, course_ids=c_ids
    )


@router.put("/teachers/{teacher_id}", response_model=TeacherRead)
async def update_teacher(
    teacher_id: int,
    teacher_in: TeacherUpdate,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Teacher)
        .where(Teacher.id == teacher_id)
        .options(
            selectinload(Teacher.availability_links), selectinload(Teacher.course_links)
        )
    )
    teacher = (await session.execute(stmt)).scalar_one_or_none()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if teacher_in.name is not None:
        teacher.name = teacher_in.name

    if teacher_in.available_slots is not None:
        # Clear existing
        for link in teacher.availability_links:
            await session.delete(link)

        # Add new
        for ts_id in teacher_in.available_slots:
            link = TeacherAvailability(teacher_id=teacher.id, timeslot_id=ts_id)
            session.add(link)

    if teacher_in.course_ids is not None:
        # Clear existing
        for link in teacher.course_links:
            await session.delete(link)

        # Add new
        for c_id in teacher_in.course_ids:
            link = TeacherCourseLink(teacher_id=teacher.id, course_id=c_id)
            session.add(link)

    session.add(teacher)
    await session.commit()

    # Reload
    stmt = (
        select(Teacher)
        .where(Teacher.id == teacher_id)
        .options(
            selectinload(Teacher.availability_links), selectinload(Teacher.course_links)
        )
    )
    teacher = (await session.execute(stmt)).scalar_one()

    slots = [link.timeslot_id for link in teacher.availability_links]
    c_ids = [link.course_id for link in teacher.course_links]
    return TeacherRead(
        id=teacher.id, name=teacher.name, available_slots=slots, course_ids=c_ids
    )


@router.delete("/teachers/{teacher_id}")
async def delete_teacher(teacher_id: int, session: AsyncSession = Depends(get_session)):
    teacher = await session.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    await session.delete(teacher)
    await session.commit()
    return {"ok": True}


@router.post("/teachers/{teacher_id}/link")
async def link_teacher_to_project(
    teacher_id: int, project_id: int, session: AsyncSession = Depends(get_session)
):
    # Check if link exists
    stmt = select(ProjectTeacherLink).where(
        ProjectTeacherLink.project_id == project_id,
        ProjectTeacherLink.teacher_id == teacher_id,
    )
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        return {"ok": True, "message": "Already linked"}

    link = ProjectTeacherLink(project_id=project_id, teacher_id=teacher_id)
    session.add(link)
    await session.commit()
    return {"ok": True}


@router.post("/teachers/{teacher_id}/courses/{course_id}")
async def add_teacher_course_link(
    teacher_id: int, course_id: int, session: AsyncSession = Depends(get_session)
):
    link = TeacherCourseLink(teacher_id=teacher_id, course_id=course_id)
    session.add(link)
    try:
        await session.commit()
    except:
        await session.rollback()
        # Ignore duplicate
        pass
    return {"ok": True}


@router.delete("/teachers/{teacher_id}/courses/{course_id}")
async def remove_teacher_course_link(
    teacher_id: int, course_id: int, session: AsyncSession = Depends(get_session)
):
    link = await session.get(TeacherCourseLink, (teacher_id, course_id))
    if link:
        await session.delete(link)
        await session.commit()
    return {"ok": True}
