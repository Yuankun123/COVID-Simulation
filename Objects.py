import random
import time
import numpy as np
from Tool import unit_vector
from numpy.linalg import norm
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

    def freeze(self):
        self.connect_dict[self.region1] = self.accessible_from(self.region1)
        self.connect_dict[self.region2] = self.accessible_from(self.region2)


class Region:
    @staticmethod
    def connect(region1: 'Region', region2: 'Region', pos: np.ndarray):
        new_protocol = Protocol(region1, region2, pos)  # create protocol
        region1.protocols.append(new_protocol)
        region2.protocols.append(new_protocol)

    def __init__(self, name: str, v_city: 'VirtualCity', add_self=True):
        self.na = name
        self.v_city = v_city
        self.add_self = add_self
        self.protocols: list[Protocol] = []
        self.accessible: dict['Region', int] = {}

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

    def freeze(self):
        for protocol in self.protocols:
            protocol.freeze()
        self.accessible = self.accessible_from()

    def find_protocol(self, target: 'Region') -> Protocol:
        candidates = []
        for protocol in self.protocols:
            if target in protocol.connect_dict[self].keys():
                candidates.append((protocol, protocol.connect_dict[self][target]))
        candidates.sort(key=lambda x: x[1])
        return candidates[0][0]

    def find_next_region(self, target: 'Region') -> 'Region':
        return self.find_protocol(target).other_side(self)

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


class Building(Region):
    @staticmethod
    def default_attractiveness():
        return 0

    def __init__(self, name, size, loc: np.ndarray, r_type, v_city: 'VirtualCity', attract_func=None):
        super().__init__(name, v_city)
        self.loc = loc
        self.size = size
        self.r_type = r_type
        self.attract_func = attract_func if attract_func else self.default_attractiveness
        self.attractiveness = self.attract_func()
        self.cntr = self.loc + np.array([(self.size - 1) / 2] * 2)

    def update_attractiveness(self):
        self.attractiveness = self.attract_func()

    def rand_location(self) -> np.ndarray:
        y_sigma = x_sigma = (self.size - 1) / 6
        x_mu, y_mu = self.cntr
        res = (random.gauss(x_mu, x_sigma), random.gauss(y_mu, y_sigma))
        while res not in self:
            res = (random.gauss(x_mu, x_sigma), random.gauss(y_mu, y_sigma))
        return np.array(np.round_(res))

    def __contains__(self, pos: np.ndarray):
        return 0 <= (pos - self.loc)[0] < self.size and 0 <= (pos - self.loc)[1] < self.size


class StraightRoad(Region):
    def __init__(self, width, v_city: 'VirtualCity'):
        super().__init__('Road', v_city, add_self=False)
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
    def default_attractiveness(self):
        return 1

    def __init__(self, name, size, loc: np.ndarray, v_city, attract_func=None):
        super().__init__(name, size, loc, 'R', v_city, attract_func)


class TBuilding(Building):
    def default_attractiveness(self):
        if 11 * TIME_CONSTANT <= self.v_city.current_time < 13 * TIME_CONSTANT:
            return 0
        else:
            return 10

    def __init__(self, name, size, loc: np.ndarray, v_city, attract_func=None):
        super().__init__(name, size, loc, 'T', v_city, attract_func)


class Individual:
    index = 0
    step_length = 10
    drift_sigma = 3

    def __init__(self, home: RBuilding, v_city: 'VirtualCity'):
        self.index = Individual.index
        Individual.index += 1
        self.home = home
        self.pos = home.rand_location()
        self.imagined_current_region: Region = home  # the quasi-current-location that instructs the individual to move
        self.v_city = v_city
        self.target = None
        self.target_protocol = None  # temperate protocol

    def generate_target(self):
        # noinspection PyTypeChecker
        candidates: list[Building] = [building for building in self.v_city.non_residential_buildings] + [self.home]
        weights = [candidate.attractiveness for candidate in candidates]
        return random.choices(candidates, weights=weights)[0]

    def drift(self):
        if self.target is None:
            self.pos += \
                (self.imagined_current_region.cntr - self.pos) ** 3 / (self.imagined_current_region.size / 2) ** 3
        self.pos += np.array([self.v_city.random_nums[self.index], self.v_city.random_nums[-self.index]])

    def move(self):
        if self.target is None:
            self.target = self.generate_target()
            self.imagined_current_region = self.imagined_current_region.find_next_region(self.target)
            self.target_protocol = self.imagined_current_region.find_protocol(self.target)
            # print('New target:', self.target)
            # print('Current target:', self.target_protocol.pos)
        if self.pos in self.target:
            self.imagined_current_region = self.target
            self.target = None
            return 'arrived'

        # move
        if self.pos not in self.imagined_current_region:
            direction = unit_vector(self.target_protocol.pos - self.pos)
            self.pos += np.round_(direction * Individual.step_length, decimals=0)
        else:
            self.imagined_current_region = self.target_protocol.other_side(self.imagined_current_region)
            self.target_protocol = self.imagined_current_region.find_protocol(self.target)
            # print('Current target:', self.target_protocol.pos)


class VirtualCity:
    def __init__(self, size, population, transport_activity_func):
        self.population = population
        self.size = size
        self.current_time = 0
        self.current_day = 0
        self.transport_activity_func = transport_activity_func

        self.random_nums = []
        for _ in range(2 * population):
            random.seed(time.perf_counter())
            self.random_nums.append(random.gauss(0, 3))

        self.residential_buildings: list[RBuilding] = []
        self.non_residential_buildings: list[TBuilding] = []
        self.roads: list[StraightRoad] = []
        self.individuals: list[Individual] = []
        self.transporting_individuals: list[Individual] = []

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

    def add_crowd(self):
        for _ in range(self.population):
            self.individuals.append(Individual(random.choice(self.residential_buildings), self))

    def move(self):
        for individual in self.individuals:
            individual.drift()
        transport_num = int(self.transport_activity_func() * self.population)
        self.transporting_individuals.extend(
            random.choices(self.individuals, k=transport_num - len(self.transporting_individuals))
        )
        for i, individual in enumerate(self.transporting_individuals):
            if individual.move() == 'arrived':
                self.transporting_individuals.pop(i)

    def freeze(self):
        # noinspection PyTypeChecker
        for region in self.buildings + self.roads:
            region.freeze()

    def progress(self):
        if self.current_time < 6 * TIME_CONSTANT or self.current_time >= 18 * TIME_CONSTANT:
            self.current_time = 6 * TIME_CONSTANT
            self.current_day += 1
        else:
            self.current_time += 1

    def update_attractiveness(self):
        for building in self.buildings:
            building.update_attractiveness()


class Virus:
    pass


if __name__ == '__main__':
    class _Test:
        A = Region('A')
        B = Region('B')
        C = Region('C')
        D = Region('D')
        Region.connect(A, B, np.array((0, 0)))
        Region.connect(B, C, np.array((0, 0)))
        Region.connect(C, D, np.array((0, 0)))
        Region.connect(D, A, np.array((0, 0)))
        print(A.detail_info())
        print(B.detail_info())
        print(C.detail_info())
        print(D.detail_info())
