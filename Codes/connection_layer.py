from tools import REDTEXT, WHITETEXT
import math


class AbstractProtocol:
    def __init__(self, region1: 'AbstractRegion', region2: 'AbstractRegion', *args, **kwargs):
        self.region1 = region1
        self.region2 = region2

    def other_side(self, origin: 'AbstractRegion') -> 'AbstractRegion':
        if origin == self.region1:
            return self.region2
        else:
            return self.region1

    def accessible_from(self, origin: 'AbstractRegion', current_distance: int = 0, path: list['AbstractRegion'] = None):
        res = {}
        source_region = self.other_side(origin)
        print(f'Getting view of {source_region} through {self}')
        if source_region in path:
            print('Meet the path')
            return {}
        path_copy = path[:]
        path.append(source_region)
        for region, distance in source_region.accessible_from(self, current_distance, path).items():
            if region not in path_copy:
                res[region] = distance + 1
        return res

    def place_between(self, region1, region2):
        region1.connect_dict[self] = {}
        region2.connect_dict[self] = {}

    def __repr__(self):
        return f'P[{self.region1}|{self.region2}]'


class AbstractRegion:
    def __init__(self, name: str, *args, add_self=True, **kwargs):
        self.na = name
        self.add_self = add_self
        self.connect_dict: dict[AbstractProtocol, dict[AbstractRegion: int]] = {}
        self.finished = False  # whether the connection dict has been generated

    @property
    def protocols(self):
        return list(self.connect_dict.keys())

    def _generate_connection_dict(self,
                                  current_distance: int = 0,
                                  root_path: list['AbstractRegion'] = None):
        assert not self.finished
        top_level = False
        if root_path is None:
            root_path = []
            top_level = True
        for protocol in self.protocols:
            path = root_path + [self]
            print('****start a branch')
            print(f'{self}, Processing Protocol:{protocol}')
            current_distance += 1  # the distance to the next region
            self.connect_dict[protocol] = protocol.accessible_from(self, current_distance, path)
        if top_level:
            self.finished = True

    def accessible_from(self, origin, current_distance: int = 0, path: list['AbstractRegion'] = None) -> \
            dict['AbstractRegion', int]:
        print(f'Getting accessible regions from {self} through protocols except {origin}')
        if not self.finished:
            self._generate_connection_dict(current_distance, path)
        else:
            print(f'{self} already has connection dict')

        res = {}
        if self.add_self:
            res = {self: 0}
        for protocol in self.protocols:
            if protocol != origin:
                for region, distance in self.connect_dict[protocol].items():
                    if region != self and (region not in res.keys() or distance < res[region]):
                        res[region] = distance
        return res

    def finish_construction(self):
        print(f'Start to process {self}')
        self._generate_connection_dict()
        print(f'########{self} finished')

    def find_protocols(self, target: 'AbstractRegion') -> list[AbstractProtocol]:
        assert target != self
        candidates: list[AbstractProtocol] = []
        min_distance = math.inf
        for protocol in self.protocols:
            if self.connect_dict[protocol][target] <= min_distance:
                candidates.append(protocol)
                min_distance = self.connect_dict[protocol][target]
        return candidates

    def __repr__(self):
        return REDTEXT + self.na + WHITETEXT

    def detail_info(self):
        res = f'{self.na}. ' \
              f'Having protocols to: {", ".join([repr(protocol.other_side(self)) for protocol in self.protocols])}, '
        for region, distance in self.connect_dict.items():
            res += f'Having access to {region} in distance {distance} '
        return res


class AbstractBlock:
    def __init__(self):
        self.regions: dict[str, AbstractRegion] = {}

    def add_region(self, name, *args, add_self=True, **kwargs):
        self.regions[name] = AbstractRegion(name, *args, add_self, **kwargs)

    def connect(self, region_na1, region_na2, *args, **kwargs):
        assert region_na1 in self.regions.keys()
        assert region_na2 in self.regions.keys()
        region1, region2 = self.regions[region_na1], self.regions[region_na2]
        new_protocol = AbstractProtocol(region1, region2, *args, **kwargs)
        new_protocol.place_between(region1, region2)


if __name__ == '__main__':
    class _Test:
        host = AbstractBlock()
        host.add_region('A')
        host.add_region('B')
        host.add_region('C')
        host.add_region('D')
        host.add_region('E')
        host.add_region('F')
        host.connect('A', 'B')
        host.connect('B', 'C')
        host.connect('C', 'D')
        host.connect('D', 'E')
        host.connect('E', 'F')
        host.connect('F', 'A')
        host.connect('B', 'E')

        for region in host.regions.values():
            region.finish_construction()
        for region in host.regions.values():
            print(region.connect_dict)
            print(region.finished)

        print(host.regions['A'].find_protocols(host.regions['E']))
