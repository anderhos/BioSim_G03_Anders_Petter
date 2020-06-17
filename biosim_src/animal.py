# -*- coding: utf-8 -*-

__author__ = "Anders Mølmen Høst & Petter Kolstad Hetland"
__email__ = "anders.molmen.host@nmbu.no, petter.storesund.hetland@nmbu.no"

import random as random
from math import e
import numpy as np


class Animal:
    """Super class for Herbivores and Carnivores.

    """

    def __init__(self, weight, age):
        """Initialize the animal class

        :param weight: Weight of animal
        :type weight: float
        :param age: Age of animal
        :type age: int
        """
        if weight is None:
            self._weight = self.birth_weight
        else:
            self._weight = float(weight)
        self._age = age

        self._species = self.__class__.__name__
        self._death_prob = None
        self.has_moved = False

    @classmethod
    def set_params(cls, new_params):
        """Set parameter for animal classes.

        :param new_params: dict
        """
        for key in new_params:
            if key not in cls.p:
                raise KeyError("Invalid key name: " + key)

        for key in cls.p:
            if key in new_params:
                if new_params[key] < 0:
                    raise ValueError("Parameter must be positive")
                cls.p.update(new_params)

    @classmethod
    def get_params(cls):
        """
        Getter function for the set parameter method

        :return dictionary with parameters
        :r_type: dict
        """
        return cls.p

    def __repr__(self):
        """Format for string representation
        """
        return "{}({} years, {:.3} kg)".format(self._species, self._age, self._weight)

    def __str__(self):
        """Format for better readability
        """
        return "{}({} years, {:.3} kg)".format(self._species, self._age, self._weight)

    @classmethod
    def from_dict(cls, animal_dict):
        """Allows the sim to add instances directly from dictionaries when adding pop

        :param animal_dict: Dict with format {'species': 'Herbivore', 'age': 5, 'weight': 20}
        :type animal_dict: dict
        """
        class_weight = animal_dict["weight"]
        class_age = animal_dict["age"]
        return cls(age=class_age, weight=class_weight)

    @property
    def weight(self):
        """
        :return: Weight of animal
        :r_type: float
        """
        return self._weight

    @weight.setter
    def weight(self, weight):
        """Setter method. Set the animal weight."""
        self._weight = weight

    @property
    def age(self):
        """
        :return: Age of animal
        :r_type: int
        """
        return self._age

    @age.setter
    def age(self, age):
        """Setter method. Set the animal age."""
        self._age = age

    @property
    def species(self):
        """
        :return: Specie of animal
        :r_type: str
        """
        return self._species

    def aging(self):
        """Increments age by one every season

        """
        self.age += 1

    def give_birth(self, n_same):
        """Animals give birth based on fitness and same-type animals in cell

        :param n_same: number of same-type animals
        :type n_same: int
        :return: True or False
        :rtype: bool
        """
        birth_prob = self.p["gamma"] * self.fitness * (n_same - 1)
        if self.weight < self.p["zeta"] * (self.p["w_birth"] + self.p["sigma_birth"]):
            return False, None  # Return false if weight of mother is less than birth
        elif birth_prob >= 1:
            give_birth = True
        elif 0 < birth_prob < 1:
            give_birth = True if random.random() < birth_prob else False
        else:
            give_birth = False

        if give_birth:  # If give_birth is true
            birth_weight = self.birth_weight
            if birth_weight < self.weight:
                self.weight -= self.p["xi"] * birth_weight
                return True, birth_weight
            else:
                return False, None
        else:
            return False, None

    def migrate(self):
        """Method deciding whether animal will migrate

        :rtype: bool
        """
        move_prob = self.p["mu"] * self.fitness
        if random.random() < move_prob:
            return True
        else:
            return False

    def lose_weight(self):
        """Animals lose weight based on parameter eta

        :param eta: from dictionary p of parameters
        """
        self.weight -= self.weight * self.p["eta"]

    def death(self):
        """Return true when called if the animal is to be removed from the simulation
        and false otherwise.

        :param omega: from dictionary of parameters
        :param _death_prob: the probability that the animal dies
        :rtype: bool
        """
        if self.weight <= 0:
            death = True
        else:
            self._death_prob = self.p["omega"] * (1 - self.fitness)

            death = True if random.random() < self._death_prob else False

        return death

    @staticmethod
    def q(sgn, x, x_half, phi):
        """
        :param sgn: Sign, positive/negative
        :param x, x_half, phi: see fitness function
        """
        return 1.0 / (1.0 + e ** (sgn * phi * (x - x_half)))

    @property
    def fitness(self):
        """
        Function returning the fitness of an animal.

        :return: a value between 0 and 1
        :r_type: int

        """
        return self.q(+1, self.age, self.p["a_half"], self.p["phi_age"]) * self.q(
            -1, self.weight, self.p["w_half"], self.p["phi_weight"]
        )

    @property
    def birth_weight(self):
        """
        Birth weight of newborn animal is drawn randomly

        param: w_birth: birth weight of animal
        param: sigma_birth: standard deviation
        param: N: Population size
        return: birth_weight, drawn from gaussian distribution
        r_type: float

        """
        birth_weight = random.gauss(self.p["w_birth"], self.p["sigma_birth"])
        return birth_weight


class Herbivore(Animal):

    # Dictionary of parameters belonging to the Herbivore class
    p = {
        "w_birth": 8.0,
        "sigma_birth": 1.5,
        "beta": 0.9,
        "eta": 0.05,
        "a_half": 40.0,
        "phi_age": 0.6,
        "w_half": 10.0,
        "phi_weight": 0.1,
        "mu": 0.25,
        "gamma": 0.2,
        "zeta": 3.5,
        "xi": 1.2,
        "omega": 0.4,
        "F": 10.0,
    }

    def __init__(self, weight=None, age=0):
        super().__init__(weight, age)

    def eat_fodder(self, cell):
        """
        When an animal eats, its weight increases

        :param: F: the amount of fodder a herbivore can eat
        :param: beta: a factor to which weight is increased
        """
        consumption_amount = self.p["F"]  # Calculate amount of fodder consumed
        if consumption_amount <= cell.fodder:
            self.weight += self.p["beta"] * consumption_amount  # Eat fodder
            cell.fodder -= consumption_amount  # Removes consumed fodder from cell object

        elif consumption_amount > cell.fodder > 0:
            self.weight += self.p["beta"] * cell.fodder  # Eat fodder
            cell.fodder = 0  # Sets fodder to zero.


class Carnivore(Animal):
    """
    Carnivore class
    """
    # Dictionary containing default parameter values for Carnivore class
    p = {
        "w_birth": 6.0,
        "sigma_birth": 1.0,
        "beta": 0.75,
        "eta": 0.125,
        "a_half": 40.0,
        "phi_age": 0.3,
        "w_half": 4.0,
        "phi_weight": 0.4,
        "mu": 0.4,
        "gamma": 0.8,
        "zeta": 3.5,
        "xi": 1.1,
        "omega": 0.8,
        "F": 50.0,
        "DeltaPhiMax": 10.0,
    }

    def __init__(self, weight=None, age=0):
        super().__init__(weight, age)

    def kill_prey(self, sorted_herbivores):
        """Iterates through sorted herbivores and eats until F is met

        :param sorted_herbivores: Herbivores sorted by fitness levels from low to high
        :type sorted_herbivores: list
            ...
        :return: Animals killed by herbivore to be removed from simulation
        :rtype: list
        """
        consumption_weight = 0
        herbs_killed = []
        fitness = self.fitness

        for herb in sorted_herbivores:
            if consumption_weight < self.p["F"]:
                fitness_diff = fitness - herb.fitness
                if fitness_diff <= 0:
                    kill_prey = False

                elif 0 < fitness_diff < self.p["DeltaPhiMax"]:
                    kill_prob = fitness_diff / self.p["DeltaPhiMax"]
                    kill_prey = True if random.random() <= kill_prob else False

                else:
                    kill_prey = True

                if kill_prey:  # If the herb is killed
                    consumption_weight += (
                        herb.weight
                    )  # Add herb weight to consumption_weight variable
                    herbs_killed.append(herb)
            else:
                continue

        if consumption_weight > self.p["F"]:  # Auto-adjust consumption_weight to be <= F-parameter
            consumption_weight = self.p["F"]

        self.weight += consumption_weight * self.p["beta"]  # Add weight to carnivore

        return herbs_killed
