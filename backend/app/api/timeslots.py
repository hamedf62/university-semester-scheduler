from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session
from app.models import TimeSlot

router = APIRouter()


@router.get("/timeslots/", response_model=List[TimeSlot])
async def get_timeslots(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(TimeSlot).order_by(TimeSlot.day_of_week, TimeSlot.start_time)
    )
    return result.scalars().all()
