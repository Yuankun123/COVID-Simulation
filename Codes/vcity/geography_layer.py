import random
import time
import numpy as np
from Codes.tools import Span
from Codes.vcity.connection_layer import *
__all__ = ['GeoPart', 'GeoRegion', 'GeoDistrict']


class GeoPart(AbstractPart):
    cls_abbrev = 'GP'

    def __init__(self, name: str, pos: np.ndarray, **kwargs):
        super(GeoPart, self).__init__(name, **kwargs)
        self.pos = pos


class GeoRegion(AbstractRegion):
    """Every Building is a rectangle"""
    cls_abbrev = 'GR'

    def __init__(self,
                 name: str,
                 x_span: tuple | Span,
                 y_span: tuple | Span,
                 add_self=True,
                 **kwargs):
        self.x_span, self.y_span = Span(*x_span), Span(*y_span)
        super().__init__(name, add_self=add_self, **kwargs)
        self.sw_pos = np.array([self.x_span.start, self.y_span.start])
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


class GeoDistrict(AbstractDistrict, is_wrap_type=True):
    part_type = GeoPart
    cls_abbrev = 'GD'

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

    @property
    def ports(self) -> list[GeoPart]:
        res = []
        for building in self:
            res.extend(building.ports)
        return res

    @classmethod
    def _get_ports(cls, region1: GeoRegion, region2: GeoRegion) -> tuple[GeoPart, GeoPart]:
        x_overlapped_span = Span.overlapped_span(region1.x_span, region2.x_span)
        y_overlapped_span = Span.overlapped_span(region1.y_span, region2.y_span)
        cntr_pos = np.array([x_overlapped_span.cntr, y_overlapped_span.cntr])
        if len(y_overlapped_span) == 0:  # vertical
            if region1.y_span.cntr > region2.y_span.cntr:  # region1 on top
                pos1 = cntr_pos + np.array([0, 1])
                pos2 = cntr_pos - np.array([0, 1])
            else:  # region2 on top
                pos1 = cntr_pos - np.array([0, 1])
                pos2 = cntr_pos + np.array([0, 1])
        elif len(x_overlapped_span) == 0:  # horizontal
            if region1.x_span.cntr > region2.x_span.cntr:  # region1 on the right
                pos1 = cntr_pos + np.array([1, 0])
                pos2 = cntr_pos - np.array([1, 0])
            else:  # region2 on the right
                pos1 = cntr_pos - np.array([1, 0])
                pos2 = cntr_pos + np.array([1, 0])

        else:  # overlap
            pos1 = pos2 = cntr_pos

        assert pos1 in region1, f'pos: {pos1} is not in region: {region1}'
        assert pos2 in region2, f'pos: {pos2} is not in region: {region2}'

        root_port1 = cls.part_type(f'[{region2}->{region1}]', pos1).add_master(master=region1)
        root_port2 = cls.part_type(f'[{region1}->{region2}]', pos2).add_master(master=region2)

        return root_port1, root_port2


if __name__ == '__main__':
    class _Test:
        print(GeoDistrict.part_type)
