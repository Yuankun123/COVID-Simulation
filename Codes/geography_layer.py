import random
import time
import numpy as np
from tools import Span
from connection_layer import *
__all__ = ['GeoPort', 'GeoRegion', 'GeoDistrict']


class GeoPort(AbstractPort, is_port_type=True):
    def __init__(self, name: str, pos: np.ndarray, **kwargs):
        super().__init__(name, **kwargs)
        self.pos = pos


class GeoRegion(GeoPort, AbstractRegion):
    """Every Building is a rectangle"""
    def __init__(self,
                 name: str,
                 x_span: tuple | Span,
                 y_span: tuple | Span,
                 add_self=True,
                 **kwargs):
        self.x_span, self.y_span = Span(*x_span), Span(*y_span)
        super().__init__(name, np.array([self.x_span.start, self.y_span.start]), **kwargs)
        self.add_self = add_self
        self.cntr = np.array([self.x_span.cntr, self.y_span.cntr])

    def __contains__(self, pos: np.ndarray):
        return pos[0] in self.x_span and pos[1] in self.y_span

    def rand_location(self) -> np.ndarray:
        x_sigma, y_sigma = len(self.x_span) / 6, len(self.y_span) / 6
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
    subregions: list[GeoRegion]

    def __init__(self, name, x_span: tuple | Span = (-1, -1), y_span: tuple | Span = (-1, -1), **kwargs):
        super().__init__(name, x_span, y_span, **kwargs)

    @property
    def buildings(self) -> list[GeoRegion]:
        if self.level == 1:
            return [subregion for subregion in self.subregions if subregion.add_self]
        res = []
        for subregion in self.subregions:
            assert isinstance(subregion, GeoDistrict), subregion.__class__
            res.extend(subregion.buildings)
        return res

    @property
    def roads(self) -> list[GeoRegion]:
        if self.level == 1:
            return [subregion for subregion in self.subregions if not subregion.add_self]
        res = []
        for subregion in self.subregions:
            assert isinstance(subregion, GeoDistrict)
            res.extend(subregion.roads)
        return res

    @property
    def ports(self) -> list[GeoPort]:
        res = []
        for building in self:
            res.extend(building.ports)
        return res

    @staticmethod
    def _wrapped(target: GeoRegion, stop_level: int) -> 'GeoDistrict':
        current_target = target
        index = 0
        while current_target.level < stop_level:
            current_target = GeoDistrict(f'Wrapper #{index} of {target.na}', target.x_span,
                                         target.y_span)(current_target)
            index += 1
        return current_target

    @classmethod
    def _get_ports(cls, region1: GeoRegion, region2: GeoRegion) -> tuple[GeoPort, GeoPort]:
        x_overlapped_span = Span.overlapped_span(region1.x_span, region2.x_span)
        y_overlapped_span = Span.overlapped_span(region1.y_span, region2.y_span)
        cntr_pos = np.array([x_overlapped_span.cntr, y_overlapped_span.cntr])
        if len(x_overlapped_span) > len(y_overlapped_span):  # vertical
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

        root_port1 = cls.port_type(f'AP[{region2}->{region1}]', pos1).slaved(master=region1)
        root_port2 = cls.port_type(f'AP[{region1}->{region2}]', pos2).slaved(master=region2)

        return root_port1, root_port2


if __name__ == '__main__':
    class _Test:
        print(GeoDistrict.port_type)
