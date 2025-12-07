from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


from datetime import datetime


# Enums
class ClassroomType(str, Enum):
    NORMAL = "normal"
    COMPUTER_SITE = "computer_site"
    GALLERY = "gallery"
    WORKSHOP = "workshop"


class Degree(str, Enum):
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    COLLEGE = "college"


class SemesterType(int, Enum):
    FIRST = 1
    SECOND = 2


class WeekParity(str, Enum):
    ODD = "odd"
    EVEN = "even"
    BOTH = "both"


# Models


class EntranceTerm(SQLModel, table=True):
    id: int = Field(primary_key=True)  # e.g., 14031
    year: int
    semester: SemesterType

    teacher_links: List["TeacherEntranceLink"] = Relationship(
        back_populates="entrance_term"
    )


class Classroom(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    faculty: str
    capacity: int
    type: ClassroomType
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    project_links: List["ProjectClassroomLink"] = Relationship(
        back_populates="classroom"
    )


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    required_room_type: ClassroomType
    units: int = Field(default=2)
    min_population: Optional[int] = Field(default=20)
    max_population: Optional[int] = Field(default=40)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    teacher_links: List["TeacherCourseLink"] = Relationship(back_populates="course")
    lessons: List["Lesson"] = Relationship(back_populates="course")
    student_group_links: List["StudentGroupCourseLink"] = Relationship(
        back_populates="course"
    )
    project_links: List["ProjectCourseLink"] = Relationship(back_populates="course")


class TeacherAvailability(SQLModel, table=True):
    teacher_id: int = Field(foreign_key="teacher.id", primary_key=True)
    timeslot_id: int = Field(foreign_key="timeslot.id", primary_key=True)
    project_id: int = Field(foreign_key="project.id", primary_key=True)

    teacher: "Teacher" = Relationship(back_populates="availability_links")
    timeslot: "TimeSlot" = Relationship()
    project: "Project" = Relationship()


class Teacher(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # available_slots field removed in favor of availability_links

    course_links: List["TeacherCourseLink"] = Relationship(back_populates="teacher")
    entrance_links: List["TeacherEntranceLink"] = Relationship(back_populates="teacher")
    lessons: List["Lesson"] = Relationship(back_populates="teacher")
    availability_links: List["TeacherAvailability"] = Relationship(
        back_populates="teacher"
    )
    project_links: List["ProjectTeacherLink"] = Relationship(back_populates="teacher")


class TeacherCourseLink(SQLModel, table=True):
    teacher_id: int = Field(foreign_key="teacher.id", primary_key=True)
    course_id: int = Field(foreign_key="course.id", primary_key=True)

    teacher: Teacher = Relationship(back_populates="course_links")
    course: Course = Relationship(back_populates="teacher_links")


class TeacherEntranceLink(SQLModel, table=True):
    teacher_id: int = Field(foreign_key="teacher.id", primary_key=True)
    entrance_term_id: int = Field(foreign_key="entranceterm.id", primary_key=True)

    teacher: Teacher = Relationship(back_populates="entrance_links")
    entrance_term: EntranceTerm = Relationship(back_populates="teacher_links")


class ProjectTeacherLink(SQLModel, table=True):
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    teacher_id: int = Field(foreign_key="teacher.id", primary_key=True)
    project: "Project" = Relationship(back_populates="teacher_links")
    teacher: "Teacher" = Relationship(back_populates="project_links")


class ProjectCourseLink(SQLModel, table=True):
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    course_id: int = Field(foreign_key="course.id", primary_key=True)
    project: "Project" = Relationship(back_populates="course_links")
    course: "Course" = Relationship(back_populates="project_links")


class ProjectStudentGroupLink(SQLModel, table=True):
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    group_id: int = Field(foreign_key="studentgroup.id", primary_key=True)
    project: "Project" = Relationship(back_populates="group_links")
    group: "StudentGroup" = Relationship(back_populates="project_links")


class ProjectClassroomLink(SQLModel, table=True):
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    classroom_id: int = Field(foreign_key="classroom.id", primary_key=True)
    project: "Project" = Relationship(back_populates="classroom_links")
    classroom: "Classroom" = Relationship(back_populates="project_links")


class StudentGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    degree: Degree
    population: int
    allowed_days: Optional[str] = Field(default=None)  # e.g., "0,2,4"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    lessons: List["Lesson"] = Relationship(back_populates="group")
    course_links: List["StudentGroupCourseLink"] = Relationship(back_populates="group")
    project_links: List["ProjectStudentGroupLink"] = Relationship(
        back_populates="group"
    )


class StudentGroupCourseLink(SQLModel, table=True):
    group_id: int = Field(foreign_key="studentgroup.id", primary_key=True)
    course_id: int = Field(foreign_key="course.id", primary_key=True)

    group: StudentGroup = Relationship(back_populates="course_links")
    course: Course = Relationship(back_populates="student_group_links")


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="New Project")
    description: Optional[str] = None
    term_id: Optional[int] = None  # e.g. 14032
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    lessons: List["Lesson"] = Relationship(back_populates="project")
    solver_runs: List["SolverRun"] = Relationship(back_populates="project")

    teacher_links: List["ProjectTeacherLink"] = Relationship(back_populates="project")
    course_links: List["ProjectCourseLink"] = Relationship(back_populates="project")
    group_links: List["ProjectStudentGroupLink"] = Relationship(
        back_populates="project"
    )
    classroom_links: List["ProjectClassroomLink"] = Relationship(
        back_populates="project"
    )


class SolverRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    run_id: str = Field(index=True, unique=True)  # UUID
    status: str = Field(default="running")  # running, completed, failed
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    config_weights: str  # JSON string of weights
    fitness_score: float = 0.0
    satisfaction_percentage: float = 0.0

    project: Project = Relationship(back_populates="solver_runs")


class Lesson(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    course_id: int = Field(foreign_key="course.id")
    teacher_id: Optional[int] = Field(default=None, foreign_key="teacher.id")
    group_id: int = Field(foreign_key="studentgroup.id")
    duration_slots: int = Field(default=1)  # Usually 1 slot (2 hours)

    project: Optional[Project] = Relationship(back_populates="lessons")
    course: Course = Relationship(back_populates="lessons")
    teacher: Optional[Teacher] = Relationship(back_populates="lessons")
    group: StudentGroup = Relationship(back_populates="lessons")
    schedule_results: List["ScheduleResult"] = Relationship(back_populates="lesson")


class TimeSlot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    day_of_week: int  # 0=Saturday, 1=Sunday, ... 5=Thursday, 6=Friday
    start_time: str  # "08:00"
    end_time: str  # "10:00"


class ScheduleResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str  # UUID for the solver run
    lesson_id: int = Field(foreign_key="lesson.id")
    room_id: int = Field(foreign_key="classroom.id")
    timeslot_id: int = Field(foreign_key="timeslot.id")
    teacher_id: int = Field(foreign_key="teacher.id")
    week_parity: WeekParity = Field(default=WeekParity.BOTH)

    lesson: Lesson = Relationship(back_populates="schedule_results")
    room: "Classroom" = Relationship()
    timeslot: "TimeSlot" = Relationship()
    teacher: "Teacher" = Relationship()
