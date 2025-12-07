import asyncio
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
    TimeSlot,
)
from app.solver.genome import Population
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

        self.constraint_checker = ConstraintChecker(
            lessons,
            classrooms,
            courses,
            teachers,
            groups,
            teacher_course_links,
            teacher_entrance_links,
        )
        self.fitness_calculator = FitnessCalculator(weights)
        self.operators = GeneticOperators(len(timeslots), len(classrooms))

        # Precompute timeslot day map
        # Assuming timeslot IDs are sequential or we map them
        # For simplicity, let's assume timeslot list index corresponds to ID-1
        self.timeslot_day_map = np.array([ts.day_of_week for ts in timeslots])

    async def run(self, population_size: int = 100, generations: int = 1000) -> Dict:
        population = Population(population_size, len(self.lessons))
        population.init_population(len(self.timeslots), len(self.classrooms))

        best_genome = None
        best_cost = float("inf")

        for gen in range(generations):
            # Evaluate
            valid_genomes = []
            for genome in population.genomes:
                if self.constraint_checker.check_hard_constraints(genome.genes):
                    genome.is_valid = True
                    genome.fitness = self.fitness_calculator.calculate_cost(
                        genome.genes,
                        self.constraint_checker.lesson_teacher_ids,
                        self.constraint_checker.lesson_group_ids,
                        self.timeslot_day_map,
                    )
                    valid_genomes.append(genome)

                    if genome.fitness < best_cost:
                        best_cost = genome.fitness
                        best_genome = genome
                else:
                    genome.is_valid = False
                    genome.fitness = float("inf")  # Penalize invalid

            # Selection (Tournament)
            new_genomes = []
            # Elitism: Keep best
            if best_genome:
                new_genomes.append(best_genome)  # Need deep copy ideally

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

            if gen % 10 == 0:
                print(f"Generation {gen}: Best Cost = {best_cost}")

        return self._format_result(best_genome)

    def _tournament_select(self, genomes: List, k: int = 3):
        candidates = [genomes[i] for i in np.random.randint(0, len(genomes), k)]
        # Sort by fitness (lower cost is better)
        candidates.sort(key=lambda x: x.fitness)
        return candidates[0]

    def _format_result(self, genome):
        if not genome:
            return None

        results = []
        for i, gene in enumerate(genome.genes):
            results.append(
                {
                    "lesson_id": self.lessons[i].id,
                    "timeslot_id": self.timeslots[gene[0]].id,
                    "room_id": self.classrooms[gene[1]].id,
                }
            )
        return results
