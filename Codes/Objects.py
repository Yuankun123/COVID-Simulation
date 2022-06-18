import random
import time
import numpy as np
from Tool import unit_vector, norm
NORMAL = 'normal'
INFECTED = 'infected'
TIME_CONSTANT = 360  # 1 hours contains 360 time units


class Protocol:
    def __init__(self, region1: 'Region', region2: 'Region', pos: np.ndarray):
        self.region1 = region1
        self.region2 = region2
        self.pos = pos
        self.connect_dict: dict[Region, dict[Region, int]] = {}

    def other_side(self, origin: 'Region') -> 'Region':
        if origin == self.region1:
            return self.region2
        else:
            return self.region1

    def accessible_from(self, origin: 'Region', track: list['Region'] = None):
        if track is None:
            track = []
        # print(f'Getting view form {origin} to {self}')
        res = {}
        source_region = self.other_side(origin)
        if source_region in track:
            return {}
        for region, distance in source_region.accessible_from(self, track).items():
            res[region] = distance + 1
        return res

    def __repr__(self):
        return f'Protocol between {repr(self.region1)} and {repr(self.region2)}'

    def finish_construction(self):
        self.connect_dict[self.region1] = self.accessible_from(self.region1)
        self.connect_dict[self.region2] = self.accessible_from(self.region2)


class Region:
    @staticmethod
    def connect(region1: 'Region', region2: 'Region', pos: np.ndarray):
        new_protocol = Protocol(region1, region2, pos)  # create protocol
        region1.protocols.append(new_protocol)
        region2.protocols.append(new_protocol)

    def __init__(self, name: str, vcity: 'VirtualCity', add_self=True):
        self.na = name
        self.vcity = vcity
        self.add_self = add_self
        self.protocols: list[Protocol] = []
        self.accessible: dict[Region, int] = {}
        self.normal_individuals: list[Individual] = []
        self.infected_individuals: list[Individual] = []

    def accessible_from(self, origin: Protocol = None, root_track=None) -> dict['Region', int]:
        # print(f'Getting Accessible Regions From {origin} in {self}')
        if root_track is None:
            root_track = []

        res = {}
        if self.add_self:
            res = {self: 0}
        for protocol in self.protocols:
            if protocol != origin:
                track = root_track + [self]  # this automatically create a copy
                for region, distance in protocol.accessible_from(self, track).items():
                    if region != self and (region not in res.keys() or distance < res[region]):
                        res[region] = distance
        return res

    def finish_construction(self):
        for protocol in self.protocols:
            protocol.finish_construction()
        self.accessible = self.accessible_from()

    def find_protocol(self, target: 'Region') -> Protocol:
        assert target != self
        candidates = []
        for protocol in self.protocols:
            if target in protocol.connect_dict[self].keys():
                candidates.append((protocol, protocol.connect_dict[self][target]))
        candidates.sort(key=lambda x: x[1])
        return candidates[0][0]

    def __repr__(self):
        return self.na

    def detail_info(self):
        res = f'{self.na}. ' \
              f'Having protocols to: {", ".join([repr(protocol.other_side(self)) for protocol in self.protocols])}, '
        for region, distance in self.accessible_from().items():
            res += f'Having access to {region} in distance {distance} '
        return res

    def __contains__(self, pos: np.ndarray):
        pass

    def update_infected(self):
        for individual1 in self.infected_individuals:
            for individual2 in self.normal_individuals:
                if norm(individual1.pos - individual2.pos) < Virus.infect_distance:
                    random.seed(time.perf_counter())
                    individual2.infected_state = random.choices([INFECTED, NORMAL], cum_weights=[Virus.risk, 1])[0]
                    if individual2.infected_state == INFECTED:
                        self.normal_individuals.remove(individual2)
                        self.infected_individuals.append(individual2)

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


class Building(Region):
    @staticmethod
    def default_attractiveness(current_time):
        return 0

    def __init__(self, name, size, loc: np.ndarray, r_type, vcity: 'VirtualCity', attract_func=None):
        super().__init__(name, vcity)
        self.loc = loc
        self.size = size
        self.r_type = r_type
        self.attract_func = attract_func if attract_func else self.default_attractiveness
        self.attractiveness = self.attract_func(0)
        self.cntr = self.loc + np.array([(self.size - 1) / 2] * 2)

    def update_attractiveness(self, current_time):
        self.attractiveness = self.attract_func(current_time)

    def rand_location(self) -> np.ndarray:
        y_sigma = x_sigma = (self.size - 1) / 6
        x_mu, y_mu = self.cntr
        random.seed(time.perf_counter())
        res = (random.gauss(x_mu, x_sigma), random.gauss(y_mu, y_sigma))
        while res not in self:
            res = (random.gauss(x_mu, x_sigma), random.gauss(y_mu, y_sigma))
        return np.array(np.round_(res))

    def __contains__(self, pos: np.ndarray):
        return 0 <= (pos - self.loc)[0] < self.size and 0 <= (pos - self.loc)[1] < self.size


class StraightRoad(Region):
    def __init__(self, width, vcity: 'VirtualCity'):
        super().__init__('Road', vcity, add_self=False)
        self.width = width

    def distance_from_axis(self, pos):
        x, y = pos
        (x1, y1), (x2, y2) = [protocol.pos for protocol in self.protocols]
        adjusted_delta_y = abs((y1 - y) * (x2 - x1) + (x - x1) * (y2 - y1))
        return adjusted_delta_y / ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def __contains__(self, pos: np.ndarray):
        if not self.distance_from_axis(pos) < self.width:
            return False
        port1, port2 = [protocol.pos for protocol in self.protocols]
        squared_length = norm(port1 - port2) ** 2
        if norm(port1 - pos) ** 2 > norm(port2 - pos) ** 2 + squared_length \
                or norm(port2 - pos) ** 2 > norm(port1 - pos) ** 2 + squared_length:
            return False
        return True


class RBuilding(Building):
    def default_attractiveness(self, current_time):
        return 1

    def __init__(self, name, size, loc: np.ndarray, vcity, attract_func=None):
        super().__init__(name, size, loc, 'R', vcity, attract_func)


class TBuilding(Building):
    def default_attractiveness(self, current_time):
        if 11 * TIME_CONSTANT <= current_time < 13 * TIME_CONSTANT:
            return 1
        else:
            return 10

    def __init__(self, name, size, loc: np.ndarray, vcity, attract_func=None):
        super().__init__(name, size, loc, 'T', vcity, attract_func)


class Individual:
    index = 0

    def __init__(self, home: RBuilding, crowd: 'Crowd', infected=False):
        if infected:
            self.infected_state = INFECTED
        else:
            self.infected_state = NORMAL

        self.index = Individual.index
        Individual.index += 1

        self.home = home
        self.pos = home.rand_location()
        self.imagined_current_region: Region = home  # the quasi-current-location that instructs the individual to move
        self.current_region = home
        home.add_individual(self)

        self.crowd = crowd
        self.target = None
        self.target_protocol = None  # temperate protocol

    def generate_target(self):
        # noinspection PyTypeChecker
        candidates: list[Building] = [building for building in self.crowd.non_residential_buildings] + [self.home]
        weights = [candidate.attractiveness for candidate in candidates]
        while (res := random.choices(candidates, weights=weights)[0]) == self.current_region:
            pass
        return res

    def drift(self):
        self.pos += np.array([self.crowd.random_nums[self.index], self.crowd.random_nums[-self.index]])
        ''' if isinstance(self.current_region, Building):
            while self.pos not in self.current_region and self.pos not in self.imagined_current_region:
                # noinspection PyUnresolvedReferences
                self.pos += (self.current_region.cntr - self.pos) / 10'''
        if self.target is None:
            self.pos += (self.current_region.cntr - self.pos) / (self.current_region.size / 2)
            while self.pos not in self.current_region:
                self.pos += (self.current_region.cntr - self.pos) / (self.current_region.size / 10)

    def move(self):
        if self.target is None:
            self.target = self.generate_target()
            self.target_protocol = self.current_region.find_protocol(self.target)
            self.imagined_current_region = self.target_protocol.other_side(self.current_region)

        # move
        if self.pos not in self.imagined_current_region:
            direction = unit_vector(self.target_protocol.pos - self.pos)
            self.pos += np.round_(direction * self.crowd.step_length, decimals=0)

        if self.pos in self.target:
            assert self.imagined_current_region == self.target, (self.current_region, self.imagined_current_region,
                                                                 self.target_protocol, self.target)
            self.current_region.remove_individual(self)
            self.imagined_current_region.add_individual(self)
            self.current_region = self.imagined_current_region
            self.target = None
            return 'arrived'

        if self.pos in self.imagined_current_region:
            self.current_region.remove_individual(self)
            self.imagined_current_region.add_individual(self)
            self.current_region = self.imagined_current_region

            self.target_protocol = self.current_region.find_protocol(self.target)
            self.imagined_current_region = self.target_protocol.other_side(self.current_region)
            # print('Current target:', self.target_protocol.pos)


class VirtualCity:
    def __init__(self, size):
        self.size = size
        self.residential_buildings: list[RBuilding] = []
        self.non_residential_buildings: list[TBuilding] = []
        self.roads: list[StraightRoad] = []

    @property
    def buildings(self) -> list[Building]:
        # noinspection PyTypeChecker
        return self.non_residential_buildings + self.residential_buildings

    def build_road(self, port_dict: dict[Building, tuple[int, int]], width):
        for region, pos in port_dict.items():
            assert region in self.buildings
            assert 0 <= pos[0] - region.loc[0] < region.size and 0 <= pos[1] - region.loc[1] < region.size, region

        new_road = StraightRoad(width, self)
        self.roads.append(new_road)

        for region, pos in port_dict.items():
            Region.connect(new_road, region, np.array(pos))

    def add_region(self, name, loc: tuple, size, r_type):
        res = None
        if r_type == 'R':
            self.residential_buildings.append(res := RBuilding(name, size, np.array(loc), self))
        if r_type == 'T':
            self.non_residential_buildings.append(res := TBuilding(name, size, np.array(loc), self))
        return res

    def finish_construction(self):
        # noinspection PyTypeChecker
        for region in self.buildings + self.roads:
            region.finish_construction()

    def update_attractiveness(self, current_time):
        for building in self.buildings:
            building.update_attractiveness(current_time)

    def update_infected(self):
        # noinspection PyTypeChecker
        for region in self.buildings + self.roads:
            region.update_infected()


class Crowd:
    def __init__(self, population: int, initial_infected: int, step_length, drift_sigma, transport_activity):
        self.initial_infected = initial_infected
        self.population = population
        self.step_length = step_length
        self.drift_sigma = drift_sigma
        self.transport_activity = transport_activity

        self.residential_buildings = []
        self.non_residential_buildings = []
        self.individuals: list[Individual] = []
        self.transporting_individuals: list[Individual] = []

        self.random_nums = []
        for _ in range(2 * population):
            random.seed(time.perf_counter())
            self.random_nums.append(random.gauss(0, 3))

    def initiate_individuals(self, residential_buildings, non_residential_buildings):
        self.residential_buildings = residential_buildings
        self.non_residential_buildings = non_residential_buildings
        for _ in range(self.population - self.initial_infected):
            self.individuals.append(Individual(random.choice(self.residential_buildings), self))
        for _ in range(self.initial_infected):
            self.individuals.append(Individual(random.choice(self.residential_buildings), self, True))

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


class Simulation(VirtualCity, Crowd):
    def __init__(self,
                 time_period: tuple,     # period of time in a day that we simulate (in unit)
                 size: int,              # size of the virtual city
                 population: int,        # population of this simulation
                 initial_infected: int,  # number of initially infected individuals
                 step_length: float,     # distance traveled per time unit
                 drift_sigma: float,     # stdev for drifting
                 transport_activity,     # percent of population transporting among regions in a given time unit (func)
                 ):
        self.current_time = 0
        self.current_day = 0
        self.time_period = time_period
        VirtualCity.__init__(self, size)
        Crowd.__init__(self, population, initial_infected, step_length, drift_sigma, transport_activity)

    def finish_construction(self):
        VirtualCity.finish_construction(self)
        self.initiate_individuals(self.residential_buildings, self.non_residential_buildings)

    def progress(self):
        if self.current_time not in range(*self.time_period):
            self.current_time = self.time_period[0]
            self.current_day += 1
        else:
            self.current_time += 1

        self.update_attractiveness(self.current_time)
        self.move_all(self.current_time)
        self.update_infected()


class Virus:
    infect_distance = 1.8
    risk = 0.01
    pass


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
        print(A.detail_info())
        print(B.detail_info())
        print(C.detail_info())
        print(D.detail_info())
