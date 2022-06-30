import matplotlib.pyplot as plt
from typing import Iterable

from objects import Simulation
from vcity.display_support import Displayer as Dis
__all__ = ['Displayer']


class Displayer(Dis):
    index = 0
    target: Simulation

    def __init__(self, target: Simulation, x_span: Iterable, y_span: Iterable):
        super().__init__(target, x_span, y_span)

    def refresh(self):
        super().refresh()
        target = self.target

        plt.scatter(x=[indiv.pos[0] for indiv in target.normal_individuals],
                    y=[indiv.pos[1] for indiv in target.normal_individuals],
                    marker='o')

        plt.scatter(x=[indiv.pos[0] for indiv in target.infected_individuals],
                    y=[indiv.pos[1] for indiv in target.infected_individuals],
                    marker='o', color='red')
