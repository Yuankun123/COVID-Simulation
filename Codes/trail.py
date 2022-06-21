from virtual_city import VirtualCity
import matplotlib.pyplot as plt


class DVirtualCity(VirtualCity):
    def __init__(self, size):

        super().__init__(size)
        plt.ion()
        plt.figure(figsize=(10, 10), dpi=80)
        axes = plt.gca()
        axes.set_aspect(1)

    def display(self):
        plt.cla()
        plt.xlim(0, self.size - 1)
        plt.ylim(0, self.size - 1)
        axes = plt.gca()
        for region in self.buildings:
            axes.add_artist(plt.Rectangle(xy=tuple(region.sw_loc), width=region.x_span.span, height=region.y_span.span, 
                                          fill=False))
        for road in self.roads:
            axes.add_artist(plt.Rectangle(xy=tuple(road.sw_loc), width=road.x_span.span, height=road.y_span.span, 
                                          fill=True, facecolor='#e3d1d1', edgecolor='black'))

        plt.scatter(x=[protocol.pos[0] for protocol in self.protocols],
                    y=[protocol.pos[1] for protocol in self.protocols],
                    marker='x')


vcity = DVirtualCity(1000)
'''vcity.build_road({'R1': (350, 300), 'R4': (450, 300)}, 5)
vcity.build_road({'R2': (350, 500), 'T1': (450, 500)}, 5)
vcity.build_road({'R3': (350, 700), 'T2': (450, 700)}, 5)
vcity.build_road({'R4': (550, 300), 'T3': (650, 300)}, 5)
vcity.build_road({'T1': (550, 500), 'T4': (650, 500)}, 5)
vcity.build_road({'T2': (550, 700), 'T5': (650, 700)}, 5)

vcity.build_road({'R1': (300, 350), 'R2': (300, 450)}, 5)
vcity.build_road({'R4': (500, 350), 'T1': (500, 450)}, 5)
vcity.build_road({'T3': (700, 350), 'T4': (700, 450)}, 5)
vcity.build_road({'R2': (300, 550), 'R3': (300, 650)}, 5)
vcity.build_road({'T1': (500, 550), 'T2': (500, 650)}, 5)
vcity.build_road({'T4': (700, 550), 'T5': (700, 650)}, 5)'''
vcity.add_inner_region('R1', (400, 500), (400, 500))
vcity.add_inner_region('R2', (400, 500), (500, 600))
vcity.add_inner_region('R3', (500, 600), (500, 600))
vcity.add_inner_region('R4', (500, 600), (400, 500))
vcity.add_inner_region('Ro1', (390, 400), (400, 610), False)
vcity.add_inner_region('Ro2', (400, 610), (600, 610), False)
vcity.add_inner_region('Ro3', (600, 610), (390, 600), False)
vcity.add_inner_region('Ro4', (390, 600), (390, 400), False)
vcity.connect('R1', 'Ro1', (400, 550))
vcity.connect('R1', 'Ro2', (450, 600))
vcity.connect('R2', 'Ro2', (550, 600))
vcity.connect('R2', 'Ro3', (600, 550))
vcity.connect('R3', 'Ro3', (600, 450))
vcity.connect('R3', 'Ro4', (550, 400))
vcity.connect('R4', 'Ro4', (450, 400))
vcity.connect('R4', 'Ro1', (400, 450))

vcity.finish_construction()
vcity.display()
plt.pause(10000)
