"""Standard Templates for Building a Virtual City"""
from geography_layer import (GeoDistrict as Gd,
                             GeoRegion as Gr)
from tools import Span
from display_support import Displayer


class Row(Gd):
    """
    row of buildings, not connected and cannot be connected with each other (because it is meaningless).
    :param refer_pos: reference position
    :param x_lens: x_len of each building
    :param y_lens: y_len of each building
    Note: one of x_lens and y_lens should have only one element.
    """

    def __init__(self, refer_pos: tuple, x_lens: list[int], y_lens: list[int]):
        assert len(x_lens) == 1 or len(y_lens) == 1
        curr_x, curr_y = refer_x, refer_y = refer_pos
        super().__init__('row', Span(refer_x, _len=sum(x_lens)), Span(refer_y, _len=sum(y_lens)))
        regions = []

        if len(x_lens) == 1:  # vertical

            for i, _len in enumerate(y_lens):
                regions.append(Gr(f'R#{i} of the row', Span(curr_x, _len=x_lens[0]), Span(curr_y, _len=_len),
                                  add_self=True))
                curr_y += _len

        else:  # horizontal
            for i, _len in enumerate(x_lens):
                regions.append(Gr(f'R#{i} of the row', Span(curr_x, _len=_len), Span(curr_y, _len=y_lens[0]),
                                  add_self=True))
                curr_x += _len

        self(*regions)


class Trd(Gd):
    """Typical Residential District."""

    def __init__(self, refer_pos):
        refer_x, refer_y = refer_pos
        super().__init__('tra', Span(refer_x, _len=110), Span(refer_y, _len=100))
        self.axis = Gr('', Span(refer_x + 50, _len=10), Span(refer_y, _len=100), add_self=False)

        curr_y = refer_y
        regions = [self.axis]
        connections = []
        for i in range(5):
            regions.extend([
                current_row := Row((refer_x, curr_y), [10]*5, [10]),
                current_road := Gr('', (0, 50), Span(curr_y + 10, _len=5), add_self=False)
            ])
            for house in current_row:
                connections.append((house, current_road))
            connections.append((self.axis, current_road))

            regions.extend([
                current_row := Row((refer_x + 60, curr_y), [10] * 5, [10]),
                current_road := Gr('', (60, 110), Span(curr_y + 10, _len=5), add_self=False)
            ])
            for house in current_row:
                connections.append((house, current_road))
            connections.append((self.axis, current_road))

            curr_y += 20

        self(*regions, connections=connections)


class Tbd(Gd):
    """Typical Business District"""
    pass


class Tsd(Gd):
    """Typical Shopping District"""
    pass


if __name__ == '__main__':
    trail_city = Trd((0, 0))

    Displayer(trail_city, None).refresh()
    Displayer.display(True)
