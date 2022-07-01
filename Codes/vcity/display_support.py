import matplotlib.pyplot as plt
import matplotlib.patches as patches
from Codes.vcity.compound import Compound
from typing import Iterable
__all__ = ['Displayer']


class Displayer:
    index = 0

    def __init__(self, target: Compound, x_span: Iterable, y_span: Iterable):
        self.name = target.rna
        self.target = target
        self.index = Displayer.index
        self.x_span = x_span
        self.y_span = y_span
        Displayer.index += 1

        self.figure: plt.Figure = plt.figure(self.index, figsize=(10, 10), dpi=80)
        self.axes: plt.Axes = self.figure.add_axes([0, 0.05, 1, 0.90])

    def __set_up(self):
        self.axes.cla()
        self.axes.set_aspect('equal')
        self.axes.set_title(self.name)
        self.axes.set_xlim(*self.x_span)
        self.axes.set_ylim(*self.y_span)

    def refresh(self):
        self.__set_up()
        axes = self.axes
        target = self.target

        for region in target.rbds:
            axes.add_patch(patches.Rectangle(xy=tuple(region.sw_pos), width=len(region.x_span),
                                             height=len(region.y_span), fill=True, facecolor='blue',
                                             alpha=0.2, edgecolor='black'))

        for sqr in target.sqrs:
            axes.add_artist(plt.Rectangle(xy=tuple(sqr.sw_pos), width=len(sqr.x_span), height=len(sqr.y_span),
                                          fill=True, facecolor='#3fb24d', edgecolor='black'))

        for road in target.rds:
            axes.add_artist(plt.Rectangle(xy=tuple(road.sw_pos), width=len(road.x_span), height=len(road.y_span),
                                          fill=True, facecolor='#e3d1d1', edgecolor='black'))

        '''axes.scatter(x=[port.pos[0] for port in target.ports],
                     y=[port.pos[1] for port in target.ports],
                     marker='x')'''

    @staticmethod
    def display(static=False):
        if static:
            plt.pause(100000)
        else:
            plt.pause(0.0001)
