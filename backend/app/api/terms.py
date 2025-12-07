from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session
from app.models import EntranceTerm, SemesterType

router = APIRouter()


@router.get("/terms/", response_model=List[EntranceTerm])
async def get_terms(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(EntranceTerm).order_by(EntranceTerm.id.desc())
    )
    return result.scalars().all()


@router.post("/terms/", response_model=EntranceTerm)
async def create_term(term: EntranceTerm, session: AsyncSession = Depends(get_session)):
    # Check if term exists
    existing = await session.get(EntranceTerm, term.id)
    if existing:
        raise HTTPException(status_code=400, detail="Term already exists")

    session.add(term)
    await session.commit()
    await session.refresh(term)
    return term
