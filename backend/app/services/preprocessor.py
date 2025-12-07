from typing import List
from app.models import Lesson


class Preprocessor:
    def merge_small_sections(
        self, lessons: List[Lesson], min_population: int = 50
    ) -> List[Lesson]:
        """
        Merges lessons of the same course and same student group (or compatible groups)
        if their combined population is less than min_population.

        Note: This is a simplified version. In reality, we might merge different groups
        taking the same course if they are in the same semester/field.
        """
        # Group by course_id and group_id (or just course_id if we want to merge different groups)
        # For now, let's assume we only merge sections of the exact same group and course
        # (which might happen if data is split in source).

        # A more advanced strategy: Group by Course. Then bin-pack groups into sections.

        # Placeholder for advanced logic
        return lessons
