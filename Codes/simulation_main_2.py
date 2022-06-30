import time
import random
import math
import threading

from objects import Simulation, TIME_CONSTANT
from display_support import Displayer
from tools import rand_rearrange
display = input('Display?, Y or N')


def test_transport_activity(current_time):
    if 6 * TIME_CONSTANT < current_time <= 8 * TIME_CONSTANT:
        return (math.cos(1.5 * (current_time / TIME_CONSTANT - 8)) + 1) / 10 + 0.1
    else:
        return (math.cos(0.75 * (current_time / TIME_CONSTANT - 8)) + 1) / 10 + 0.1


sim = Simulation(time_period=(6 * TIME_CONSTANT, 20 * TIME_CONSTANT), population=300, initial_infected=20,
                 step_length=5, drift_sigma=3, transport_activity=test_transport_activity,
                 infection_radius=1.8, risk=0.01)

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
    displayer = Displayer(sim, (0, sim.size[0]), (0, sim.size[1]))
    while sim.current_day < 5:
        sim.progress()
        sim.print_progress_info()
        displayer.refresh()
        displayer.display()
    stop = True
else:
    while sim.current_day < 5:
        sim.progress()
        sim.print_progress_info()


