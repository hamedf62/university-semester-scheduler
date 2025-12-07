import asyncio
import numpy as np
from typing import List, Dict, Any
from collections import defaultdict
from app.models import (
    Lesson,
    Classroom,
    Course,
    Teacher,
    StudentGroup,
    TeacherCourseLink,
    TeacherEntranceLink,
    TimeSlot,
)
from app.solver.genome import Population, Genome
from app.solver.constraints import ConstraintChecker
from app.solver.fitness import FitnessCalculator
from app.solver.operators import GeneticOperators


class SolverEngine:
    def __init__(
        self,
        lessons: List[Lesson],
        classrooms: List[Classroom],
        timeslots: List[TimeSlot],
        courses: List[Course],
        teachers: List[Teacher],
        groups: List[StudentGroup],
        teacher_course_links: List[TeacherCourseLink],
        teacher_entrance_links: List[TeacherEntranceLink],
        weights: Dict[str, float],
    ):

        self.lessons = lessons
        self.classrooms = classrooms
        self.timeslots = timeslots
        self.courses_map = {c.id: c for c in courses}
        self.groups_map = {g.id: g for g in groups}
        self.teachers = teachers

        # Map teachers to indices
        self.teacher_id_to_idx = {t.id: i for i, t in enumerate(teachers)}
        self.teacher_idx_to_id = {i: t.id for i, t in enumerate(teachers)}

        # Map Course -> Valid Teacher Indices
        self.course_valid_teachers = defaultdict(list)
        for link in teacher_course_links:
            if link.teacher_id in self.teacher_id_to_idx:
                t_idx = self.teacher_id_to_idx[link.teacher_id]
                self.course_valid_teachers[link.course_id].append(t_idx)

        # 1. Preprocess Lessons into Genes (SubLessons)
        self.gene_metadata = []  # List of dicts with metadata
        self.fixed_parities = []

        # Arrays for ConstraintChecker
        group_ids = []
        course_ids = []
        populations = []
        req_room_types = []
        allowed_days = []

        self.valid_teachers_per_gene = []

        for lesson in lessons:
            course = self.courses_map[lesson.course_id]
            group = self.groups_map[lesson.group_id]
            units = course.units

            # Determine valid teachers for this lesson
            valid_teacher_indices = []
            if lesson.teacher_id is not None:
                # Pre-assigned teacher
                if lesson.teacher_id in self.teacher_id_to_idx:
                    valid_teacher_indices = [self.teacher_id_to_idx[lesson.teacher_id]]
                else:
                    # Fallback
                    valid_teacher_indices = self.course_valid_teachers.get(
                        course.id, []
                    )
            else:
                # Dynamic assignment
                valid_teacher_indices = self.course_valid_teachers.get(course.id, [])

            if not valid_teacher_indices:
                # Fallback: all teachers if none found (should be handled by validation ideally)
                valid_teacher_indices = list(self.teacher_id_to_idx.values())

            # Parse allowed days
            g_allowed = None
            if group.allowed_days:
                # "0,2,4" -> [0, 2, 4]
                try:
                    g_allowed = [int(d) for d in group.allowed_days.split(",")]
                except:
                    pass

            # Determine SubLessons
            # 2 Units -> 1 Gene (Both)
            # 3 Units -> 2 Genes (1 Both, 1 Variable)
            # 1 Unit -> 1 Gene (Variable)

            sub_lessons = []
            if units == 2:
                sub_lessons.append({"parity": 2})  # Both
            elif units == 3:
                sub_lessons.append({"parity": 2})  # Both
                sub_lessons.append({"parity": -1})  # Variable
            elif units == 1:
                sub_lessons.append({"parity": -1})  # Variable
            else:
                # Fallback for other units (e.g. 4 -> 2 Both)
                count = units // 2
                rem = units % 2
                for _ in range(count):
                    sub_lessons.append({"parity": 2})
                if rem:
                    sub_lessons.append({"parity": -1})

            for sl in sub_lessons:
                self.gene_metadata.append(
                    {
                        "lesson_id": lesson.id,
                        "course_id": lesson.course_id,
                        "teacher_id": lesson.teacher_id,
                        "group_id": lesson.group_id,
                    }
                )
                self.fixed_parities.append(sl["parity"])

                group_ids.append(lesson.group_id)
                course_ids.append(lesson.course_id)
                populations.append(group.population)
                req_room_types.append(course.required_room_type)
                allowed_days.append(g_allowed)
                self.valid_teachers_per_gene.append(valid_teacher_indices)

        self.num_genes = len(self.gene_metadata)
        self.fixed_parities = np.array(self.fixed_parities)

        # Maps
        self.timeslot_day_map = np.array([ts.day_of_week for ts in timeslots])

        # Compute daily index
        ts_daily_idx = np.zeros(len(timeslots), dtype=int)
        # Group by day
        day_groups = defaultdict(list)
        for i, ts in enumerate(timeslots):
            day_groups[ts.day_of_week].append((ts.start_time, i))

        for d in day_groups:
            day_groups[d].sort()  # Sort by start_time
            for rank, (st, idx) in enumerate(day_groups[d]):
                ts_daily_idx[idx] = rank

        self.timeslot_daily_idx_map = ts_daily_idx

        # Process Teacher Availability
        teacher_allowed_slots_by_index = {}
        # Map timeslot ID to index
        ts_id_to_idx = {ts.id: i for i, ts in enumerate(timeslots)}

        for teacher in teachers:
            # Check availability_links if loaded, or assume passed separately?
            # The SolverEngine receives `teachers` list.
            # We need to ensure `availability_links` are loaded on these teacher objects.
            # Or we can pass a separate map.
            # Assuming `teachers` have `availability_links` loaded.
            if hasattr(teacher, "availability_links") and teacher.availability_links:
                allowed_indices = []
                for link in teacher.availability_links:
                    if link.timeslot_id in ts_id_to_idx:
                        allowed_indices.append(ts_id_to_idx[link.timeslot_id])

                if allowed_indices:
                    t_idx = self.teacher_id_to_idx[teacher.id]
                    teacher_allowed_slots_by_index[t_idx] = allowed_indices
            # Fallback for old string format if still present (migration removed it but object might have it if not refreshed?)
            # No, migration removed it.

        # Precompute valid rooms for each gene
        self.valid_rooms_per_gene = []
        for i in range(self.num_genes):
            valid_rooms = []
            req_type = req_room_types[i]
            pop = populations[i]
            for r_idx, room in enumerate(classrooms):
                # Check Type (Strict equality as per constraint checker)
                if room.type == req_type and room.capacity >= pop:
                    valid_rooms.append(r_idx)

            self.valid_rooms_per_gene.append(valid_rooms)

        self.constraint_checker = ConstraintChecker(
            self.num_genes,
            np.array(group_ids),
            np.array(course_ids),
            np.array(populations),
            np.array(req_room_types),
            allowed_days,
            classrooms,
            self.timeslot_day_map,
            teacher_allowed_slots_by_index=teacher_allowed_slots_by_index,
        )

        self.fitness_calculator = FitnessCalculator(weights)
        self.operators = GeneticOperators(
            len(timeslots),
            len(classrooms),
            self.fixed_parities,
            self.valid_rooms_per_gene,
            self.valid_teachers_per_gene,
        )

    async def run(
        self,
        population_size: int = 100,
        generations: int = 1000,
        max_stagnant_generations: int = 150,
    ) -> tuple[List[Dict[str, Any]] | None, float]:
        population = Population(population_size, self.num_genes)
        population.init_population(
            len(self.timeslots),
            len(self.classrooms),
            self.fixed_parities,
            self.valid_rooms_per_gene,
            self.valid_teachers_per_gene,
        )

        best_genome = None
        best_cost = float("inf")
        stagnant_counter = 0

        for gen in range(generations):
            # Evaluate
            valid_genomes = []
            improved = False
            for genome in population.genomes:
                violations = self.constraint_checker.calculate_violations(genome.genes)

                soft_cost = self.fitness_calculator.calculate_cost(
                    genome.genes,
                    self.constraint_checker.lesson_group_ids,
                    self.timeslot_day_map,
                    self.timeslot_daily_idx_map,
                )

                genome.fitness = soft_cost + violations

                if violations == 0:
                    genome.is_valid = True
                    valid_genomes.append(genome)
                else:
                    genome.is_valid = False

                if genome.fitness < best_cost:
                    best_cost = genome.fitness
                    best_genome = genome
                    improved = True

            if improved:
                stagnant_counter = 0
            else:
                stagnant_counter += 1

            if stagnant_counter >= max_stagnant_generations:
                print(
                    f"Stopping early at generation {gen} due to stagnation ({max_stagnant_generations} gens without improvement)."
                )
                break

            # Selection (Tournament)
            new_genomes = []
            # Elitism: Keep best
            if best_genome:
                # Deep copy best genome to avoid mutation
                import copy

                new_genomes.append(copy.deepcopy(best_genome))

            while len(new_genomes) < population_size:
                # Select 2 parents
                p1 = self._tournament_select(population.genomes)
                p2 = self._tournament_select(population.genomes)

                # Crossover
                child = self.operators.crossover(p1, p2)

                # Mutation
                self.operators.mutate(child)

                new_genomes.append(child)

            population.genomes = new_genomes

            # Early stopping if perfect score (0)
            if best_cost == 0:
                break

            if gen % 10 == 0:
                print(f"Generation {gen}/{generations}: Best Cost = {best_cost}")

        if best_genome and best_genome.is_valid:
            # Calculate satisfaction percentage
            # Assuming max possible cost is roughly estimated or we normalize
            # For now, let's just return fitness.
            # We can add a method to calculate satisfaction based on soft constraints violations count vs total constraints.

            # Let's assume we can get detailed breakdown from fitness calculator if we run it one last time
            # cost, breakdown = self.fitness_calculator.calculate(best_genome, detailed=True)

            # For now, just return results and cost
            return self._build_result(best_genome), best_cost
        return None, best_cost

    def _tournament_select(self, genomes: List[Genome], k: int = 3) -> Genome:
        selected = np.random.choice(genomes, k)
        # Sort by fitness (lower is better)
        selected = sorted(selected, key=lambda g: g.fitness)
        return selected[0]

    def _build_result(self, genome: Genome) -> List[Dict[str, Any]]:
        results = []
        for i, gene in enumerate(genome.genes):
            ts_idx = gene[0]
            room_idx = gene[1]
            parity = gene[2]  # 0, 1, 2
            teacher_idx = gene[3]

            meta = self.gene_metadata[i]

            # Map parity int to Enum string
            parity_str = "both"
            if parity == 0:
                parity_str = "odd"
            elif parity == 1:
                parity_str = "even"

            teacher_id = self.teacher_idx_to_id.get(teacher_idx)

            results.append(
                {
                    "lesson_id": meta["lesson_id"],
                    "timeslot_id": self.timeslots[ts_idx].id,
                    "room_id": self.classrooms[room_idx].id,
                    "week_parity": parity_str,
                    "teacher_id": teacher_id,
                }
            )
        return results
