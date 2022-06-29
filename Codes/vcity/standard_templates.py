"""Standard Elements for Building a Virtual City"""
from Codes.vcity.geography_layer import GeoDistrict, GeoRegion
from Codes.tools import Span
from inspect import signature
__all__ = ['CityCtor', 'Row', 'Trd', 'Tbd', 'Tsd', 'Rlt']


class CityCtor:
    """A singleton that functions as a constructing interface.
    Users can use this interface to specify how to construct buildings
    and roads"""
    instance = None

    class __Road(GeoRegion):
        """Default Road."""
        cls_abbrev = 'Rd'

        def __init__(self, name: str, x_span: tuple | Span, y_span: tuple | Span, add_self=False, **kwargs):
            if add_self:
                raise RuntimeWarning(f'A road should have add_self=False')
            super().__init__(name, x_span, y_span, False, **kwargs)

    class __Building(GeoRegion):
        """Default Building."""
        cls_abbrev = 'Bd'

        def __init__(self, name: str, x_span: tuple | Span, y_span: tuple | Span, add_self=True, **kwargs):
            # TODO: allow multiple floors
            if not add_self:
                raise RuntimeWarning(f'A building should have add_self=True')
            super().__init__(name, x_span, y_span, True, **kwargs)

    road_ctor_sig = signature(__Road).parameters.keys()
    bld_ctor_sig = signature(__Building).parameters.keys()

    def __new__(cls, *args, **kwargs):
        if cls.instance:
            return cls.instance
        return super().__new__(cls)

    def __init__(self):
        self.road = self.__Road
        self.bld = self.__Building
        CityCtor.instance = self

    def configure(self, road_ctor=None, bld_ctor=None):
        if not (callable(road_ctor) and callable(bld_ctor)):
            raise TypeError(f'Constructor function not callable')

        if not signature(road_ctor).parameters.keys() == CityCtor.road_ctor_sig:
            raise ValueError('Road constructor having incorrect signature')

        if not signature(bld_ctor).parameters.keys() == CityCtor.bld_ctor_sig:
            raise ValueError('Building constructor having incorrect signature')

        self.road = road_ctor
        self.bld = bld_ctor


class Element(GeoDistrict):
    """The base class of elements. Elements are special geo-districts that share a same constructor"""
    ctor = CityCtor()

    def __init__(self, refer_pos, **kwargs):
        super().__init__(**kwargs)
        self.refer_x, self.refer_y = refer_pos

    def all_accessible_names(self) -> list[str]:
        """Give out a list of names that are accessible for external connections. Need to be implemented
        in each element"""
        raise NotImplementedError

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            print(self.direct_subregions.keys())
            raise RuntimeError(f'Name {item} not found. Valid names are {self.all_accessible_names()}')


class Row(Element):
    """
    row of buildings, not connected and cannot be connected with each other (because it is meaningless).
    :param refer_pos: reference position
    :param x_lens: x_len of each building
    :param y_lens: y_len of each building
    Note: one of x_lens and y_lens should have only one element.
    """
    cls_abbrev = 'Row'

    def __init__(self, name: str, refer_pos: tuple, x_lens: list[int], y_lens: list[int]):
        assert len(x_lens) == 1 or len(y_lens) == 1
        super().__init__(name=name, refer_pos=refer_pos)
        curr_x, curr_y = self.refer_x, self.refer_y
        regions = []

        if len(x_lens) == 1:  # vertical
            self.len = len(y_lens)
            for i, _len in enumerate(y_lens):
                regions.append(self.ctor.bld(name=str(i),
                                             x_span=Span(curr_x, _len=x_lens[0]),
                                             y_span=Span(curr_y, _len=_len)
                                             ))
                curr_y += _len

        else:  # horizontal
            self.len = len(x_lens)
            for i, _len in enumerate(x_lens):
                regions.append(self.ctor.bld(name=str(i),
                                             x_span=Span(curr_x, _len=_len),
                                             y_span=Span(curr_y, _len=y_lens[0])
                                             ))
                curr_x += _len

        self(*regions)

    def all_accessible_names(self) -> list[str]:
        return [str(i) for i in range(self.len)]


class Trd(Element):
    """Typical Residential District. (110x100)"""
    cls_abbrev = 'TRD'

    def __init__(self, name, refer_pos):
        super().__init__(name=name, refer_pos=refer_pos)
        axis = self.ctor.road(name='axis',
                              x_span=Span(self.refer_x + 50, _len=10),
                              y_span=Span(self.refer_y, _len=100)
                              )

        curr_y = self.refer_y
        regions = [axis]
        connections = []
        for i in range(5):
            regions.extend([
                current_row := Row(f'L{i}', (self.refer_x, curr_y), [10] * 5, [10]),
                current_road := self.ctor.road(f'l{i}', Span(self.refer_x, _len=50), Span(curr_y + 10, _len=5))
            ])
            for house in current_row:
                connections.append((house, current_road))
            connections.append((axis, current_road))

            regions.extend([
                current_row := Row(f'R{i}', (self.refer_x + 60, curr_y), [10] * 5, [10]),
                current_road := self.ctor.road(f'r{i}', Span(self.refer_x + 60, _len=50), Span(curr_y + 10, _len=5))
            ])
            for house in current_row:
                connections.append((house, current_road))
            connections.append((axis, current_road))

            curr_y += 20

        self(*regions, connections=connections)

    def all_accessible_names(self) -> list[str]:
        return ['axis']


class Tbd(Element):
    """Typical Business District"""
    pass


class Tsd(Element):
    """Typical Shopping District"""
    pass


class Rlt(Element):
    """Road Lattice"""
    cls_abbrev = 'Rlt'

    def __init__(self, name: str, refer_pos: tuple[int, int], road_width: int, road_xs: list[int], road_ys: list[int]):
        super().__init__(name=name, refer_pos=refer_pos)
        assert road_xs[0] == self.refer_x
        assert road_ys[0] == self.refer_y
        horizontals = []
        verticals = []
        connections = []
        x_span = Span(self.refer_x, _len=road_xs[-1] + road_width)
        y_span = Span(self.refer_y, _len=road_ys[-1] + road_width)

        # creating horizontal roads
        for i, curr_y in enumerate(road_ys):
            horizontals.append(self.ctor.road(f'h{i}', x_span=x_span, y_span=Span(curr_y, _len=road_width)))

        # creating vertical roads
        for i, curr_x in enumerate(road_xs):
            verticals.append(self.ctor.road(f'v{i}', x_span=Span(curr_x, _len=road_width), y_span=y_span))

        for h_road in horizontals:
            for v_road in verticals:
                connections.append((h_road, v_road))

        self(*(horizontals + verticals), connections=connections)

    def all_accessible_names(self) -> list[str]:
        return [road.rna for road in self.roads]


if __name__ == '__main__':
    from Codes.vcity.display_support import Displayer
    road_lattice = Trd('1', (5, 5))
    print(road_lattice.all_accessible_names())
    print(road_lattice['L0'])
    print(road_lattice.subparts)
    Displayer(road_lattice, (0, 320), (0, 365)).refresh()
    Displayer.display(True)
