import asyncio
import os
import pandas as pd
from app.db import init_db, get_session
from app.models import TimeSlot
from app.api.upload import upload_data
from app.api.solver import run_solver_task
from fastapi import UploadFile
from io import BytesIO


# Mock Data Creation
def create_mock_excel():
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Teachers
        pd.DataFrame(
            [{"Name": "Dr. Smith"}, {"Name": "Prof. Johnson"}, {"Name": "Dr. Brown"}]
        ).to_excel(writer, sheet_name="Teachers", index=False)

        # Classrooms
        pd.DataFrame(
            [
                {
                    "Name": "Room 101",
                    "Faculty": "Science",
                    "Capacity": 60,
                    "Type": "normal",
                },
                {
                    "Name": "Lab A",
                    "Faculty": "Science",
                    "Capacity": 30,
                    "Type": "computer_site",
                },
                {
                    "Name": "Hall 1",
                    "Faculty": "Arts",
                    "Capacity": 100,
                    "Type": "normal",
                },
            ]
        ).to_excel(writer, sheet_name="Classrooms", index=False)

        # Courses
        pd.DataFrame(
            [
                {"Name": "Intro to CS", "RequiredRoomType": "normal"},
                {"Name": "Programming 1", "RequiredRoomType": "computer_site"},
                {"Name": "History", "RequiredRoomType": "normal"},
            ]
        ).to_excel(writer, sheet_name="Courses", index=False)

        # StudentGroups
        pd.DataFrame(
            [
                {
                    "Name": "CS-2024",
                    "Field": "CS",
                    "Degree": "bachelor",
                    "EntranceYear": 1403,
                    "EntranceSemester": 1,
                    "Population": 50,
                },
                {
                    "Name": "Arts-2024",
                    "Field": "Arts",
                    "Degree": "bachelor",
                    "EntranceYear": 1403,
                    "EntranceSemester": 1,
                    "Population": 40,
                },
            ]
        ).to_excel(writer, sheet_name="StudentGroups", index=False)

        # TeacherCourses
        pd.DataFrame(
            [
                {"TeacherName": "Dr. Smith", "CourseName": "Intro to CS"},
                {"TeacherName": "Dr. Smith", "CourseName": "Programming 1"},
                {"TeacherName": "Prof. Johnson", "CourseName": "History"},
                {"TeacherName": "Dr. Brown", "CourseName": "Programming 1"},
            ]
        ).to_excel(writer, sheet_name="TeacherCourses", index=False)

        # Lessons (Requirements)
        pd.DataFrame(
            [
                {
                    "Course": "Intro to CS",
                    "Group": "CS-2024",
                    "Teacher": "Dr. Smith",
                    "DurationSlots": 1,
                },
                {
                    "Course": "Programming 1",
                    "Group": "CS-2024",
                    "Teacher": "Dr. Brown",
                    "DurationSlots": 1,
                },
                {
                    "Course": "History",
                    "Group": "Arts-2024",
                    "Teacher": "Prof. Johnson",
                    "DurationSlots": 1,
                },
            ]
        ).to_excel(writer, sheet_name="Lessons", index=False)

    output.seek(0)
    return output


async def seed_timeslots():
    async for session in get_session():
        # Check if timeslots exist
        # For simplicity, just add if empty
        # In real app, use a migration or seed script
        from sqlalchemy.future import select

        res = await session.execute(select(TimeSlot))
        if not res.scalars().first():
            slots = []
            for day in range(6):  # Sat-Fri
                slots.append(
                    TimeSlot(day_of_week=day, start_time="08:00", end_time="10:00")
                )
                slots.append(
                    TimeSlot(day_of_week=day, start_time="10:00", end_time="12:00")
                )
                slots.append(
                    TimeSlot(day_of_week=day, start_time="12:00", end_time="14:00")
                )
                slots.append(
                    TimeSlot(day_of_week=day, start_time="14:00", end_time="16:00")
                )
                slots.append(
                    TimeSlot(day_of_week=day, start_time="16:00", end_time="18:00")
                )
            session.add_all(slots)
            await session.commit()
            print("Seeded TimeSlots.")


async def main():
    print("Initializing DB...")
    await init_db()
    await seed_timeslots()

    print("Creating Mock Excel...")
    excel_file = create_mock_excel()

    print("Uploading Data...")
    # Simulate Upload
    async for session in get_session():
        upload_file = UploadFile(filename="test.xlsx", file=excel_file)
        await upload_data(upload_file, session)

    print("Running Solver...")
    weights = {"teacher_gaps": 1.0, "student_compactness": 1.0, "student_gaps": 1.0}

    # Run directly (not via API endpoint to avoid background task complexity in script)
    await run_solver_task("test-run-1", weights)

    print("Done! Check database for results.")


if __name__ == "__main__":
    asyncio.run(main())
