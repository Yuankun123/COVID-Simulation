import matplotlib.pyplot as plt
from Codes.vcity.geography_layer import GeoDistrict
from typing import Iterable
__all__ = ['Displayer']


class Displayer:
    index = 0

    def __init__(self, target: GeoDistrict, x_span: Iterable, y_span: Iterable):
        self.name = target.rna
        self.target = target
        self.index = Displayer.index
        Displayer.index += 1

        plt.ion()
        plt.figure(self.index, figsize=(10, 10), dpi=80)
        plt.title(self.name)
        axes = plt.gca()
        axes.set_aspect(1)

        plt.xlim(*x_span)
        plt.ylim(*y_span)

    def refresh(self):
        plt.figure(self.index)
        axes = plt.gca()
        target = self.target

        for region in target.buildings:
            axes.add_artist(plt.Rectangle(xy=tuple(region.sw_pos), width=len(region.x_span), height=len(region.y_span),
                                          fill=True, facecolor='blue', alpha=0.2, edgecolor='black'))
        for road in target.roads:
            axes.add_artist(plt.Rectangle(xy=tuple(road.sw_pos), width=len(road.x_span), height=len(road.y_span),
                                          fill=True, facecolor='#e3d1d1', edgecolor='black'))

        plt.scatter(x=[port.pos[0] for port in target.ports],
                    y=[port.pos[1] for port in target.ports],
                    marker='x')

    @staticmethod
    def display(static=False):
        if static:
            plt.pause(10000)
        else:
            plt.pause(0.0001)
