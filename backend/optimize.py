import asyncio
from sqlmodel import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import engine
from app.models import (
    Lesson,
    Classroom,
    TimeSlot,
    Course,
    Teacher,
    StudentGroup,
    TeacherCourseLink,
    TeacherEntranceLink,
    ScheduleResult,
    WeekParity,
)
from app.solver.engine import SolverEngine


from sqlalchemy.orm import selectinload


async def optimize():
    print("Loading data for optimization...")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Load all necessary data
        lessons = (await session.execute(select(Lesson))).scalars().all()
        if not lessons:
            print("No lessons found. Please run seed_data.py first.")
            return

        classrooms = (await session.execute(select(Classroom))).scalars().all()
        timeslots = (await session.execute(select(TimeSlot))).scalars().all()
        courses = (await session.execute(select(Course))).scalars().all()

        # Eagerly load availability_links for teachers
        teachers = (
            (
                await session.execute(
                    select(Teacher).options(selectinload(Teacher.availability_links))
                )
            )
            .scalars()
            .all()
        )

        groups = (await session.execute(select(StudentGroup))).scalars().all()
        tc_links = (await session.execute(select(TeacherCourseLink))).scalars().all()

        # Define Optimized Weights
        # "sophisticated constraints... dont have idle time... student group only 3 days class"
        weights = {
            "teacher_idle": 10.0,  # High penalty for teacher gaps
            "student_idle": 5.0,  # Penalty for student gaps
            "student_compactness": 50.0,  # Very high penalty for extra days (target 3 days)
        }

        import json

        weights_json = json.dumps(weights)

        print("Initializing Solver with optimized weights:", weights)
        solver = SolverEngine(
            lessons=lessons,
            classrooms=classrooms,
            timeslots=timeslots,
            courses=courses,
            teachers=teachers,
            groups=groups,
            teacher_course_links=tc_links,
            teacher_entrance_links=[],
            weights=weights,
        )

        print("Running Genetic Algorithm (Population: 500, Generations: 2000)...")
        # Increase population and generations for better optimization
        results, best_cost = await solver.run(
            population_size=500, generations=2000, max_stagnant_generations=150
        )

        # Calculate satisfaction metrics
        import math

        satisfaction = 100.0 * math.exp(-best_cost / 1000.0)

        # Create SolverRun record
        import uuid

        run_id = str(uuid.uuid4())

        project_id = None
        if lessons:
            project_id = lessons[0].project_id

        if project_id is None:
            # Fetch a project
            from app.models import Project

            result = await session.execute(select(Project))
            project = result.scalars().first()
            if project:
                project_id = project.id
            else:
                print("Error: No project found in database. Cannot save run.")
                return

        from app.models import SolverRun
        from datetime import datetime

        status = "completed" if results else "failed"

        solver_run = SolverRun(
            project_id=project_id,
            run_id=run_id,
            status=status,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            config_weights=weights_json,
            fitness_score=best_cost,
            satisfaction_percentage=satisfaction,
        )
        session.add(solver_run)
        await session.commit()

        if results:
            print(
                f"Optimization Successful! Found schedule with {len(results)} assignments. Best Cost: {best_cost}"
            )

            # Save results to DB
            print("Saving results to DB...")

            # Save ScheduleResults
            db_results = []
            for res in results:
                parity = WeekParity.BOTH
                if res["week_parity"] == "odd":
                    parity = WeekParity.ODD
                elif res["week_parity"] == "even":
                    parity = WeekParity.EVEN

                db_results.append(
                    ScheduleResult(
                        run_id=run_id,
                        lesson_id=res["lesson_id"],
                        room_id=res["room_id"],
                        timeslot_id=res["timeslot_id"],
                        teacher_id=res["teacher_id"],
                        week_parity=parity,
                    )
                )

            session.add_all(db_results)
            await session.commit()
            print(f"Results saved with Run ID: {run_id}")
            print(f"Saved {len(db_results)} schedule results with Run ID: {run_id}")

        else:
            print(
                f"Optimization Failed. Could not find a valid schedule satisfying all hard constraints. Best Cost: {best_cost}. Run saved as failed."
            )


if __name__ == "__main__":
    asyncio.run(optimize())
