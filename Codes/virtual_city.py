import random
import time
import numpy as np
from tools import Span
from connection_layer import AbstractProtocol, AbstractRegion, ComplexRegion


class GeoProtocol(AbstractProtocol):
    def __init__(self, region1, region2, pos):
        super().__init__(region1, region2)
        self.pos = pos


class GeoRegion(AbstractRegion):
    """Every Building is a rectangle"""
    def __init__(self, region_name: str, vcity: 'VirtualCity', x_span: Span, y_span: Span, add_self):
        super().__init__(region_name, add_self)
        self.vcity = vcity
        self.x_span = x_span
        self.y_span = y_span
        self.sw_loc = np.array([x_span.start, y_span.start])
        self.cntr = np.array([x_span.cntr, y_span.cntr])

    def __contains__(self, pos: np.ndarray):
        return pos[0] in self.x_span and pos[1] in self.y_span

    def adjacent(self, pos: np.ndarray):
        return self.x_span.adjacent(pos[0]) and self.y_span.adjacent(pos[1])

    def rand_location(self) -> np.ndarray:
        x_sigma, y_sigma = self.x_span.span / 6, self.y_span.span / 6
        x_mu, y_mu = self.cntr
        random.seed(time.perf_counter())
        res = (random.gauss(x_mu, x_sigma), random.gauss(y_mu, y_sigma))
        while res not in self:
            res = (random.gauss(x_mu, x_sigma), random.gauss(y_mu, y_sigma))
        return np.array(np.round_(res))


class VirtualCity(ComplexRegion):
    _part_name_dict: list[GeoRegion]
    protocols: list[GeoProtocol]
    inner_protocol_type = GeoProtocol
    inner_region_type = GeoRegion

    def __init__(self, size):
        super().__init__()
        self.size = size
        self.buildings: list[GeoRegion] = []
        self.roads: list[GeoRegion] = []

    def add_inner_region(self, name, x_span: tuple = None, y_span: tuple = None, targetable=True, **kwargs):
        new_building = super().add_inner_region(name, vcity=self, x_span=Span(*x_span), y_span=Span(*y_span),
                                                add_self=targetable, **kwargs)
        if targetable:
            self.buildings.append(new_building)
        else:
            self.roads.append(new_building)
        return new_building

    def connect(self, region_na1, region_na2, pos: tuple = None, **kwargs):
        assert region_na1
        super().connect(region_na1, region_na2, pos=pos)


if __name__ == '__main__':
    class _Test:
        pass
