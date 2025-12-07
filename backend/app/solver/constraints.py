import numpy as np
from typing import List, Dict
from app.models import (
    Lesson,
    Classroom,
    Course,
    Teacher,
    StudentGroup,
    TeacherCourseLink,
    TeacherEntranceLink,
)


class ConstraintChecker:
    def __init__(
        self,
        lessons: List[Lesson],
        classrooms: List[Classroom],
        courses: List[Course],
        teachers: List[Teacher],
        groups: List[StudentGroup],
        teacher_course_links: List[TeacherCourseLink],
        teacher_entrance_links: List[TeacherEntranceLink],
    ):

        self.lessons = lessons
        self.classrooms = classrooms
        self.courses = {c.id: c for c in courses}
        self.teachers = {t.id: t for t in teachers}
        self.groups = {g.id: g for g in groups}

        # Precompute mappings for fast lookup
        self.lesson_teacher_ids = np.array([l.teacher_id for l in lessons])
        self.lesson_group_ids = np.array([l.group_id for l in lessons])
        self.lesson_course_ids = np.array([l.course_id for l in lessons])
        self.lesson_populations = np.array(
            [self.groups[l.group_id].population for l in lessons]
        )

        self.classroom_capacities = np.array([c.capacity for c in classrooms])
        self.classroom_types = np.array([c.type for c in classrooms])

        # Capability Matrices (could be optimized further)
        self.teacher_course_allowed = set(
            (l.teacher_id, l.course_id) for l in teacher_course_links
        )
        self.teacher_entrance_allowed = set(
            (l.teacher_id, l.entrance_term_id) for l in teacher_entrance_links
        )

    def check_hard_constraints(self, genome_genes: np.ndarray) -> bool:
        """
        genome_genes: (num_lessons, 2) array. col 0 = timeslot_idx, col 1 = room_idx
        """
        timeslot_indices = genome_genes[:, 0]
        room_indices = genome_genes[:, 1]

        num_lessons = len(self.lessons)

        # 1. Room Capacity
        # Check if assigned room capacity >= lesson population
        assigned_capacities = self.classroom_capacities[room_indices]
        if np.any(self.lesson_populations > assigned_capacities):
            return False

            # 2. Room Type Compatibility
        # Check if assigned room type matches course requirement
        assigned_room_types = self.classroom_types[room_indices]

        # Map lesson -> course -> required_type
        # We need an array of required_room_types aligned with lessons
        # Precompute this in __init__ for speed
        if not hasattr(self, "lesson_required_room_types"):
            self.lesson_required_room_types = np.array(
                [self.courses[l.course_id].required_room_type for l in self.lessons]
            )

        # Compare arrays
        # Note: Enum comparison in numpy might need string conversion or int mapping
        # Assuming types are strings or compatible enums
        if np.any(assigned_room_types != self.lesson_required_room_types):
            return False

        # 3. Conflicts (Teacher, Room, Group)

        # 3. Conflicts (Teacher, Room, Group)
        # We need to check if any two lessons share the same (TimeSlot, Entity) pair.

        # Create a combined ID for checking duplicates
        # We can use sorting to find duplicates efficiently

        # Room Conflict: Same TimeSlot, Same Room
        # Combine TimeSlot and Room into a single integer (assuming < 10000 rooms)
        room_time_hashes = timeslot_indices * 10000 + room_indices
        if len(np.unique(room_time_hashes)) != num_lessons:
            return False  # Duplicate (Time, Room) found

        # Teacher Conflict: Same TimeSlot, Same Teacher
        teacher_time_hashes = timeslot_indices * 10000 + self.lesson_teacher_ids
        if len(np.unique(teacher_time_hashes)) != num_lessons:
            return False

        # Group Conflict: Same TimeSlot, Same Group
        group_time_hashes = timeslot_indices * 10000 + self.lesson_group_ids
        if len(np.unique(group_time_hashes)) != num_lessons:
            return False

        # 4. Teacher Capability & Entrance Restrictions
        # These are static checks on the Lesson definition itself, not the schedule.
        # They should be checked before the solver runs or during lesson creation.
        # However, if the solver assigns teachers (which it doesn't in this model, it assigns times/rooms to existing lessons),
        # then we don't need to check it here.
        # The prompt says "assigning teacher to course", implying the solver might assign teachers?
        # "assigning teacher to course per semester"
        # If the solver assigns teachers, the genome needs a 3rd column for teacher_idx.
        # The current TODO says "Genome ... mapping of Lesson -> (TimeSlot, Classroom)".
        # And the Lesson model has `teacher_id` as a foreign key.
        # So I assume the Teacher is already assigned to the Lesson before scheduling.
        # If the goal is to ALSO assign teachers, the Lesson model shouldn't have teacher_id fixed yet.
        # But for now, I'll stick to the TODO which implies scheduling fixed lessons.

        return True
