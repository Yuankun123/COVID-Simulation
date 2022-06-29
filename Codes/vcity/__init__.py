from Codes.vcity.geography_layer import *
from Codes.vcity.standard_templates import CityCtor
from Codes.vcity.compound import Vcity
from Codes.vcity.display_support import Displayer

if __name__ == '__main__':
    class _Test:
        Displayer(Vcity(), (0, 350), (0, 320)).refresh()
        Displayer.display(True)
