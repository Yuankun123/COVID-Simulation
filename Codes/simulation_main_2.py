import time
import random
import math
import threading
from moviepy.editor import VideoClip
from moviepy.video.io.bindings import mplfig_to_npimage

from objects import Simulation, TIME_CONSTANT
from display_support import Displayer
from tools import rand_rearrange
mode = input('\'D\' for displaying\n\'R\'for recording\n\'P\'for printing information directly\n')


def test_transport_activity(current_time):
    if 6 * TIME_CONSTANT < current_time <= 8 * TIME_CONSTANT:
        return (math.cos(1.5 * (current_time / TIME_CONSTANT - 8)) + 1) / 10
    else:
        return (math.cos(0.75 * (current_time / TIME_CONSTANT - 8)) + 1) / 10


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
displayer = Displayer(sim, (0, sim.size[0]), (0, sim.size[1]))
if mode == 'D':
    while sim.current_day < 5:
        sim.progress()
        sim.print_progress_info()
        displayer.refresh()
        Displayer.display()
elif mode == 'R':
    path = input('please enter the path to save the video')

    # noinspection PyUnusedLocal
    def task(t):
        sim.progress()
        displayer.refresh()
        return mplfig_to_npimage(displayer.figure)

    animation = VideoClip(task, duration=252)
    animation.write_videofile(path, fps=20)
else:
    while sim.current_day < 5:
        sim.progress()
        sim.print_progress_info()
stop = True
