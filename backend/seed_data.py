import asyncio
import random
from sqlmodel import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import engine, init_db
from app.models import (
    TimeSlot,
    Classroom,
    ClassroomType,
    StudentGroup,
    Degree,
    Teacher,
    Course,
    TeacherCourseLink,
    StudentGroupCourseLink,
    Project,
    Lesson,
    TeacherAvailability,
    ProjectTeacherLink,
    ProjectCourseLink,
    ProjectClassroomLink,
    ProjectStudentGroupLink,
)


async def seed():
    print("Initializing DB...")
    await init_db()

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 0. Create Project
        print("Seeding Project...")
        result = await session.execute(
            select(Project).where(Project.name == "Semester 1403-1")
        )
        project = result.scalars().first()
        if not project:
            project = Project(
                name="Semester 1403-1", description="Default seeded project"
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)

        project_id = project.id

        # 1. TimeSlots
        print("Seeding TimeSlots...")
        result = await session.execute(select(TimeSlot))
        existing_slots = result.scalars().all()
        if not existing_slots:
            slots = []
            days = range(6)  # Sat to Thu
            # 08:00 to 20:00 (6 slots of 2 hours)
            times = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]
            for d in days:
                for i in range(len(times) - 1):
                    slots.append(
                        TimeSlot(
                            day_of_week=d, start_time=times[i], end_time=times[i + 1]
                        )
                    )
            session.add_all(slots)
            await session.commit()
            # Refresh to get IDs
            result = await session.execute(select(TimeSlot))
            existing_slots = result.scalars().all()

        timeslot_map = {(ts.day_of_week, ts.start_time): ts.id for ts in existing_slots}

        # 2. Classrooms
        print("Seeding Classrooms...")
        result = await session.execute(select(Classroom))
        existing_rooms = result.scalars().all()

        if not existing_rooms:
            rooms = []
            # 20 Classrooms
            for i in range(1, 21):
                rooms.append(
                    Classroom(
                        name=f"Room {100+i}",
                        faculty="Eng",
                        capacity=60,  # Increased capacity
                        type=ClassroomType.NORMAL,
                    )
                )
            for i in range(1, 6):  # More sites
                rooms.append(
                    Classroom(
                        name=f"Site {i}",
                        faculty="Eng",
                        capacity=50,  # Increased capacity
                        type=ClassroomType.COMPUTER_SITE,
                    )
                )
            for i in range(1, 6):  # More workshops
                rooms.append(
                    Classroom(
                        name=f"Workshop {i}",
                        faculty="Eng",
                        capacity=50,  # Increased capacity
                        type=ClassroomType.WORKSHOP,
                    )
                )
            session.add_all(rooms)
            await session.commit()

            # Link to Project
            for room in rooms:
                session.add(
                    ProjectClassroomLink(project_id=project_id, classroom_id=room.id)
                )
            await session.commit()
        else:
            # Update capacities of existing rooms to ensure solvability
            for room in existing_rooms:
                if room.type == ClassroomType.NORMAL:
                    room.capacity = 60
                else:
                    room.capacity = 50
                session.add(room)
            await session.commit()

            # Ensure links exist
            for room in existing_rooms:
                link = await session.get(ProjectClassroomLink, (project_id, room.id))
                if not link:
                    session.add(
                        ProjectClassroomLink(
                            project_id=project_id, classroom_id=room.id
                        )
                    )
            await session.commit()

        # 3. Teachers
        print("Seeding Teachers...")
        result = await session.execute(select(Teacher))
        teachers = result.scalars().all()
        if len(teachers) < 50:
            new_teachers = []
            start_idx = len(teachers) + 1
            for i in range(start_idx, 51):
                teacher = Teacher(name=f"Teacher {i}")
                session.add(teacher)
                await session.commit()
                await session.refresh(teacher)
                new_teachers.append(teacher)

                # Availability
                is_evening = i > 20
                if is_evening:
                    for ts in existing_slots:
                        if ts.start_time >= "14:00":
                            session.add(
                                TeacherAvailability(
                                    teacher_id=teacher.id, timeslot_id=ts.id
                                )
                            )
                else:
                    # All slots
                    for ts in existing_slots:
                        session.add(
                            TeacherAvailability(
                                teacher_id=teacher.id, timeslot_id=ts.id
                            )
                        )

                # Link to Project
                session.add(
                    ProjectTeacherLink(project_id=project_id, teacher_id=teacher.id)
                )

            await session.commit()

            # Reload teachers
            result = await session.execute(select(Teacher))
            teachers = result.scalars().all()
        else:
            # Ensure links exist
            for t in teachers:
                link = await session.get(ProjectTeacherLink, (project_id, t.id))
                if not link:
                    session.add(
                        ProjectTeacherLink(project_id=project_id, teacher_id=t.id)
                    )
            await session.commit()

        # 4. Courses
        print("Seeding Courses...")
        result = await session.execute(select(Course))
        courses = result.scalars().all()
        if len(courses) < 50:
            new_courses = []
            start_idx = len(courses) + 1
            for i in range(start_idx, 51):
                units = 3 if random.random() < 0.8 else 2
                rtype = ClassroomType.NORMAL
                if random.random() < 0.1:
                    rtype = ClassroomType.COMPUTER_SITE

                course = Course(
                    name=f"Course {i}",
                    units=units,
                    required_room_type=rtype,
                    min_population=20,
                    max_population=60,
                )
                session.add(course)
                await session.commit()
                await session.refresh(course)
                new_courses.append(course)

                # Link to Project
                session.add(
                    ProjectCourseLink(project_id=project_id, course_id=course.id)
                )

            await session.commit()

            # Reload courses
            result = await session.execute(select(Course))
            courses = result.scalars().all()
        else:
            # Ensure links exist
            for c in courses:
                link = await session.get(ProjectCourseLink, (project_id, c.id))
                if not link:
                    session.add(
                        ProjectCourseLink(project_id=project_id, course_id=c.id)
                    )
            await session.commit()

        # 5. StudentGroups (20 Groups)
        print("Seeding StudentGroups...")
        result = await session.execute(select(StudentGroup))
        groups = result.scalars().all()

        # We want exactly 20 groups for this project if possible, or ensure at least 20 exist
        if len(groups) < 20:
            new_groups = []
            start_idx = len(groups) + 1
            for i in range(start_idx, 21):
                group = StudentGroup(
                    name=f"Group {i}",
                    degree=Degree.BACHELOR,
                    population=random.randint(30, 50),
                    allowed_days="0,1,2,3,4,5",
                )
                session.add(group)
                await session.commit()
                await session.refresh(group)
                new_groups.append(group)

                # Link to Project
                session.add(
                    ProjectStudentGroupLink(project_id=project_id, group_id=group.id)
                )

            await session.commit()

            result = await session.execute(select(StudentGroup))
            groups = result.scalars().all()
        else:
            # Ensure links exist
            for g in groups:
                link = await session.get(ProjectStudentGroupLink, (project_id, g.id))
                if not link:
                    session.add(
                        ProjectStudentGroupLink(project_id=project_id, group_id=g.id)
                    )
            await session.commit()

        # 6. TeacherCourseLink
        print("Linking Teachers to Courses...")
        result = await session.execute(select(TeacherCourseLink))
        links = result.scalars().all()
        if not links:
            for course in courses:
                # Pick 3 random teachers
                assigned_teachers = random.sample(teachers, k=3)
                for t in assigned_teachers:
                    # Check if link exists
                    link = await session.get(TeacherCourseLink, (t.id, course.id))
                    if not link:
                        session.add(
                            TeacherCourseLink(teacher_id=t.id, course_id=course.id)
                        )
            await session.commit()

        # 7. StudentGroupCourseLink (Curriculum)
        print("Linking Groups to Courses...")
        # Ensure every group has courses
        for group in groups:
            # Check if group has any courses
            stmt = select(StudentGroupCourseLink).where(
                StudentGroupCourseLink.group_id == group.id
            )
            existing_links = (await session.execute(stmt)).scalars().all()

            if not existing_links:
                # Assign ~6 courses to each group
                group_courses = random.sample(courses, k=min(6, len(courses)))
                for c in group_courses:
                    session.add(
                        StudentGroupCourseLink(group_id=group.id, course_id=c.id)
                    )
        await session.commit()

        # 8. Lessons (Derived from Group-Course Links)
        print("Generating Lessons...")
        # Clear existing lessons for this project to avoid duplicates if re-running
        # In a real scenario, we might want to be more careful, but for seeding/testing:
        # await session.execute(delete(Lesson).where(Lesson.project_id == project_id))

        # For each group, for each course they need, create a Lesson
        # We need to know which teacher teaches which course.
        # For simplicity in seeding, we'll pick the FIRST available teacher for that course.

        # Reload data to be sure
        groups = (await session.execute(select(StudentGroup))).scalars().all()

        # We need to fetch links again or use relationships if loaded.
        # Let's iterate and check links.

        lessons_created = 0
        for group in groups:
            # Get courses for this group
            # We can use the link table directly
            stmt = select(StudentGroupCourseLink).where(
                StudentGroupCourseLink.group_id == group.id
            )
            sg_links = (await session.execute(stmt)).scalars().all()

            for link in sg_links:
                course_id = link.course_id

                # Find a teacher for this course
                stmt_tc = select(TeacherCourseLink).where(
                    TeacherCourseLink.course_id == course_id
                )
                tc_links = (await session.execute(stmt_tc)).scalars().all()

                if tc_links:
                    # Pick a random teacher from those who can teach it
                    chosen_tc = random.choice(tc_links)
                    teacher_id = chosen_tc.teacher_id

                    # Create Lesson
                    # Check if exists first?
                    # For now, let's assume if we are seeding fresh or just appending
                    # We'll check if a lesson exists for this group+course+project
                    stmt_lesson = select(Lesson).where(
                        Lesson.project_id == project_id,
                        Lesson.group_id == group.id,
                        Lesson.course_id == course_id,
                    )
                    existing_lesson = (
                        (await session.execute(stmt_lesson)).scalars().first()
                    )

                    if not existing_lesson:
                        lesson = Lesson(
                            project_id=project_id,
                            course_id=course_id,
                            teacher_id=teacher_id,
                            group_id=group.id,
                            duration_slots=1,  # Default 2 hours
                        )
                        session.add(lesson)
                        lessons_created += 1

        await session.commit()
        print(f"Created {lessons_created} new lessons.")

    print("Seeding Complete.")


if __name__ == "__main__":
    asyncio.run(seed())
