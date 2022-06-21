from objects import Simulation, TIME_CONSTANT
from tools import rand_rearrange
import matplotlib.pyplot as plt
import random
import threading
import time
import sys
sys.setrecursionlimit(6000)
# ask display
display = input('Display?, Y or N')


def test_transport_activity(current_time):
    return 0.1


class DSimulation(Simulation):
    def __init__(self,
                 time_period: tuple,     # period of time in a day that we simulate (in unit)
                 size: int,              # size of the virtual city
                 population: int,        # population of this simulation
                 initial_infected: int,  # number of initially infected individuals
                 step_length: float,     # distance traveled per time unit
                 drift_sigma: float,     # stdev for drifting
                 transport_activity,     # percent of population transporting among regions in a given time unit (func)
                 infection_radius: float,
                 risk: float
                 ):

        super().__init__(time_period, size, population, initial_infected, step_length, drift_sigma, transport_activity,
                         infection_radius, risk)
        if display == 'Y':
            plt.ion()
            plt.figure(figsize=(10, 10), dpi=80)
            axes = plt.gca()
            axes.set_aspect(1)

    def display(self):
        plt.cla()
        plt.xlim(0, self.size - 1)
        plt.ylim(0, self.size - 1)
        plt.title(f'{sim.current_time // TIME_CONSTANT}')
        axes = plt.gca()
        for region in self.buildings.values():
            axes.add_artist(plt.Rectangle(xy=tuple(region.loc),
                                          width=region.size, height=region.size, fill=False))
        for road in self.roads:
            axes.add_artist(plt.Line2D(xdata=[protocol.pos[0] for protocol in road.protocols],
                                       ydata=[protocol.pos[1] for protocol in road.protocols],
                                       linewidth=1, color='black', fillstyle='none', markersize=10))

        plt.scatter(x=[indiv.pos[0] for indiv in self.normal_individuals],
                    y=[indiv.pos[1] for indiv in self.normal_individuals],
                    marker='o')

        plt.scatter(x=[indiv.pos[0] for indiv in self.infected_individuals],
                    y=[indiv.pos[1] for indiv in self.infected_individuals],
                    marker='o', color='red')

    def protocols_info(self):
        for protocol in sum([road.protocols for road in self.roads], []):
            print(protocol.connect_dict)

    def progress_info(self):
        if self.current_time % TIME_CONSTANT == 0:
            print(f'\nDay{self.current_day} {self.current_time // TIME_CONSTANT}:00')
        print(f'\r{len(self.infected_individuals)}', end='')


sim = DSimulation(time_period=(6 * TIME_CONSTANT, 20 * TIME_CONSTANT), size=1000, population=300, initial_infected=20,
                  step_length=10, drift_sigma=3, transport_activity=test_transport_activity, infection_radius=1.8,
                  risk=0.01)

# add buildings
i = 0
types = rand_rearrange(['R']*385 + ['T']*771)
for x in range(0, 1000, 30):  # 34 columns
    for y in range(0, 1000, 30):  # 34 rows
        sim.add_building(str(i), (x, y), 11, f'{types[i]}')
        i += 1

# horizontal roads
i = 0
for left_end_x in range(10, 1000, 30):
    for left_end_y in range(5, 1000, 30):
        sim.build_road({str(i): (left_end_x, left_end_y), str(i + 34): (left_end_x + 20, left_end_y)}, 5)
        i += 1

# horizontal roads
i = 0
for lower_end_x in range(5, 1000, 30):
    for lower_end_y in range(10, 1000, 30):
        if i % 34 == 33:
            i += 1
        sim.build_road({str(i): (lower_end_x, lower_end_y), str(i + 1): (lower_end_x, lower_end_y + 20)}, 5)
        i += 1


threading.stack_size(200000000)
thr = threading.Thread(target=sim.finish_construction)
thr.start()
thr.join()
# parallel random number generator
stop = False


def random_refresh():
    while not stop:
        time.sleep(0.000001)
        random.seed(time.perf_counter())
        sim.random_nums.append(random.gauss(0, 3))
        sim.random_nums.pop(0)
        sim.random_nums = rand_rearrange(sim.random_nums)


rs = threading.Thread(target=random_refresh)
rs.start()
if display == 'Y':
    while sim.current_day < 30:
        sim.progress()
        sim.progress_info()
        sim.display()
        plt.pause(0.00001)
else:
    while sim.current_day < 30:
        sim.progress()
        sim.progress_info()
stop = True
