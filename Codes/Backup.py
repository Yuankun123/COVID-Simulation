'''class GeoRegion(AbstractRegion):

    """Every region is a parallelogram"""

    def __init__(self, name: str,
                 vcity: 'VirtualCity',
                 anchor1: np.ndarray,
                 extend_len: int,
                 extend_dir='horizontal',
                 anchor_mode='corner',
                 anchor2: np.ndarray = None,
                 targetable=True):
        """
        :param name: name of the region
        :param vcity: virtual city the region belongs to
        :param anchor1: anchor1 position
        :param extend_len: extend length
        :param extend_dir: horizontal or vertical
        :param anchor_mode: anchor's position related to the region, 'corner' or 'edge'
        :param anchor2: anchor2 position
        :param targetable: whether this region can become a target of transportation
        """
        super().__init__(name, targetable)
        self.vcity = vcity

        # configure the parallelogram region
        assert anchor_mode in ['corner', 'edge'], f'Bad parameter {anchor_mode} for anchor_mode'
        assert extend_dir in ['horizontal', 'vertical'], f'Bad parameter {extend_dir} for extend_dir'
        assert anchor1[0] <= anchor2[0] and anchor1[1] <= anchor2[1], f'{anchor1} is not on the lower left of {anchor2}'
        assert extend_len % 2 == 0, f'Extend length should be a even number'

        if anchor_mode == 'edge':
            if extend_dir == 'horizontal':
                sw_corner = anchor1 - np.array([extend_len / 2, 0])
            else:
                sw_corner = anchor1 - np.array([0, extend_len / 2])
        else:
            sw_corner = anchor1
        self.extend_dir = extend_dir
        self.extend_len = extend_len

        if extend_dir == 'horizontal':
            assert anchor2[1] != anchor1[1], 'Cannot extend horizontally because the anchors have the same y'
            self.main_dir_span = Span(anchor1[1], anchor2[1])
            ratio = (anchor2[0] - anchor1[0]) / self.main_dir_span.span
            self.get_subdir_span = lambda y: Span((y - sw_corner[1]) * ratio + sw_corner[0],
                                                  (y - sw_corner[1]) * ratio + sw_corner[0] + self.extend_len)
            main_cntr = self.main_dir_span.cntr
            self.cntr = np.array(self.get_subdir_span(main_cntr).cntr, main_cntr)
        else:
            assert anchor2[0] != anchor1[0], 'Cannot extend vertically because the anchors have the same x'
            self.main_dir_span = Span(anchor1[0], anchor2[0])
            ratio = (anchor2[1] - anchor1[1]) / self.main_dir_span.span
            self.get_subdir_span = lambda x: Span((x - sw_corner[0]) * ratio + sw_corner[1],
                                                  (x - sw_corner[0]) * ratio + sw_corner[1] + self.extend_len)
            main_cntr = self.main_dir_span.cntr
            self.cntr = np.array(main_cntr, self.get_subdir_span(main_cntr).cntr)

    def __contains__(self, pos: np.ndarray):
        if self.extend_dir == 'horizontal':
            if pos[1] in self.main_dir_span and pos[0] in self.get_subdir_span(pos[1]):
                return True
            else:
                return False
        else:
            if pos[0] in self.main_dir_span and pos[1] in self.get_subdir_span(pos[0]):
                return True
            else:
                return False

    def adjacent(self, pos: np.ndarray):
        """include both ends"""
        if self.extend_dir == 'horizontal':
            if self.main_dir_span.adjacent(pos[1]) and self.get_subdir_span(pos[1]).adjacent(pos[0]):
                return True
            else:
                return False
        else:
            if self.main_dir_span.adjacent(pos[0]) and self.get_subdir_span(pos[0]).adjacent(pos[1]):
                return True
            else:
                return False

    def rand_location(self) -> np.ndarray:
        main_sigma = self.main_dir_span.span / 6
        main_mu = self.main_dir_span.cntr
        random.seed(time.perf_counter())
        main_val = random.gauss(main_mu, main_sigma)
        while main_val not in self.main_dir_span:
            main_val = random.gauss(main_mu, main_sigma)

        current_sub_span = self.get_subdir_span(main_val)
        sub_sigma = current_sub_span.span / 6
        sub_mu = current_sub_span.cntr
        random.seed(time.perf_counter())
        sub_val = random.gauss(sub_mu, sub_sigma)
        while sub_val not in current_sub_span:
            sub_val = random.gauss(sub_mu, sub_sigma)

        if self.extend_dir == 'horizontal':
            return np.array(sub_val, main_val)
        else:
            return np.array(main_val, sub_val)'''

import random
import time
import threading
import numpy as np
from tools import norm, Span
from vcity import AbstractRegion, AbstractProtocol

NORMAL = 'normal'
INFECTED = 'infected'
TIME_CONSTANT = 360  # 1 hours contains 360 time units


class Protocol(AbstractProtocol):
    def __init__(self, region1, region2, pos):
        super().__init__(region1, region2)
        self.pos = pos


class Region(AbstractRegion):
    @staticmethod
    def pale_attractiveness(current_time):
        return 0

    """Every region is a parallelogram"""

    def __init__(self, region_name: str,
                 vcity: 'VirtualCity',
                 anchor1: np.ndarray,
                 extend_len: int,
                 extend_dir='horizontal',
                 anchor_mode='corner',
                 anchor2: np.ndarray = None,
                 targetable=True,
                 attract_func=None):
        """
        :param region_name: name of the region
        :param vcity: virtual city the region belongs to
        :param anchor1: anchor1 position
        :param extend_len: extend length
        :param extend_dir: horizontal or vertical
        :param anchor_mode: anchor's position related to the region, 'corner' or 'edge'
        :param anchor2: anchor2 position
        :param targetable: whether this region can become a target of transportation
        """
        super().__init__(region_name, targetable)
        self.vcity = vcity
        self.normal_individuals: list[Individual] = []
        self.infected_individuals: list[Individual] = []
        self.attract_func = attract_func if attract_func else Region.pale_attractiveness
        self.attractiveness = self.attract_func(0)

        # configure the parallelogram region
        assert anchor_mode in ['corner', 'edge'], f'Bad parameter {anchor_mode} for anchor_mode'
        assert extend_dir in ['horizontal', 'vertical'], f'Bad parameter {extend_dir} for extend_dir'
        assert anchor1[0] <= anchor2[0] and anchor1[1] <= anchor2[1], f'{anchor1} is not on the lower left of {anchor2}'
        assert extend_len % 2 == 0, f'Extend length should be a even number'

        if anchor_mode == 'edge':
            if extend_dir == 'horizontal':
                sw_corner = anchor1 - np.array([extend_len / 2, 0])
            else:
                sw_corner = anchor1 - np.array([0, extend_len / 2])
        else:
            sw_corner = anchor1
        self.extend_dir = extend_dir
        self.extend_len = extend_len

        if extend_dir == 'horizontal':
            assert anchor2[1] != anchor1[1], 'Cannot extend horizontally because the anchors have the same y'
            self.main_dir_span = Span(anchor1[1], anchor2[1])
            ratio = (anchor2[0] - anchor1[0]) / self.main_dir_span.span
            self.get_subdir_span = lambda y: Span((y - sw_corner[1]) * ratio + sw_corner[0],
                                                  (y - sw_corner[1]) * ratio + sw_corner[0] + self.extend_len)
            main_cntr = self.main_dir_span.cntr
            self.cntr = np.array(self.get_subdir_span(main_cntr).cntr, main_cntr)
        else:
            assert anchor2[0] != anchor1[0], 'Cannot extend vertically because the anchors have the same x'
            self.main_dir_span = Span(anchor1[0], anchor2[0])
            ratio = (anchor2[1] - anchor1[1]) / self.main_dir_span.span
            self.get_subdir_span = lambda x: Span((x - sw_corner[0]) * ratio + sw_corner[1],
                                                  (x - sw_corner[0]) * ratio + sw_corner[1] + self.extend_len)
            main_cntr = self.main_dir_span.cntr
            self.cntr = np.array(main_cntr, self.get_subdir_span(main_cntr).cntr)

    def __contains__(self, pos: np.ndarray):
        if self.extend_dir == 'horizontal':
            if pos[1] in self.main_dir_span and pos[0] in self.get_subdir_span(pos[1]):
                return True
            else:
                return False
        else:
            if pos[0] in self.main_dir_span and pos[1] in self.get_subdir_span(pos[0]):
                return True
            else:
                return False

    def adjacent(self, pos: np.ndarray):
        """include both ends"""
        if self.extend_dir == 'horizontal':
            if self.main_dir_span.adjacent(pos[1]) and self.get_subdir_span(pos[1]).adjacent(pos[0]):
                return True
            else:
                return False
        else:
            if self.main_dir_span.adjacent(pos[0]) and self.get_subdir_span(pos[0]).adjacent(pos[1]):
                return True
            else:
                return False

    def rand_location(self) -> np.ndarray:
        main_sigma = self.main_dir_span.span / 6
        main_mu = self.main_dir_span.cntr
        random.seed(time.perf_counter())
        main_val = random.gauss(main_mu, main_sigma)
        while main_val not in self.main_dir_span:
            main_val = random.gauss(main_mu, main_sigma)

        current_sub_span = self.get_subdir_span(main_val)
        sub_sigma = current_sub_span.span / 6
        sub_mu = current_sub_span.cntr
        random.seed(time.perf_counter())
        sub_val = random.gauss(sub_mu, sub_sigma)
        while sub_val not in current_sub_span:
            sub_val = random.gauss(sub_mu, sub_sigma)

        if self.extend_dir == 'horizontal':
            return np.array(sub_val, main_val)
        else:
            return np.array(main_val, sub_val)

    def update_attractiveness(self, current_time):
        self.attractiveness = self.attract_func(current_time)

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


class VirtualCity:
    def __init__(self, size):
        self.size = size
        self.residential_buildings: dict[str, Region] = {}
        self.non_residential_buildings: dict[str, Region] = {}
        self.roads: list[Region] = []

    @property
    def buildings(self) -> dict[str, Region]:
        return {**self.non_residential_buildings, **self.residential_buildings}

    @property
    def regions(self) -> list[Region]:
        # noinspection PyTypeChecker
        return list(self.buildings.values()) + self.roads

    def build_road(self, port_dict: dict[str, tuple[int, int]], width, direction):
        for building_na, pos in port_dict.items():
            assert building_na in self.buildings.keys()
            building = self.buildings[building_na]
            assert building.adjacent(np.array(pos)), \
                f'{building_na} cannot be connected on {pos}'

        building_na1, building_na2 = port_dict.keys()
        building1, building2 = self.buildings[building_na1], self.buildings[building_na2]
        new_road = Region(f'R({building_na1}-{building_na2})', self, )
        self.roads.append(new_road)

    def add_building(self, name, loc: tuple, size, r_type):
        if r_type == 'R':
            self.residential_buildings[name] = Region(name, size, np.array(loc), self)
        if r_type == 'T':
            self.non_residential_buildings[name] = Region(name, size, np.array(loc), self)

    def finish_construction(self):
        threads = []
        for region in self.regions:
            threads.append(threading.Thread(target=region.finish_construction))
            threads[-1].start()
        for thread in threads:
            thread.join()


class Crowd:
    residential_buildings: dict[str, Region]
    non_residential_buildings: dict[str, Region]

    def __init__(self, population: int, initial_infected: int, step_length, drift_sigma, transport_activity):
        self.initial_infected = initial_infected
        self.population = population
        self.step_length = step_length
        self.drift_sigma = drift_sigma
        self.transport_activity = transport_activity

        self.normal_individuals: list[Individual] = []
        self.infected_individuals: list[Individual] = []
        self.transporting_individuals: list[Individual] = []

        self.random_nums = []
        for _ in range(2 * population):
            random.seed(time.perf_counter())
            self.random_nums.append(random.gauss(0, 3))

    @property
    def individuals(self):
        return self.normal_individuals + self.infected_individuals

    def initiate_individuals(self):
        for _ in range(self.population - self.initial_infected):
            self.normal_individuals.append(Individual(random.choice(list(self.residential_buildings.values())), self))
        for _ in range(self.initial_infected):
            self.infected_individuals.append(Individual(random.choice(list(self.residential_buildings.values())), self,
                                                        True))

    def move_all(self, current_time):
        for individual in self.individuals:
            individual.drift()
        transport_num = int(self.transport_activity(current_time) * self.population)
        self.transporting_individuals.extend(
            random.choices(self.individuals, k=transport_num - len(self.transporting_individuals))
        )
        for i, individual in enumerate(self.transporting_individuals):
            if individual.move() == 'arrived':
                self.transporting_individuals.pop(i)


class Virus:
    def __init__(self, infection_radius, risk):
        self.infection_radius = infection_radius
        self.risk = risk


class Simulation(VirtualCity, Crowd, Virus):
    def __init__(self,
                 time_period: tuple,  # period of time in a day that we simulate (in unit)
                 size: int,  # size of the virtual city
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
        VirtualCity.__init__(self, size)
        Crowd.__init__(self, population, initial_infected, step_length, drift_sigma, transport_activity)
        Virus.__init__(self, infection_radius, risk)

    def finish_construction(self):
        VirtualCity.finish_construction(self)
        self.initiate_individuals()

    def progress(self):
        if self.current_time not in range(*self.time_period):
            self.current_time = self.time_period[0]
            self.current_day += 1
        else:
            self.current_time += 1

        # update attractiveness
        for building in self.buildings.values():
            building.update_attractiveness(self.current_time)
        # move
        self.move_all(self.current_time)
        # update infection state
        for region in self.regions:
            region.update_infected(self)


if __name__ == '__main__':
    class _Test:
        A = Region('A', None)
        B = Region('B', None)
        C = Region('C', None)
        D = Region('D', None)
        Region.connect(A, B, np.array((0, 0)))
        Region.connect(B, C, np.array((0, 0)))
        Region.connect(C, D, np.array((0, 0)))
        Region.connect(D, A, np.array((0, 0)))
        for region in [A, B, C, D]:
            region.finish_construction()
        print(A.guidance_dict)
