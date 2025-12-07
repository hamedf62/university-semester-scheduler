import numpy as np
from typing import Dict


class FitnessCalculator:
    def __init__(self, weights: Dict[str, float], num_days: int = 6):
        self.weights = weights
        self.num_days = num_days

    def calculate_cost(
        self,
        genome_genes: np.ndarray,
        lesson_group_ids: np.ndarray,
        timeslot_day_map: np.ndarray,  # Map timeslot_idx -> day_idx (0-5)
        timeslot_daily_idx_map: np.ndarray,  # Map timeslot_idx -> 0, 1, 2, 3, 4
    ) -> float:
        """
        Calculate the weighted cost (lower is better).
        """
        cost = 0.0
        timeslot_indices = genome_genes[:, 0]
        parities = genome_genes[:, 2]  # 0, 1, 2
        teacher_indices = genome_genes[:, 3]

        # Helper to calculate gaps for a set of slots
        def calc_gaps(slots):
            if len(slots) <= 1:
                return 0
            daily_slots = timeslot_daily_idx_map[slots]
            # Sort by daily slot
            daily_slots.sort()
            # Gaps = sum(diff - 1)
            return np.sum(np.diff(daily_slots) - 1)

        # 1. Teacher Idle Time (Gaps)
        unique_teachers = np.unique(teacher_indices)
        for t_idx in unique_teachers:
            t_mask = teacher_indices == t_idx
            t_slots = timeslot_indices[t_mask]
            t_parities = parities[t_mask]
            t_days = timeslot_day_map[t_slots]

            # For each day the teacher works
            for d in np.unique(t_days):
                day_mask = t_days == d
                d_slots = t_slots[day_mask]
                d_parities = t_parities[day_mask]

                # Odd Week Slots: Parity is ODD(0) or BOTH(2)
                odd_mask = (d_parities == 0) | (d_parities == 2)
                odd_slots = d_slots[odd_mask]
                cost += calc_gaps(odd_slots) * self.weights.get("teacher_idle", 1.0)

                # Even Week Slots: Parity is EVEN(1) or BOTH(2)
                even_mask = (d_parities == 1) | (d_parities == 2)
                even_slots = d_slots[even_mask]
                cost += calc_gaps(even_slots) * self.weights.get("teacher_idle", 1.0)

        # 2. Student Constraints
        unique_groups = np.unique(lesson_group_ids)
        for g_id in unique_groups:
            g_mask = lesson_group_ids == g_id
            g_slots = timeslot_indices[g_mask]
            g_parities = parities[g_mask]
            g_days = timeslot_day_map[g_slots]

            # Compactness: Count unique days
            # Odd Week Days
            odd_mask = (g_parities == 0) | (g_parities == 2)
            odd_days = np.unique(g_days[odd_mask])
            cost += len(odd_days) * self.weights.get("student_compactness", 1.0)

            # Even Week Days
            even_mask = (g_parities == 1) | (g_parities == 2)
            even_days = np.unique(g_days[even_mask])
            cost += len(even_days) * self.weights.get("student_compactness", 1.0)

            # Idle Time (Gaps)
            for d in np.unique(g_days):
                day_mask = g_days == d
                d_slots = g_slots[day_mask]
                d_parities = g_parities[day_mask]

                odd_slots = d_slots[(d_parities == 0) | (d_parities == 2)]
                cost += calc_gaps(odd_slots) * self.weights.get("student_idle", 1.0)

                even_slots = d_slots[(d_parities == 1) | (d_parities == 2)]
                cost += calc_gaps(even_slots) * self.weights.get("student_idle", 1.0)

        return cost
