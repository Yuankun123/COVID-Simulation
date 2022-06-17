from Objects import VirtualCity, TIME_CONSTANT
from Tool import rand_rearrange
import matplotlib.pyplot as plt
import random
import threading
import time
# ask display
display = input('Display?, Y or N')


def transport_activity():
    return 0.1


class Simulation(VirtualCity):
    def __init__(self, size, population):
        super().__init__(size, population, transport_activity)
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
        for region in self.buildings:
            axes.add_artist(plt.Rectangle(xy=tuple(region.loc),
                                          width=region.size, height=region.size, fill=False))
        for road in self.roads:
            axes.add_artist(plt.Line2D(xdata=[protocol.pos[0] for protocol in road.protocols],
                                       ydata=[protocol.pos[1] for protocol in road.protocols],
                                       linewidth=1, color='red', fillstyle='none',
                                       marker='x', markersize=10))

        plt.scatter(x=[indiv.pos[0] for indiv in self.individuals], y=[indiv.pos[1] for indiv in self.individuals],
                    marker='o')

    def protocols_info(self):
        for protocol in sum([road.protocols for road in self.roads], []):
            print(protocol.connect_dict)


sim = Simulation(size=1000, population=300)
R1 = sim.add_region('R1', (250, 250), 101, 'R')
R2 = sim.add_region('R2', (250, 450), 101, 'R')
R3 = sim.add_region('R3', (250, 650), 101, 'R')
R4 = sim.add_region('R4', (450, 250), 101, 'R')
T1 = sim.add_region('T1', (450, 450), 101, 'T')
T2 = sim.add_region('T2', (450, 650), 101, 'T')
T3 = sim.add_region('T3', (650, 250), 101, 'T')
T4 = sim.add_region('T4', (650, 450), 101, 'T')
T5 = sim.add_region('T5', (650, 650), 101, 'T')

sim.build_road({R1: (350, 300), R4: (450, 300)}, 5)
sim.build_road({R2: (350, 500), T1: (450, 500)}, 5)
sim.build_road({R3: (350, 700), T2: (450, 700)}, 5)
sim.build_road({R4: (550, 300), T3: (650, 300)}, 5)
sim.build_road({T1: (550, 500), T4: (650, 500)}, 5)
sim.build_road({T2: (550, 700), T5: (650, 700)}, 5)

sim.build_road({R1: (300, 350), R2: (300, 450)}, 5)
sim.build_road({R4: (500, 350), T1: (500, 450)}, 5)
sim.build_road({T3: (700, 350), T4: (700, 450)}, 5)
sim.build_road({R2: (300, 550), R3: (300, 650)}, 5)
sim.build_road({T1: (500, 550), T2: (500, 650)}, 5)
sim.build_road({T4: (700, 550), T5: (700, 650)}, 5)
sim.freeze()
sim.add_crowd()

# parallel random number generator
stop = False


def random_refresh():
    while not stop:
        time.sleep(0.00001)
        random.seed(time.perf_counter())
        sim.random_nums.append(random.gauss(0, 3))
        sim.random_nums.pop(0)
        rand_rearrange(sim.random_nums)



rs = threading.Thread(target=random_refresh)
rs.start()
if display == 'Y':
    while sim.current_day < 30:
        sim.progress()
        sim.update_attractiveness()
        sim.move()
        sim.display()
        plt.pause(0.00001)
        if sim.current_time % TIME_CONSTANT == 0:
            print(sim.current_time // TIME_CONSTANT)
else:
    while sim.current_day < 30:
        sim.progress()
        sim.update_attractiveness()
        sim.move()
        if sim.current_time % TIME_CONSTANT == 0:
            print(sim.current_time // TIME_CONSTANT)
stop = True
