"""Standard Elements for Building a Virtual City"""
from Codes.vcity.geography_layer import GeoRegion
from Codes.tools import Span
__all__ = ['CityCtor', 'Element', 'Road', 'Building', 'ResidentialBd', 'BusinessBd', 'Square']


class Element(GeoRegion):
    """Base class for all elements. May be override to add methods for elements.
    The overridden class may have some additional methods that every elements can preform"""

    def __getattr__(self, item):
        print(f'{self.__class__} objects do not have attribute \'{item}\'. You may need to'
              f'use CityCtor.configure to bind you own element type')


class Road(Element):
    """Default Road."""
    cls_abbrev = 'Rd'

    def __init__(self, name: str, x_span: tuple | Span, y_span: tuple | Span, add_self=False, **kwargs):
        if add_self:
            raise RuntimeWarning(f'A road should have add_self=False')
        super().__init__(name, x_span, y_span, False, **kwargs)


class Building(Element):
    """Default Building."""
    cls_abbrev = 'Bd'

    def __init__(self, name: str, x_span: tuple | Span, y_span: tuple | Span, add_self=True, **kwargs):
        # TODO: allow multiple floors
        if not add_self:
            raise RuntimeWarning(f'A building should have add_self=True')
        super().__init__(name, x_span, y_span, True, **kwargs)


class ResidentialBd(Building):
    cls_abbrev = 'RBd'


class BusinessBd(Building):
    cls_abbrev = 'BBd'


class Square(Building):
    cls_abbrev = 'Sqr'


class CityCtor:
    """A singleton that functions as a constructing interface.
    Users can use this interface to specify how to construct buildings
    and roads"""
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance:
            return cls.instance
        return super().__new__(cls)

    def __init__(self):
        if CityCtor.instance is None:
            self.ele = Element
            self.rd = Road
            self.rbd = ResidentialBd
            self.bbd = BusinessBd
            self.sqr = Square
            CityCtor.instance = self

    def configure(self, road=Road, rbd=ResidentialBd, bbd=BusinessBd, sqr=Square):
        assert issubclass(road, Road)
        assert issubclass(rbd, ResidentialBd)
        assert issubclass(bbd, BusinessBd)
        assert issubclass(sqr, Square)

        self.rd = road
        self.rbd = rbd
        self.bbd = bbd
        self.sqr = sqr
