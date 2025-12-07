import numpy as np
from typing import Dict


class FitnessCalculator:
    def __init__(self, weights: Dict[str, float], num_days: int = 6):
        self.weights = weights
        self.num_days = num_days

    def calculate_cost(
        self,
        genome_genes: np.ndarray,
        lesson_teacher_ids: np.ndarray,
        lesson_group_ids: np.ndarray,
        timeslot_day_map: np.ndarray,
    ) -> float:
        """
        Calculate the weighted cost (lower is better).
        timeslot_day_map: array mapping timeslot_idx to day_idx (0-5)
        """
        cost = 0.0
        timeslot_indices = genome_genes[:, 0]

        # Map timeslots to days
        days = timeslot_day_map[timeslot_indices]

        # 1. Teacher Gaps
        # For each teacher, check their daily schedule.
        # Ideally, they should have continuous blocks.
        unique_teachers = np.unique(lesson_teacher_ids)
        for t_id in unique_teachers:
            t_mask = lesson_teacher_ids == t_id
            t_days = days[t_mask]
            t_slots = timeslot_indices[t_mask]

            # For each day the teacher works
            for d in np.unique(t_days):
                d_slots = np.sort(t_slots[t_days == d])
                if len(d_slots) > 1:
                    # Calculate gaps: difference between adjacent slots - 1
                    # Assuming slots are sequential integers for the day
                    # We need a map from timeslot_idx to daily_slot_idx (0-4)
                    # Let's assume timeslot_idx = day * 5 + slot
                    daily_slots = d_slots % 5
                    gaps = np.sum(np.diff(daily_slots) - 1)
                    cost += gaps * self.weights.get("teacher_gaps", 1.0)

        # 2. Student Compactness (3 days preferred)
        unique_groups = np.unique(lesson_group_ids)
        for g_id in unique_groups:
            g_mask = lesson_group_ids == g_id
            g_days = np.unique(days[g_mask])
            num_active_days = len(g_days)

            # Penalty if > 3 days
            if num_active_days > 3:
                cost += (num_active_days - 3) * self.weights.get(
                    "student_compactness", 1.0
                )

            # 3. Student Gaps
            g_slots = timeslot_indices[g_mask]
            g_days_full = days[g_mask]
            for d in g_days:
                d_slots = np.sort(g_slots[g_days_full == d])
                if len(d_slots) > 1:
                    daily_slots = d_slots % 5
                    gaps = np.sum(np.diff(daily_slots) - 1)
                    cost += gaps * self.weights.get("student_gaps", 1.0)

        # 4. Room Utilization (Optional)
        # cost += ...

        return cost
