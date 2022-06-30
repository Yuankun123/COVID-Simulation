import time
import random
import numpy as np
from typing import Optional

from tools import unit_vector, norm
from vcity import Vcity, CityCtor, Element, Road, Building, ResidentialBd, BusinessBd, Square, GeoPart

NORMAL = 'normal'
INFECTED = 'infected'
TIME_CONSTANT = 360  # 1 hours contains 360 time units


class IElement(Element):
    """Elements that interact with people"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.normal_individuals: list[Individual] = []
        self.infected_individuals: list[Individual] = []

    def add_individual(self, indiv: 'Individual'):
        if indiv.infected_state == NORMAL:
            self.normal_individuals.append(indiv)
        else:
            self.infected_individuals.append(indiv)

    def remove_individual(self, indiv: 'Individual'):
        if indiv.infected_state == NORMAL:
            self.normal_individuals.remove(indiv)
        else:
            self.infected_individuals.remove(indiv)


class IRoad(IElement, Road):
    cls_abbrev = 'IRd'


class IBuilding(IElement, Building):
    cls_abbrev = 'IBd'
    curr_attract: float

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.curr_attract = cls.avg_attract(0)

    @staticmethod
    def avg_attract(current_time) -> float:
        raise NotImplementedError

    @classmethod
    def update_attract(cls, current_time):
        cls.curr_attract = cls.avg_attract(current_time)


class IResidentialBd(IBuilding, ResidentialBd):
    cls_abbrev = 'IRBd'

    @staticmethod
    def avg_attract(current_time) -> float:
        return 1


# currently not used
class IBusinessBd(IBuilding, BusinessBd):
    cls_abbrev = 'IBBd'

    @staticmethod
    def avg_attract(current_time) -> float:
        return 1


class ISquare(IBuilding, Square):
    cls_abbrev = 'ISqr'

    @staticmethod
    def avg_attract(current_time) -> float:
        if 11 * TIME_CONSTANT <= current_time < 13 * TIME_CONSTANT:
            return 0.1
        else:
            return 10


ctor = CityCtor()
ctor.configure(road=IRoad, rbd=IResidentialBd, bbd=IBusinessBd, sqr=ISquare)


class Individual:
    index = 0

    def __init__(self, home: IResidentialBd, sim: 'Simulation', infected=False):
        if infected:
            self.infected_state = INFECTED
        else:
            self.infected_state = NORMAL

        self.index = Individual.index
        Individual.index += 1

        self.home = home
        self.pos = home.rand_location()
        self.imagined_current_region: IElement = home  # the location that instructs the individual to move
        self.current_region = home
        home.add_individual(self)

        self.sim = sim
        self.target: Optional[IBuilding] = None
        self.target_port = None  # temperate protocol
        self.target_pos: Optional[np.ndarray] = None  # a specific position in target region

    def generate_target(self) -> IBuilding:
        candidates: list[IBuilding] = [region for region in self.sim.sqrs] + [self.home]
        # TODO the possibility should be computed for each type of building
        weights = [candidate.curr_attract for candidate in candidates]
        while (res := random.choices(candidates, weights=weights)[0]) == self.current_region:
            pass
        return res

    def drift(self):
        self.pos += np.array([self.sim.random_nums[self.index], self.sim.random_nums[-self.index]])
        while self.pos not in self.current_region:
            self.pos += unit_vector(self.current_region.cntr - self.pos) * self.sim.step_length

    def move(self):
        if self.target is None:
            while self.pos not in self.current_region:
                self.pos += unit_vector(self.current_region.cntr - self.pos) * self.sim.step_length
            self.target = self.generate_target()
            self.target_pos = self.target.rand_location()
            # print('New Target Address:', self.target.address)

            self.target_port = self.current_region.find_port(self.target)
            self.imagined_current_region = self.target_port.master
            assert isinstance(self.target_port, GeoPart)
            assert isinstance(self.imagined_current_region, IElement)

            # print('Next Port:', self.target_port)
            # print('Port Position', self.target_port.pos)

        # move
        if self.pos not in self.imagined_current_region:
            direction = unit_vector(self.target_port.pos - self.pos)
            step = np.round_(direction * self.sim.step_length, decimals=0)
            self.pos += step
            # print('step:', step)

        if self.pos in self.target:
            if self.imagined_current_region != self.target:
                print((f'Current:{self.current_region}',
                       f'Imagined:{self.imagined_current_region}',
                       f'Target:{self.target}',
                       f'Target protocol: {self.target_port}',
                       f'Pos:{self.pos}'))
                raise RuntimeError
            if norm(self.pos - self.target_pos) > self.sim.step_length / 2:
                direction = unit_vector(self.target_pos - self.pos)
                step = np.round_(direction * self.sim.step_length, decimals=0)
                self.pos += step
                # print('step:', step)
                return
            else:
                self.current_region.remove_individual(self)
                self.imagined_current_region.add_individual(self)
                self.current_region = self.imagined_current_region
                self.target = None
                self.target_pos = None
                return 'arrived'

        if self.pos in self.imagined_current_region:
            self.current_region.remove_individual(self)
            self.imagined_current_region.add_individual(self)
            self.current_region = self.imagined_current_region

            self.target_port = self.current_region.find_port(self.target)
            self.imagined_current_region = self.target_port.master
            assert isinstance(self.target_port, GeoPart)
            assert isinstance(self.imagined_current_region, IElement)

            # print('Next Port:', self.target_port)
            # print('Port Position', self.target_port.pos)

        # print('Current Address:', self.current_region.address)
        # print('Self Position', self.pos)


class Crowd:
    def __init__(self, population: int, initial_infected: int, step_length, drift_sigma, transport_activity):
        self.initial_infected = initial_infected
        self.population = population
        self.step_length = step_length
        self.drift_sigma = drift_sigma
        self.transport_activity = transport_activity

        self.normal_individuals: list[Individual] = []
        self.infected_individuals: list[Individual] = []
        self.transporting_individuals: list[Individual] = []
        self.drifting_individuals: list[Individual] = []

        self.random_nums = []
        for _ in range(2 * population):
            random.seed(time.perf_counter())
            self.random_nums.append(random.gauss(0, 3))

    @property
    def individuals(self):
        return self.normal_individuals + self.infected_individuals

    def move_all(self, current_time):
        for individual in self.drifting_individuals:
            individual.drift()

        transport_num = int(self.transport_activity(current_time) * self.population)
        while len(self.transporting_individuals) < transport_num - len(self.transporting_individuals):
            random.seed(random.seed(time.perf_counter()))
            new_indiv = random.choice(self.drifting_individuals)
            self.transporting_individuals.append(new_indiv)
            self.drifting_individuals.remove(new_indiv)

        for i, individual in reversed(list(enumerate(self.transporting_individuals))):
            if individual.move() == 'arrived':
                self.transporting_individuals.pop(i)
                self.drifting_individuals.append(individual)
            else:
                assert individual.target_pos is not None


class Simulation(Vcity, Crowd):
    def __init__(self,
                 time_period: tuple,  # period of time in a day that we simulate (in unit)
                 population: int,  # population of this simulation
                 initial_infected: int,  # number of initially infected individuals
                 step_length: float,  # distance traveled per time unit
                 drift_sigma: float,  # stdev for drifting
                 transport_activity,  # percent of population transporting among regions in a given time unit (func)
                 infection_radius: float,
                 risk: float,
                 ):
        self.current_time = 0
        self.current_day = 0
        self.time_period = time_period
        super().__init__(population=population,
                         initial_infected=initial_infected,
                         step_length=step_length,
                         drift_sigma=drift_sigma,
                         transport_activity=transport_activity)
        self.initiate_individuals()

    def initiate_individuals(self):
        for _ in range(self.population - self.initial_infected):
            self.normal_individuals.append(Individual(random.choice(self.rbds), self))
        for _ in range(self.initial_infected):
            self.infected_individuals.append(Individual(random.choice(self.rbds), self, True))
        self.drifting_individuals = self.individuals

    def progress(self):
        if self.current_time not in range(*self.time_period):
            self.current_time = self.time_period[0]
            self.current_day += 1
        else:
            self.current_time += 1

        # update attractiveness
        IResidentialBd.update_attract(self.current_time)
        ISquare.update_attract(self.current_time)

        # move
        self.move_all(self.current_time)
        # update infection state
        '''for region in self.regions:
            region.update_infected(self)'''

    def print_progress_info(self):
        if self.current_time % TIME_CONSTANT == 0:
            print(f'\nDay{self.current_day} {self.current_time // TIME_CONSTANT}:00')
        print(f'\r{len(self.infected_individuals)}', end='')
