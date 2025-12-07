import numpy as np
from app.solver.genome import Genome
from typing import List


class GeneticOperators:
    def __init__(
        self,
        num_timeslots: int,
        num_classrooms: int,
        fixed_parities: np.ndarray = None,
        valid_rooms_per_gene: List[List[int]] = None,
        valid_teachers_per_gene: List[List[int]] = None,
    ):
        self.num_timeslots = num_timeslots
        self.num_classrooms = num_classrooms
        self.fixed_parities = fixed_parities
        self.valid_rooms_per_gene = valid_rooms_per_gene
        self.valid_teachers_per_gene = valid_teachers_per_gene

    def mutate(self, genome: Genome, mutation_rate: float = 0.01):
        # Randomly change genes
        mask = np.random.random(genome.genes.shape[0]) < mutation_rate
        num_mutations = np.sum(mask)

        if num_mutations > 0:
            # Mutate timeslots
            genome.genes[mask, 0] = np.random.randint(
                0, self.num_timeslots, size=num_mutations
            )
            # Mutate rooms
            if self.valid_rooms_per_gene:
                mutated_indices = np.where(mask)[0]
                for idx in mutated_indices:
                    valid_rooms = self.valid_rooms_per_gene[idx]
                    if valid_rooms:
                        genome.genes[idx, 1] = np.random.choice(valid_rooms)
                    else:
                        genome.genes[idx, 1] = np.random.randint(0, self.num_classrooms)
            else:
                genome.genes[mask, 1] = np.random.randint(
                    0, self.num_classrooms, size=num_mutations
                )

            # Mutate Parity
            if self.fixed_parities is not None:
                variable_mask = self.fixed_parities == -1
                mutation_mask = mask & variable_mask
                num_parity_mutations = np.sum(mutation_mask)
                if num_parity_mutations > 0:
                    genome.genes[mutation_mask, 2] = np.random.randint(
                        0, 2, size=num_parity_mutations
                    )

            # Mutate Teachers
            if self.valid_teachers_per_gene:
                mutated_indices = np.where(mask)[0]
                for idx in mutated_indices:
                    valid_teachers = self.valid_teachers_per_gene[idx]
                    if valid_teachers:
                        genome.genes[idx, 3] = np.random.choice(valid_teachers)
                    else:
                        # Should not happen
                        genome.genes[idx, 3] = 0

    def crossover(self, parent1: Genome, parent2: Genome) -> Genome:
        # Uniform Crossover
        child = Genome(parent1.genes.shape[0])
        mask = np.random.random(parent1.genes.shape[0]) < 0.5

        child.genes[mask] = parent1.genes[mask]
        child.genes[~mask] = parent2.genes[~mask]

        return child
