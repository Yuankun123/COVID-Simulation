from tools import REDTEXT, WHITETEXT
import math


class AbstractPart:
    """An abstract part is the smallest object in a connection level,
    it can be an abstract region or even an abstract block"""
    def __init__(self, name: str): self.na = name
    def __repr__(self): return REDTEXT + self.na + WHITETEXT


class AbstractRegion(AbstractPart):
    """An abstract region is the smallest object connectable by protocols"""
    def __init__(self, name: str, add_self=True, **kwargs):
        super(AbstractRegion, self).__init__(name)
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

    def connection_info(self):
        res = f'{self.region_na}. ' \
              f'Having protocols to: {", ".join([repr(protocol.other_side(self)) for protocol in self.protocols])}, '
        for region, distance in self.connect_dict.items():
            res += f'Having access to {region} in distance {distance} '
        return res

    def find_parts(self, target: 'AbstractRegion') -> list[AbstractPart]:
        assert target != self
        candidates: list[AbstractPart] = []
        min_distance = math.inf
        for protocol in self.protocols:
            if self.connect_dict[protocol][target] <= min_distance:
                candidates.append(protocol.port_on(self))
                min_distance = self.connect_dict[protocol][target]
        return candidates


class AbstractProtocol:
    """an abstract protocol consist of two abstract regions and two abstract ports"""

    def __init__(self, region1: AbstractRegion, region2: AbstractRegion,
                 port1: AbstractPart = None, port2: AbstractPart = None, **kwargs):
        self.protocol_na = f'P[{region1}|{region2}]'
        if not port1:
            port1 = AbstractPart(f'Port1 of {self}')
        if not port2:
            port2 = AbstractPart(f'Port2 of {self}')

        assert isinstance(region1, AbstractRegion), f'{region1} is not an abstract region'
        assert isinstance(region2, AbstractRegion), f'{region2} is not an abstract region'
        assert isinstance(port1, AbstractPart), f'{port1} is not an abstract port'
        assert isinstance(port2, AbstractPart), f'{port2} is not an abstract port'

        port1.port_na = f'Port1 of {self}'
        port2.port_na = f'Port2 of {self}'
        self.connect_dict: dict[AbstractRegion, tuple[AbstractPart, AbstractRegion]] = {
            region1: (port1, region2),
            region2: (port2, region1)
        }

    def other_side(self, origin: AbstractRegion) -> AbstractRegion: return self.connect_dict[origin][1]
    def port_on(self, region: AbstractRegion) -> AbstractPart: return self.connect_dict[region][0]

    def accessible_from(self, origin: AbstractRegion, current_distance: int = 0, path: list[AbstractRegion] = None):
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

    def place_between(self, region1: AbstractRegion, region2: AbstractRegion):
        region1.connect_dict[self] = {}
        region2.connect_dict[self] = {}

    def __repr__(self):
        return self.protocol_na


class ComplexRegion(AbstractRegion):
    """A complex region preserve all features of a region. It can also contains inner regions
    that are either complex or not"""
    default_parts_type = AbstractPart

    def __init__(self, name, add_self=True, inner_parts_type=None, **kwargs):
        super(ComplexRegion, self).__init__(name, add_self, **kwargs)
        self._part_name_dict: dict[str, AbstractPart] = {}
        self.inner_protocols: list[AbstractProtocol] = []
        if inner_parts_type:
            self.inner_parts_type = inner_parts_type
        else:
            self.inner_parts_type = self.default_parts_type

    @property
    def parts(self) -> list[AbstractPart]: return list(self._part_name_dict.values())
    def __getitem__(self, item: str) -> AbstractPart: return self._part_name_dict[item]
    def __setitem__(self, key: str, value: AbstractPart): self._part_name_dict[key] = value

    def __contains__(self, item: str | AbstractPart):
        """item can be the name of the region of the region object"""
        return item in self._part_name_dict.keys() or item in self._part_name_dict.values()

    def recursively_contains(self, item: str | AbstractPart):
        if item in self:
            return True
        for part in self.parts:
            if hasattr(part, 'recursively_contains') and part.recursively_contains(item):
                return True
        return False

    def add_inner_region(self, name: str, add_self=True, **kwargs):
        assert name not in self, f'Name {name} already exists'
        self[name] = self.inner_region_type(name, add_self=add_self, **kwargs)
        return self[name]

    def connect(self, region_na1: str, region_na2: str, **kwargs):
        assert region_na1 in self, f'Name {region_na1} dose not exist'
        assert region_na2 in self, f'Name {region_na2} does not exist'
        region1, region2 = self[region_na1], self[region_na2]
        new_protocol = AbstractProtocol(region1, region2, port1, port2, **kwargs)
        new_protocol.place_between(region1, region2)
        self.inner_protocols.append(new_protocol)

    def finish_inner_construction(self):
        for region in self.inner_regions:
            region.finish_construction()


class ProtocolType(type):
    """a meta class used to generate protocol types"""
    pass


if __name__ == '__main__':
    class _Test:
        host = ComplexRegion('1st host')
        host.add_inner_region('A')
        host.add_inner_region('B')
        host.add_inner_region('C')
        host.add_inner_region('D')
        host.add_inner_region('E')
        host.add_inner_region('F')
        host.connect('A', 'B')
        host.connect('B', 'C')
        host.connect('C', 'D')
        host.connect('D', 'E')
        host.connect('E', 'F')
        host.connect('F', 'A')
        host.connect('B', 'E')
        host.finish_inner_construction()

        for region in host.inner_regions:
            print(region.connect_dict)
            print(region.finished)

        print(host['A'].find_ports(host['E']))
