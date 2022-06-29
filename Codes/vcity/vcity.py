"""Sample Virtual City"""
from standard_templates import *
from geography_layer import *

__all__ = ['Vcity']


class Vcity(GeoDistrict):
    def __init__(self, **kwargs):
        super().__init__('The City', **kwargs)
        ctor = CityCtor()
        self(rlt := Rlt('main', (0, 0), 5, [0, 115, 230, 345], [0, 105, 210, 315]),
             trd1 := Trd('1', (5, 5)),
             trd2 := Trd('2', (5, 215)),
             trd3 := Trd('3', (120, 110)),
             trd4 := Trd('4', (235, 5)),
             trd5 := Trd('5', (235, 215)),
             s1 := ctor.bld('S1', x_span=(5, 115), y_span=(110, 210)),
             s2 := ctor.bld('S2', x_span=(120, 230), y_span=(5, 105)),
             s3 := ctor.bld('S3', x_span=(120, 230), y_span=(215, 315)),
             s4 := ctor.bld('S4', x_span=(235, 345), y_span=(110, 210)),
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
        self.residential_buildings = trd1.buildings + trd2.buildings + trd3.buildings + trd4.buildings \
            + trd5.buildings
        self.squares = [s1, s2, s3, s4]
        self.size = (350, 320)


if __name__ == '__main__':
    from display_support import Displayer

    Displayer(Vcity(), (0, 350), (0, 320)).refresh()
    Displayer.display(True)
