from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_session
from app.services.parser import ExcelParser
from app.models import (
    Teacher,
    Classroom,
    Course,
    StudentGroup,
    EntranceTerm,
    TeacherCourseLink,
    SemesterType,
    Lesson,
)

router = APIRouter()


@router.post("/upload/data")
async def upload_data(
    file: UploadFile = File(...), session: AsyncSession = Depends(get_session)
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="Invalid file format. Please upload an Excel file."
        )

    content = await file.read()
    parser = ExcelParser()
    try:
        data = parser.parse_file(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")

    # Save Teachers
    if "teachers" in data:
        for t_data in data["teachers"]:
            # Check if exists
            result = await session.execute(
                select(Teacher).where(Teacher.name == t_data["name"])
            )
            if not result.scalars().first():
                session.add(Teacher(**t_data))

    # Save Classrooms
    if "classrooms" in data:
        for c_data in data["classrooms"]:
            result = await session.execute(
                select(Classroom).where(Classroom.name == c_data["name"])
            )
            if not result.scalars().first():
                session.add(Classroom(**c_data))

    # Save Courses
    if "courses" in data:
        for co_data in data["courses"]:
            result = await session.execute(
                select(Course).where(Course.name == co_data["name"])
            )
            if not result.scalars().first():
                session.add(Course(**co_data))

    await session.commit()  # Commit basic entities first to get IDs

    # Save Student Groups & Entrance Terms
    if "student_groups" in data:
        for g_data in data["student_groups"]:
            # Find or Create EntranceTerm
            term_id = int(f"{g_data['entrance_year']}{g_data['entrance_semester']}")
            result = await session.execute(
                select(EntranceTerm).where(EntranceTerm.id == term_id)
            )
            term = result.scalars().first()
            if not term:
                term = EntranceTerm(
                    id=term_id,
                    year=g_data["entrance_year"],
                    semester=SemesterType(g_data["entrance_semester"]),
                )
                session.add(term)
                await session.commit()
                await session.refresh(term)

            # Create Group
            group = StudentGroup(
                name=g_data["name"],
                field=g_data["field"],
                degree=g_data["degree"],
                entrance_term_id=term.id,
                population=g_data["population"],
            )
            session.add(group)

    # Save Teacher-Course Links
    if "teacher_courses" in data:
        for link_data in data["teacher_courses"]:
            # Resolve IDs
            t_res = await session.execute(
                select(Teacher).where(Teacher.name == link_data["teacher_name"])
            )
            teacher = t_res.scalars().first()

            c_res = await session.execute(
                select(Course).where(Course.name == link_data["course_name"])
            )
            course = c_res.scalars().first()

            if teacher and course:
                # Check if link exists
                l_res = await session.execute(
                    select(TeacherCourseLink).where(
                        TeacherCourseLink.teacher_id == teacher.id,
                        TeacherCourseLink.course_id == course.id,
                    )
                )
                if not l_res.scalars().first():
                    session.add(
                        TeacherCourseLink(teacher_id=teacher.id, course_id=course.id)
                    )

    # Save Lessons (The actual requirements)
    if "lessons" in data:
        for l_data in data["lessons"]:
            # Resolve IDs
            c_res = await session.execute(
                select(Course).where(Course.name == l_data["course_name"])
            )
            course = c_res.scalars().first()

            g_res = await session.execute(
                select(StudentGroup).where(StudentGroup.name == l_data["group_name"])
            )
            group = g_res.scalars().first()

            teacher = None
            if l_data["teacher_name"]:
                t_res = await session.execute(
                    select(Teacher).where(Teacher.name == l_data["teacher_name"])
                )
                teacher = t_res.scalars().first()

            if course and group and teacher:
                lesson = Lesson(
                    course_id=course.id,
                    teacher_id=teacher.id,
                    group_id=group.id,
                    duration_slots=l_data["duration_slots"],
                )
                session.add(lesson)

    await session.commit()
    return {
        "message": "Data imported successfully",
        "details": {k: len(v) for k, v in data.items()},
    }
