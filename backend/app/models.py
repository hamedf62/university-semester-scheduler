from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


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


# Models


class EntranceTerm(SQLModel, table=True):
    id: int = Field(primary_key=True)  # e.g., 14031
    year: int
    semester: SemesterType

    student_groups: List["StudentGroup"] = Relationship(back_populates="entrance_term")
    teacher_links: List["TeacherEntranceLink"] = Relationship(
        back_populates="entrance_term"
    )


class Classroom(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    faculty: str
    capacity: int
    type: ClassroomType
    accessibility_features: Optional[str] = None


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    required_room_type: ClassroomType

    teacher_links: List["TeacherCourseLink"] = Relationship(back_populates="course")
    lessons: List["Lesson"] = Relationship(back_populates="course")


class Teacher(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    course_links: List["TeacherCourseLink"] = Relationship(back_populates="teacher")
    entrance_links: List["TeacherEntranceLink"] = Relationship(back_populates="teacher")
    lessons: List["Lesson"] = Relationship(back_populates="teacher")


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


class StudentGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    field: str
    degree: Degree
    entrance_term_id: int = Field(foreign_key="entranceterm.id")
    population: int

    entrance_term: EntranceTerm = Relationship(back_populates="student_groups")
    lessons: List["Lesson"] = Relationship(back_populates="group")


class Lesson(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.id")
    teacher_id: int = Field(foreign_key="teacher.id")
    group_id: int = Field(foreign_key="studentgroup.id")
    duration_slots: int = Field(default=1)  # Usually 1 slot (2 hours)

    course: Course = Relationship(back_populates="lessons")
    teacher: Teacher = Relationship(back_populates="lessons")
    group: StudentGroup = Relationship(back_populates="lessons")
    schedule_result: Optional["ScheduleResult"] = Relationship(back_populates="lesson")


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

    lesson: Lesson = Relationship(back_populates="schedule_result")
