import sys
sys.path.append('C:\\Users\\Kunko\\Documents\\Github\\COVID-Simulation')
from Codes.vcity.geography_layer import *
from Codes.vcity.elements import *
from Codes.vcity.compound import Vcity
from Codes.vcity.display_support import Displayer

if __name__ == '__main__':
    class _Test:
        Displayer(Vcity(), (0, 350), (0, 320)).refresh()
        Displayer.display(True)
