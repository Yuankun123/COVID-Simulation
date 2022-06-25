import random
import time
import numpy as np
from tools import Span
from connection_layer import *


class GeoPort(get_base(), AbstractPort):
    def __init__(self, name: str, pos: np.ndarray, **kwargs):
        super().__init__(name, **kwargs)
        self.pos = pos


class GeoRegion(GeoPort, AbstractRegion):
    """Every Building is a rectangle"""
    def __init__(self,
                 name: str,
                 x_span: tuple,
                 y_span: tuple,
                 **kwargs):
        self.x_span, self.y_span = Span(*x_span), Span(*y_span)
        super().__init__(name, np.array([self.x_span.start, self.y_span.start]), **kwargs)
        self.cntr = np.array([self.x_span.cntr, self.y_span.cntr])

    def __contains__(self, pos: np.ndarray):
        return pos[0] in self.x_span and pos[1] in self.y_span

    def rand_location(self) -> np.ndarray:
        x_sigma, y_sigma = self.x_span.span / 6, self.y_span.span / 6
        x_mu, y_mu = self.cntr
        random.seed(time.perf_counter())
        res = (random.gauss(x_mu, x_sigma), random.gauss(y_mu, y_sigma))
        while res not in self:
            res = (random.gauss(x_mu, x_sigma), random.gauss(y_mu, y_sigma))
        return np.array(np.round_(res))

    @property
    def ports(self) -> list[GeoPort]:
        return [protocol.port_against(self) for protocol in self.protocols]

    def __repr__(self):
        return f'X: {self.x_span}; Y: {self.y_span}'


class GeoDistrict(GeoRegion, AbstractDistrict):
    def __init__(self, name, **kwargs):
        super().__init__(name, (0, 0), (0, 0), **kwargs)

    def _additional_task(self, new_subregion: GeoRegion):
        vcity = self.types[CITY].TheCity
        if new_subregion.level == 0:
            if new_subregion.add_self:
                vcity.buildings.append(new_subregion)
            else:
                vcity.roads.append(new_subregion)

    @staticmethod
    def _get_ports(region1: GeoRegion, region2: GeoRegion) -> tuple[GeoPort, GeoPort]:
        x_overlapped_span = Span.overlapped_span(region1.x_span, region2.x_span)
        y_overlapped_span = Span.overlapped_span(region1.y_span, region2.y_span)
        cntr_pos = np.array([x_overlapped_span.cntr, y_overlapped_span.cntr])
        if x_overlapped_span.span > y_overlapped_span.span:  # vertical
            if region1.y_span.cntr > region2.y_span.cntr:  # region1 on top
                pos1 = cntr_pos - np.array([0, 1])
                pos2 = cntr_pos + np.array([0, 1])
            else:  # region2 on top
                pos1 = cntr_pos + np.array([0, 1])
                pos2 = cntr_pos - np.array([0, 1])
        else:  # horizontal
            if region1.x_span.cntr > region2.x_span.cntr:  # region1 on the right
                pos1 = cntr_pos - np.array([1, 0])
                pos2 = cntr_pos + np.array([1, 0])
            else:  # region2 on the right
                pos1 = cntr_pos + np.array([1, 0])
                pos2 = cntr_pos - np.array([1, 0])

        assert pos1 in region2, f'pos: {pos1} is not in region: {region2}'
        assert pos2 in region1, f'pos: {pos2} is not in region: {region1}'

        root_port1 = GeoPort(f'AP[{region2}->{region1}]', pos1).slaved(master=region1)
        root_port2 = GeoPort(f'AP[{region1}->{region2}]', pos2).slaved(master=region2)

        return root_port1, root_port2

    def __call__(self, *regions: GeoRegion, connections: tuple[tuple[GeoRegion, GeoRegion], ...] = ()) \
            -> 'GeoDistrict':
        super().__call__(*regions, connections=connections)
        return self


class GeoCity(GeoDistrict, AbstractCity):
    def __init__(self, name,  size):
        super().__init__(name)
        self.size = size
        self.buildings: list[GeoRegion] = []
        self.roads: list[GeoRegion] = []
        self.all_ports: list[GeoPort] = []

    def _get_all_ports(self):
        for building in self.buildings:
            self.all_ports.extend(building.ports)
            print(building.ports)

    def __call__(self, *regions: GeoRegion, connections: tuple[tuple[GeoRegion, GeoRegion], ...] = ()) \
            -> 'GeoCity':
        super().__call__(*regions, connections=connections)
        self._get_all_ports()
        return self


if __name__ == '__main__':
    class _Test:
        print(AbstractPort.types)
