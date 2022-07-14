"""Sample Virtual City"""
from Codes.vcity.elements import *
from Codes.vcity.geography_layer import GeoDistrict
from Codes.tools import Span
__all__ = ['Compound', 'Row', 'Trd', 'Rlt', 'Vcity']


class Compound(GeoDistrict):
    """The base class of compounds. Compounds are special geo-districts that share a same constructor"""
    def __init__(self, refer_pos, **kwargs):
        super().__init__(**kwargs)
        self.refer_x, self.refer_y = refer_pos
        self.rds: list[Road] = []
        self.rbds: list[ResidentialBd] = []
        self.bbds: list[BusinessBd] = []
        self.sqrs: list[Square] = []

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


class Row(Compound):
    """
    row of buildings, not connected and cannot be connected with each other (because it is meaningless).
    :param refer_pos: reference position
    :param x_lens: x_len of each building
    :param y_lens: y_len of each building
    Note: one of x_lens and y_lens should have only one element.
    """
    cls_abbrev = 'Row'

    def __init__(self, name: str, refer_pos: tuple, x_lens: list[int], y_lens: list[int], mode: str):
        assert mode in ['rbd', 'bbd', 'sqr']
        ctor = CityCtor()
        region_t = getattr(ctor, mode)

        assert len(x_lens) == 1 or len(y_lens) == 1
        super().__init__(name=name, refer_pos=refer_pos)
        curr_x, curr_y = self.refer_x, self.refer_y
        regions = []

        if len(x_lens) == 1:  # vertical
            self.len = len(y_lens)
            for i, _len in enumerate(y_lens):
                regions.append(region_t(name=str(i),
                                        x_span=Span(curr_x, _len=x_lens[0]),
                                        y_span=Span(curr_y, _len=_len)
                                        ))
                curr_y += _len

        else:  # horizontal
            self.len = len(x_lens)
            for i, _len in enumerate(x_lens):
                regions.append(region_t(name=str(i),
                                        x_span=Span(curr_x, _len=_len),
                                        y_span=Span(curr_y, _len=y_lens[0])
                                        ))
                curr_x += _len

        self(*regions)
        setattr(self, mode + 's', regions)

    def all_accessible_names(self) -> list[str]:
        return [str(i) for i in range(self.len)]


class Trd(Compound):
    """Typical Residential District. (110x100)"""
    cls_abbrev = 'TRD'

    def __init__(self, name, refer_pos):
        ctor = CityCtor()
        super().__init__(name=name, refer_pos=refer_pos)
        axis = ctor.rd(name='axis',
                       x_span=Span(self.refer_x + 50, _len=10),
                       y_span=Span(self.refer_y, _len=100)
                       )
        regions = [axis]
        self.rds = [axis]
        connections = []
        curr_y = self.refer_y
        for i in range(5):
            # left half
            regions.extend([
                current_row := Row(f'L{i}', (self.refer_x, curr_y), [10] * 5, [10], 'rbd'),
                current_road := ctor.rd(name=f'l{i}', x_span=Span(self.refer_x, _len=50),
                                        y_span=Span(curr_y + 10, _len=5))
            ])
            for house in current_row:
                connections.append((house, current_road))
            connections.append((axis, current_road))

            self.rbds += current_row.rbds
            self.rds.append(current_road)

            # right half
            regions.extend([
                current_row := Row(f'R{i}', (self.refer_x + 60, curr_y), [10] * 5, [10], 'rbd'),
                current_road := ctor.rd(name=f'r{i}', x_span=Span(self.refer_x + 60, _len=50),
                                        y_span=Span(curr_y + 10, _len=5))
            ])
            for house in current_row:
                connections.append((house, current_road))
            connections.append((axis, current_road))

            self.rbds += current_row.rbds
            self.rds += [current_road]

            curr_y += 20

        self(*regions, connections=connections)

    def all_accessible_names(self) -> list[str]:
        return ['axis']


'''class Tbd(Compound):
    """Typical Business District"""
    pass


class Tsd(Compound):
    """Typical Shopping District"""
    pass'''


class Rlt(Compound):
    """Road Lattice"""
    cls_abbrev = 'Rlt'

    def __init__(self, name: str, refer_pos: tuple[int, int], road_width: int, road_xs: list[int], road_ys: list[int]):
        ctor = CityCtor()
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
            horizontals.append(ctor.rd(name=f'h{i}', x_span=x_span, y_span=Span(curr_y, _len=road_width)))

        # creating vertical roads
        for i, curr_x in enumerate(road_xs):
            verticals.append(ctor.rd(name=f'v{i}', x_span=Span(curr_x, _len=road_width), y_span=y_span))

        for h_road in horizontals:
            for v_road in verticals:
                connections.append((h_road, v_road))

        self.rds = horizontals + verticals
        self(*self.rds, connections=connections)

    def all_accessible_names(self) -> list[str]:
        return [rd.rna for rd in self.rds]


class Vcity(Compound):
    cls_abbrev = 'Vct'

    def __init__(self, refer_pos=(0, 0), **kwargs):
        if tuple(refer_pos) != (0, 0):
            raise ValueError('Vcity must be built on (0, 0)')

        super().__init__(name='The City', refer_pos=(0, 0), **kwargs)
        ctor = CityCtor()
        self(rlt := Rlt('main', (0, 0), 5, [0, 115, 230, 345], [0, 105, 210, 315]),
             trd1 := Trd('1', (5, 5)),
             trd2 := Trd('2', (5, 215)),
             trd3 := Trd('3', (120, 110)),
             trd4 := Trd('4', (235, 5)),
             trd5 := Trd('5', (235, 215)),
             s1 := ctor.sqr(name='S1', x_span=(5, 115), y_span=(110, 210)),
             s2 := ctor.sqr(name='S2', x_span=(120, 230), y_span=(5, 105)),
             s3 := ctor.sqr(name='S3', x_span=(120, 230), y_span=(215, 315)),
             s4 := ctor.sqr(name='S4', x_span=(235, 345), y_span=(110, 210)),
             connections=[(trd1['axis'], rlt['h0']), (trd1['axis'], rlt['h1']),
                          (trd2['axis'], rlt['h2']), (trd2['axis'], rlt['h3']),
                          (trd3['axis'], rlt['h1']), (trd3['axis'], rlt['h2']),
                          (trd4['axis'], rlt['h0']), (trd4['axis'], rlt['h1']),
                          (trd5['axis'], rlt['h2']), (trd5['axis'], rlt['h3']),
                          (s1, rlt['v0']), (s1, rlt['v1']), (s1, rlt['h1']), (s1, rlt['h2']),
                          (s2, rlt['v1']), (s2, rlt['v2']), (s2, rlt['h0']), (s2, rlt['h1']),
                          (s3, rlt['v1']), (s3, rlt['v2']), (s3, rlt['h2']), (s3, rlt['h3']),
                          (s4, rlt['v2']), (s4, rlt['v3']), (s4, rlt['h1']), (s4, rlt['h2'])]
             )
        self.size = (350, 320)
        self.rbds = trd1.rbds + trd2.rbds + trd3.rbds + trd4.rbds + trd5.rbds
        self.rds = trd1.rds + trd2.rds + trd3.rds + trd4.rds + trd5.rds + rlt.rds
        self.sqrs = [s1, s2, s3, s4]

    def all_accessible_names(self) -> list[str]:
        return []


if __name__ == '__main__':
    from Codes.vcity.display_support import Displayer
    Displayer(city := Vcity(), (0, 350), (0, 320)).refresh()
    print(city['1']['l4'].master.find_port(city['main']))
    print(city['main'].level)
    # print(city['1']['l4'].master.accessible_from()[city['main']])
    Displayer.display(True)

