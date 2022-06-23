"""Pure Gold"""
import logging
from tools import red_text
import math
logger = logging.getLogger()


class AbstractPort:
    master: 'AbstractRegion'
    """An abstract port is the smallest object in a connection level. It is used to constitute a protocol"""
    def __init__(self, name: str, level=0, master: 'AbstractRegion' = None, **kwargs):
        assert level >= 0, 'The level of a port should be at least 0'
        self.na = name
        self.level = level
        self.master = master

    def __repr__(self):
        return self.na


class AbstractRegion(AbstractPort):
    """An abstract region is the smallest object connectable by protocols.
    It can be a member of an Abstract District"""
    master: 'AbstractDistrict'

    def __init__(self, name: str, level=1, master: 'AbstractRegion' = None, add_self=True, **kwargs):
        assert level >= 1, 'The level of a region should be at least 1'
        super(AbstractRegion, self).__init__(name, level, master)
        self.add_self = add_self
        self.connect_dict: dict[AbstractProtocol, dict[AbstractRegion: int]] = {}
        self.finished = False  # whether the connection dict has been generated

    def __repr__(self):
        return red_text(f'BR_{self.na}')

    @property
    def protocols(self):
        return list(self.connect_dict.keys())

    @property
    def ports(self) -> list[AbstractPort]:
        return [protocol.port_against(self) for protocol in self.protocols]

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
            # print('****start a branch')
            # print(f'{self}, Processing Protocol:{protocol}')
            current_distance += 1  # the distance to the next region
            self.connect_dict[protocol] = protocol.accessible_from(self, current_distance, path)
        if top_level:
            self.finished = True

    def accessible_from(self, origin=None, current_distance: int = 0, path: list['AbstractRegion'] = None) -> \
            dict['AbstractRegion', int]:
        # print(f'Getting accessible regions from {self} through protocols except {origin}')
        if not self.finished:
            self._generate_connection_dict(current_distance, path)
        else:
            pass
            # print(f'{self} already has connection dict')

        res = {}
        if self.add_self:
            res = {self: 0}
        for protocol in self.protocols:
            if protocol != origin:
                for region, distance in self.connect_dict[protocol].items():
                    if region != self and (region not in res.keys() or distance < res[region]):
                        res[region] = distance
        return res

    def connection_info(self):
        res = f'{self.na}. ' \
              f'Having protocols to: {", ".join([repr(protocol.other_side(self)) for protocol in self.protocols])}, '
        for region, distance in self.accessible_from().items():
            res += f'Having access to {region} in distance {distance} '
        return res

    def find_ports(self, target: 'AbstractRegion') -> list[AbstractPort]:
        assert target != self
        assert target.level == self.level
        candidates: list[AbstractPort] = []
        min_distance = math.inf
        for protocol in self.protocols:
            if target in self.connect_dict[protocol].keys() and self.connect_dict[protocol][target] <= min_distance:
                candidates.append(protocol.port_against(self))
                min_distance = self.connect_dict[protocol][target]
        return candidates


class AbstractProtocol:
    """an abstract protocol consist of two abstract regions and two abstract ports"""

    def __init__(self, port1: AbstractPort, port2: AbstractPort):
        region1, region2 = port1.master, port2.master
        self.protocol_na = f'Pro[{region1}|{region2}]'
        self.connect_dict: dict[AbstractRegion, tuple[AbstractPort, AbstractRegion]] = {
            region1: (port2, region2),
            region2: (port1, region1)
        }

    def other_side(self, origin: AbstractRegion) -> AbstractRegion: return self.connect_dict[origin][1]
    def port_against(self, region: AbstractRegion) -> AbstractPort: return self.connect_dict[region][0]

    def accessible_from(self, origin: AbstractRegion, current_distance: int = 0, path: list[AbstractRegion] = None):
        res = {}
        source_region = self.other_side(origin)
        # print(f'Getting view of {source_region} through {self}')
        if source_region in path:
            # print('Meet the path')
            return {}
        path_copy = path[:]
        path.append(source_region)
        for region, distance in source_region.accessible_from(self, current_distance, path).items():
            if region not in path_copy:
                res[region] = distance + 1
        return res

    def place_between(self, region1: AbstractRegion, region2: AbstractRegion):
        if not region1.finished and not region2.finished:
            region1.connect_dict[self] = {}
            region2.connect_dict[self] = {}
        elif region1.finished and region2.finished:
            assert region1.master != region2.master, f'The district {region1.master} has been finished. Cannot add' \
                                                     f'connection'
            region1.connect_dict[self] = {region2: 1}
            region2.connect_dict[self] = {region1: 1}
            for region in region1.master.subregions:
                for protocol, protocol_connect_dict in region.connect_dict.items():
                    new = {}
                    for tar_region, distance in protocol_connect_dict.items():
                        if tar_region == region1:
                            new[region2] = distance + 1
                    region.connect_dict[protocol].update(new)

            for region in region2.master.subregions:
                for protocol, protocol_connect_dict in region.connect_dict.items():
                    new = {}
                    for tar_region, distance in protocol_connect_dict.items():
                        if tar_region == region2:
                            new[region1] = distance + 1
                    region.connect_dict[protocol].update(new)

        else:
            raise AssertionError(f'{region1} and {region2} have different states')

    def __repr__(self):
        return self.protocol_na


class AbstractDistrict(AbstractRegion):
    """An abstract district can contain abstract regions (which means it can also contain other abstract districts)
    It inherits AbstractRegion because it can be seen as a region
    It inherits AbstractPort so that it can be seen as a port
    The following implementation makes it a container of abstract regions"""
    master: 'AbstractDistrict'
    port_type = AbstractPort
    root_region_type = AbstractRegion

    def __init__(self, name, level=2, master: 'AbstractDistrict' = None, add_self=True, **kwargs):
        assert level >= 2, 'The level of a district should be at least 2'
        AbstractRegion.__init__(self, name, level, master, add_self, **kwargs)
        self._subregions_name_dict: dict[str, AbstractRegion] = {}
        self.inner_finished = False

    @property
    def ports(self) -> list[AbstractPort]:
        res = []
        for region in self._root_region_dict.values():
            res.extend(region.ports)
        return res

    @property
    def subregions(self) -> list[AbstractRegion]:
        """All subregions DIRECTLY belong to this district"""
        return list(self._subregions_name_dict.values())

    @property
    def defined_names(self) -> list[str]:
        """All subregion names DIRECTLY defined in this district"""
        return list(self._subregions_name_dict.keys())

    @property
    def _root_region_dict(self):
        if self.level == 2:
            return self._subregions_name_dict
        res = {}
        for subregion in self.subregions:
            assert isinstance(subregion, AbstractDistrict), f'{self} is not a lowest level district, ' \
                                                            f'but one of its subregion, {subregion}, ' \
                                                            f'is not a district'
            for name, root_region in subregion._root_region_dict.items():
                assert name not in res.keys(), f'Overlapped name: {name}'
                res[name] = root_region
        return res

    def __setitem__(self, name: str, region: 'AbstractRegion'):
        """DIRECTLY add a subregion in this district.The name should not exist in the district previously"""
        if name not in self.defined_names:
            self._subregions_name_dict[name] = region
        else:
            raise KeyError(f'Name {name} already exists')

    def add_subregion(self, name: str, add_self=True, **kwargs) -> 'AbstractDistrict | AbstractRegion':
        new_level = self.level - 1
        assert new_level >= 1, 'Level for region should be at least 1'
        if new_level == 1:  # if we are adding a basic region
            new_subregion = self[name] = self.root_region_type(name, new_level, add_self=add_self,
                                                               master=self, **kwargs)
        else:  # if we are adding a nested district
            new_subregion = self[name] = self.__class__(name, new_level, add_self=add_self, master=self, **kwargs)
        return new_subregion

    @classmethod
    def _connect(cls, root_level_port1: 'AbstractPort', root_level_port2: 'AbstractPort'):
        new_protocol = AbstractProtocol(root_level_port1, root_level_port2)
        master1, master2 = root_level_port1.master, root_level_port2.master
        assert master1 != master2, 'Cannot connect a region to itself'
        new_protocol.place_between(master1, master2)
        if master1.master and master2.master:
            if master1.master != master2.master:
                cls._connect(master1, master2)

    def connect(self, region1: 'AbstractRegion', region2: AbstractRegion, kwargs_region1=None, kwargs_region2=None):
        assert not self.inner_finished, f'The district {self} has been finished. Cannot add connection'
        if kwargs_region1 is None:
            kwargs_region1 = {}
        if kwargs_region2 is None:
            kwargs_region2 = {}

        assert region1.level == region2.level == 1, 'Connection should be built on root level regions'
        examine_master1, examine_master2 = region1.master, region2.master
        while examine_master1 != examine_master2:
            assert examine_master1.inner_finished, f'A master of {region1}, {examine_master1}, is not yet finished'
            assert examine_master2.inner_finished, f'A master of {region2}, {examine_master2}, is not yet finished'
            examine_master1, examine_master2 = examine_master1.master, examine_master2.master
        assert examine_master1 == self, \
            f'{self} is not the lowest level common master for {region1} and {region2}'

        root_port1 = self.port_type(f'BP[{region2}->{region1}]', master=region1, **kwargs_region1)
        root_port2 = self.port_type(f'BP[{region1}->{region2}]', master=region2, **kwargs_region2)
        self._connect(root_port1, root_port2)

    def finish_inner_construction(self):
        for subregion in self.subregions:
            subregion._generate_connection_dict()
        self.inner_finished = True
    '''@staticmethod
    def build(self, construction_tree: dict[dict, dict], **root_kwargs):
        root =
        for district in construction_tree.keys():'''


if __name__ == '__main__':
    class _Test:
        super_host = AbstractDistrict('1st host', level=3)
        host1 = super_host.add_subregion('2nd host1')
        A = host1.add_subregion('A')
        B = host1.add_subregion('B')
        C = host1.add_subregion('C')
        D = host1.add_subregion('D')
        host2 = super_host.add_subregion('2nd host2')
        E = host2.add_subregion('E')
        F = host2.add_subregion('F')
        G = host2.add_subregion('G')
        H = host2.add_subregion('H')

        host1.connect(A, B)
        host1.connect(B, C)
        host1.connect(C, D)
        host1.connect(D, A)
        host1.finish_inner_construction()

        host2.connect(E, F)
        host2.connect(F, G)
        host2.connect(G, H)
        host2.connect(H, E)
        host2.finish_inner_construction()

        super_host.connect(A, E)
        super_host.finish_inner_construction()

        for region in host1.subregions:
            print(region.connect_dict)
            print(region.finished)

        print(host1.connection_info())
        print(host1.find_ports(host2))
        print(A.find_ports(B))
        print(A.ports)
