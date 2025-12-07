import numpy as np
from typing import List, Dict, Tuple
from app.models import Lesson, TimeSlot, Classroom


class Genome:
    def __init__(self, num_genes: int):
        # Genome representation:
        # Array of shape (num_genes, 4)
        # Column 0: TimeSlot Index
        # Column 1: Classroom Index
        # Column 2: Parity (0=ODD, 1=EVEN, 2=BOTH)
        # Column 3: Teacher Index
        self.genes = np.zeros((num_genes, 4), dtype=int)
        self.fitness = 0.0
        self.is_valid = False

    def random_init(
        self,
        num_timeslots: int,
        num_classrooms: int,
        fixed_parities: np.ndarray = None,
        valid_rooms_per_gene: List[List[int]] = None,
        valid_teachers_per_gene: List[List[int]] = None,
    ):
        # Random TimeSlots
        self.genes[:, 0] = np.random.randint(0, num_timeslots, size=self.genes.shape[0])

        # Random Classrooms
        if valid_rooms_per_gene:
            for i in range(self.genes.shape[0]):
                valid_rooms = valid_rooms_per_gene[i]
                if valid_rooms:
                    self.genes[i, 1] = np.random.choice(valid_rooms)
                else:
                    self.genes[i, 1] = np.random.randint(0, num_classrooms)
        else:
            self.genes[:, 1] = np.random.randint(
                0, num_classrooms, size=self.genes.shape[0]
            )

        # Parity
        if fixed_parities is not None:
            variable_mask = fixed_parities == -1
            self.genes[~variable_mask, 2] = fixed_parities[~variable_mask]
            self.genes[variable_mask, 2] = np.random.randint(
                0, 2, size=np.sum(variable_mask)
            )
        else:
            self.genes[:, 2] = 2

        # Random Teachers
        if valid_teachers_per_gene:
            for i in range(self.genes.shape[0]):
                valid_teachers = valid_teachers_per_gene[i]
                if valid_teachers:
                    self.genes[i, 3] = np.random.choice(valid_teachers)
                else:
                    # Should not happen if data is valid
                    self.genes[i, 3] = 0


class Population:
    def __init__(self, size: int, num_genes: int):
        self.genomes = [Genome(num_genes) for _ in range(size)]

    def init_population(
        self,
        num_timeslots: int,
        num_classrooms: int,
        fixed_parities: np.ndarray = None,
        valid_rooms_per_gene: List[List[int]] = None,
        valid_teachers_per_gene: List[List[int]] = None,
    ):
        for genome in self.genomes:
            genome.random_init(
                num_timeslots,
                num_classrooms,
                fixed_parities,
                valid_rooms_per_gene,
                valid_teachers_per_gene,
            )
