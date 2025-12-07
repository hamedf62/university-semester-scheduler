import numpy as np
from app.solver.genome import Genome


class GeneticOperators:
    def __init__(self, num_timeslots: int, num_classrooms: int):
        self.num_timeslots = num_timeslots
        self.num_classrooms = num_classrooms

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
            genome.genes[mask, 1] = np.random.randint(
                0, self.num_classrooms, size=num_mutations
            )

    def crossover(self, parent1: Genome, parent2: Genome) -> Genome:
        # Uniform Crossover
        child = Genome(parent1.genes.shape[0])
        mask = np.random.random(parent1.genes.shape[0]) < 0.5

        child.genes[mask] = parent1.genes[mask]
        child.genes[~mask] = parent2.genes[~mask]

        return child
