import numpy as np
from typing import List, Dict
from app.models import Classroom


class ConstraintChecker:
    def __init__(
        self,
        num_genes: int,
        lesson_group_ids: np.ndarray,
        lesson_course_ids: np.ndarray,
        lesson_populations: np.ndarray,
        lesson_required_room_types: np.ndarray,
        lesson_allowed_days: List[List[int]],  # List of allowed days for each gene
        classrooms: List[Classroom],
        timeslot_days: np.ndarray,  # Map timeslot_id -> day_of_week
        teacher_allowed_slots_by_index: Dict[
            int, List[int]
        ] = None,  # Map teacher_idx -> allowed_slots
    ):
        self.num_genes = num_genes
        self.lesson_group_ids = lesson_group_ids
        self.lesson_course_ids = lesson_course_ids
        self.lesson_populations = lesson_populations
        self.lesson_required_room_types = lesson_required_room_types
        self.lesson_allowed_days = lesson_allowed_days
        self.timeslot_days = timeslot_days
        self.teacher_allowed_slots_by_index = teacher_allowed_slots_by_index or {}

        self.classroom_capacities = np.array([c.capacity for c in classrooms])
        # Convert Enum to string or int for comparison. Assuming types are consistent.
        self.classroom_types = np.array([c.type for c in classrooms])

    def calculate_violations(self, genome_genes: np.ndarray) -> int:
        """
        genome_genes: (num_genes, 4) array.
        col 0 = timeslot_idx
        col 1 = room_idx
        col 2 = parity
        col 3 = teacher_idx
        Returns total violation score (0 means valid).
        """
        violations = 0
        timeslot_indices = genome_genes[:, 0]
        room_indices = genome_genes[:, 1]
        parities = genome_genes[:, 2]
        teacher_indices = genome_genes[:, 3]

        # 1. Hard Constraints: Overlaps

        # Helper for overlap detection with parity
        # Parity: 0=Odd, 1=Even, 2=Both
        # Bitmask: Odd=1 (01), Even=2 (10), Both=3 (11)
        # Overlap if (mask1 & mask2) > 0
        parity_masks = np.choose(parities, [1, 2, 3])

        def count_conflicts(entity_ids):
            # Sort by (timeslot, entity)
            # We want to find rows with same timeslot AND same entity
            sorted_indices = np.lexsort((timeslot_indices, entity_ids))
            sorted_times = timeslot_indices[sorted_indices]
            sorted_entities = entity_ids[sorted_indices]
            sorted_masks = parity_masks[sorted_indices]

            diff_entity = np.diff(sorted_entities)
            diff_time = np.diff(sorted_times)

            # Candidates are adjacent rows with same entity and same time
            candidates = (diff_entity == 0) & (diff_time == 0)

            if not np.any(candidates):
                return 0

            # Check parity overlap for candidates
            mask_i = sorted_masks[:-1]
            mask_next = sorted_masks[1:]
            overlaps = (mask_i & mask_next) > 0

            return np.sum(candidates & overlaps)

        # Teacher Overlap
        v_teacher = count_conflicts(teacher_indices) * 1000
        violations += v_teacher

        # Group Overlap
        v_group = count_conflicts(self.lesson_group_ids) * 1000
        violations += v_group

        # Room Overlap
        v_room = count_conflicts(room_indices) * 1000
        violations += v_room

        # 2. Capacity & Type Check
        assigned_capacities = self.classroom_capacities[room_indices]
        v_cap = np.sum(assigned_capacities < self.lesson_populations) * 100
        violations += v_cap

        assigned_room_types = self.classroom_types[room_indices]
        v_type = np.sum(assigned_room_types != self.lesson_required_room_types) * 100
        violations += v_type

        # 3. Allowed Days Check
        assigned_days = self.timeslot_days[timeslot_indices]
        v_days = 0
        for i in range(self.num_genes):
            allowed = self.lesson_allowed_days[i]
            if allowed is not None and assigned_days[i] not in allowed:
                v_days += 100
        violations += v_days

        # 3.5 Teacher Availability Check
        if self.teacher_allowed_slots_by_index:
            v_teacher_avail = 0
            for i in range(self.num_genes):
                t_idx = teacher_indices[i]
                assigned_slot = timeslot_indices[i]

                if t_idx in self.teacher_allowed_slots_by_index:
                    allowed = self.teacher_allowed_slots_by_index[t_idx]
                    if allowed and assigned_slot not in allowed:
                        v_teacher_avail += 100
            violations += v_teacher_avail

        return violations
