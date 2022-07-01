from typing import Iterable

from objects import Simulation, TIME_CONSTANT
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
        axes = self.axes
        axes.set_title(f'Day {target.current_day}, {target.current_time // TIME_CONSTANT}:00. '
                       f'Infected: {len(target.infected_individuals)}')

        axes.scatter(x=[indiv.pos[0] for indiv in target.normal_individuals],
                     y=[indiv.pos[1] for indiv in target.normal_individuals],
                     marker='o')

        axes.scatter(x=[indiv.pos[0] for indiv in target.infected_individuals],
                     y=[indiv.pos[1] for indiv in target.infected_individuals],
                     marker='o', color='red')


