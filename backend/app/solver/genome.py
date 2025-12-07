import numpy as np
from typing import List, Dict, Tuple
from app.models import Lesson, TimeSlot, Classroom


class Genome:
    def __init__(self, num_lessons: int):
        # Genome representation:
        # Two arrays of length num_lessons
        # 0: TimeSlot Index
        # 1: Classroom Index
        self.genes = np.zeros((num_lessons, 2), dtype=int)
        self.fitness = 0.0
        self.is_valid = False

    def random_init(self, num_timeslots: int, num_classrooms: int):
        self.genes[:, 0] = np.random.randint(0, num_timeslots, size=self.genes.shape[0])
        self.genes[:, 1] = np.random.randint(
            0, num_classrooms, size=self.genes.shape[0]
        )


class Population:
    def __init__(self, size: int, num_lessons: int):
        self.genomes = [Genome(num_lessons) for _ in range(size)]

    def init_population(self, num_timeslots: int, num_classrooms: int):
        for genome in self.genomes:
            genome.random_init(num_timeslots, num_classrooms)
