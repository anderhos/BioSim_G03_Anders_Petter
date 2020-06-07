# -*- coding: utf-8 -*-

"""
A basic interface file containing the minimum requirements for running a simulation
with one animal in one cell.
"""

from src.biosim.animal import Herbivore, Carnivore, Animal
from src.biosim.landscape import Lowland

import textwrap

import numpy as np
import random as random
import operator
import matplotlib.pyplot as plt


class Simulation:

    def __init__(self, seed=1234, randomize_animals=True):
        self.cell = Lowland(f_max=700)
        self.animals = []
        self.year = 0
        random.seed(seed)
        self.randomize_animals = randomize_animals

        for _ in range(50):  # Add animals
            self.animals.append(Herbivore(age=5, weight=20))
        for _ in range(0):  # Add animals
            self.animals.append(Carnivore(age=0, weight=20))

    def randomize(self):
        """
        Defining a function to randomize animals
        """
        random.shuffle(self.animals)

    def run_year_cycle(self):
        """
        Runs through each of the 6 yearly seasons for all cells
        """
        #  1. Feeding
        self.cell.fodder = self.cell.f_max
        # Randomize animals before feeding
        if self.randomize_animals:
            self.randomize()

        for herb in self.herbivore_list:  # Herbivores eat first
            if self.cell.fodder != 0:
                herb.eat_fodder(self.cell)

        for carn in self.carnivore_list:  # Carnivores eat last
            herbs_killed = carn.kill_prey(self.sorted_herbivores)  # Carnivore hunts for herbivores
            for herb in herbs_killed:
                self.animals.remove(herb)

        #  2. Procreation
        for herb in self.herbivore_list:  # Herbivores give birth
            give_birth, birth_weight = herb.give_birth(self.herb_count)

            if give_birth:
                self.animals.append(Herbivore(weight=birth_weight, age=0))

        for carn in self.carnivore_list:  # Carnivores give birth
            give_birth, birth_weight = carn.give_birth(self.carn_count)

            if give_birth:
                self.animals.append(Carnivore(weight=birth_weight, age=0))


        #  3. Migration

        #  4. Aging
        for animal in self.animals:
            animal.aging()

        #  5. Loss of weight
        for animal in self.animals:
            animal.lose_weight()

        #  6. Death
        dead_animals = []
        for animal in self.animals:
            if animal.death():
                dead_animals.append(animal)

        for animal in dead_animals:
            self.animals.remove(animal)

        self.year += 1  # Add year to simulation

    def run_simulation(self, num_years):
        """
        :param num_years: number of years to simulate
        """
        y_herb = [self.herb_count]
        y_carn = [self.carn_count]

        ax, herb_line, carn_line = self.init_plot(y_herb, y_carn, num_years)

        for year in range(num_years):
            self.run_year_cycle()

            y_herb.append(self.herb_count)
            y_carn.append(self.carn_count)
            print(self.animal_count)
            self.update_plot(y_herb, y_carn, ax, herb_line, carn_line)

        print('Simulation complete.')

    def init_plot(self, y_herb, y_carn, num_years):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        herb_line, = ax.plot(y_herb)
        carn_line, = ax.plot(y_carn)
        ax.legend(['Herbivore count', 'Carnivore count'])
        ax.set_xlabel('Simulation year')
        ax.set_ylabel('Animal count')
        ax.set_ylim([0, self.animal_count])
        ax.set_xlim([0, num_years])

        plt.ion()

        return ax, herb_line, carn_line

    @staticmethod
    def update_plot(y_herb, y_carn, ax, herb_line, carn_line):
        if max(y_herb) >= max(y_carn):
            ax.set_ylim([0, max(y_herb) + 20])
        else:
            ax.set_ylim([0, max(y_carn) + 20])

        herb_line.set_ydata(y_herb)
        herb_line.set_xdata(range(len(y_herb)))
        carn_line.set_ydata(y_carn)
        carn_line.set_xdata(range(len(y_carn)))

        plt.pause(0.05)

    @property
    def animal_count(self):
        return len(self.animals)

    @property
    def herb_count(self):
        return len(self.herbivore_list)

    @property
    def carn_count(self):
        return len(self.carnivore_list)

    @property
    def herbivore_list(self):
        return [animal for animal in self.animals if animal.__class__.__name__ == 'Herbivore']

    @property
    def carnivore_list(self):
        return [animal for animal in self.animals if animal.__class__.__name__ == 'Carnivore']

    @property
    def sorted_carnivores(self):  # Will probably be moved to landscape classes
        fitness_dict = dict([
            (animal, animal.fitness) for animal in self.carnivore_list
        ])
        sorted_carn_list = [
            pair[0] for pair in sorted(fitness_dict.items(),
                                       key=operator.itemgetter(1),
                                       reverse=True)
        ]
        return sorted_carn_list

    @property
    def sorted_herbivores(self):  # Will probably be moved to landscape classes
        fitness_dict = dict([
            (animal, animal.fitness) for animal in self.herbivore_list
        ])
        sorted_herb_list = [
            pair[0] for pair in sorted(fitness_dict.items(),
                                       key=operator.itemgetter(1),
                                       reverse=False)
        ]
        return sorted_herb_list


if __name__ == '__main__':

    sim = Simulation()  # Create simple simulation instance

    sim.run_simulation(num_years=200)

    print([herb.fitness for herb in sim.sorted_herbivores])
    print([carn.fitness for carn in sim.sorted_carnivores])

    # for animal in sim.animals:
    #     print(animal.birth_weight())
