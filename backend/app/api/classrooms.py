from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.db import get_session
from app.models import Classroom

router = APIRouter()


@router.get("/classrooms", response_model=List[Classroom])
async def get_classrooms(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Classroom))
    return result.scalars().all()


@router.post("/classrooms", response_model=Classroom)
async def create_classroom(
    classroom: Classroom, session: AsyncSession = Depends(get_session)
):
    session.add(classroom)
    await session.commit()
    await session.refresh(classroom)
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
