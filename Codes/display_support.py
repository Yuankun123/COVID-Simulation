import matplotlib.pyplot as plt
from geography_layer import GeoDistrict
__all__ = ['Displayer']


class Displayer:
    index = 0

    def __init__(self, vcity: GeoDistrict, crowd):
        self.name = vcity.na
        self.vcity = vcity
        self.crowd = crowd
        self.index = Displayer.index
        Displayer.index += 1

        plt.ion()
        plt.figure(self.index, figsize=(10, 10), dpi=80)
        plt.title(self.name)
        axes = plt.gca()
        axes.set_aspect(1)

        plt.xlim(*self.vcity.x_span)
        plt.ylim(*self.vcity.y_span)

    def refresh(self):
        plt.figure(self.index)
        axes = plt.gca()

        for region in self.vcity.buildings:
            axes.add_artist(plt.Rectangle(xy=tuple(region.pos), width=len(region.x_span), height=len(region.y_span),
                                          fill=False))
        for road in self.vcity.roads:
            axes.add_artist(plt.Rectangle(xy=tuple(road.pos), width=len(road.x_span), height=len(road.y_span),
                                          fill=True, facecolor='#e3d1d1', edgecolor='black'))

        plt.scatter(x=[port.pos[0] for port in self.vcity.ports],
                    y=[port.pos[1] for port in self.vcity.ports],
                    marker='x')

    @staticmethod
    def display(static=False):
        if static:
            plt.pause(10000)
        else:
            plt.pause(0.0001)
