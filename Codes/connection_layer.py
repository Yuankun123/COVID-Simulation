"""Pure Gold"""
from tools import red_text
import math
from typing import Optional, Iterable
__all__ = ['AbstractPort', 'AbstractRegion', 'AbstractDistrict']


class Base:
    port_type: type = None

    def __init_subclass__(cls, is_port_type=False, **kwargs):
        """A subclass's port type is itself if declared with is_port_type = True; otherwise, its port type is
        set to that of its base"""
        if is_port_type:
            cls.port_type = cls
        else:
            assert issubclass(cls.__base__, Base)
            cls.port_type = cls.__base__.port_type


class AbstractPort(Base, is_port_type=True):
    """An abstract port is the smallest object in a connection level. It is used to constitute a protocol"""
    master: Optional['AbstractRegion']

    def __init__(self, name: str, **kwargs):
        """name is just a reminder for debugging, not important"""
        self.na = name
        self.master = None

    def slaved(self, master: 'AbstractRegion') -> 'AbstractPort':
        self.master = master
        return self

    def __repr__(self):
        return self.na


class AbstractRegion(AbstractPort):
    """An abstract region is the smallest object connectable by protocols.
    It can be a member of an Abstract District"""
    master: Optional['AbstractDistrict']

    def __init__(self, name: str, add_self=True, **kwargs):
        super(AbstractRegion, self).__init__(name)
        self.add_self = add_self
        self.connect_dict: dict[AbstractProtocol, dict[AbstractRegion: int]] = {}
        self.connected = False  # whether the connection dict has been generated\
        self.level = 0

    def __repr__(self):
        return red_text(f'AR_{self.na}')

    @property
    def protocols(self):
        return list(self.connect_dict.keys())

    def _generate_connection_dict(self,
                                  current_distance: int = 0,
                                  root_path: list['AbstractRegion'] = None):
        assert not self.connected
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
            self.connected = True

    def accessible_from(self, origin=None, current_distance: int = 0, path: list['AbstractRegion'] = None) -> \
            dict['AbstractRegion', int]:
        # print(f'Getting accessible regions from {self} through protocols except {origin}')
        if not self.connected:
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
        if not region1.connected and not region2.connected:
            region1.connect_dict[self] = {}
            region2.connect_dict[self] = {}
        elif region1.connected and region2.connected:
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
    """An abstract district can contain abstract regions (which means it can also contain other abstract districts).
    It inherits AbstractRegion because it can be seen as a region.
    It inherits AbstractPort so that it can be seen as a port.
    The following implementation makes it a container of abstract regions."""
    master: Optional['AbstractDistrict']

    def __init__(self, name, **kwargs):
        super().__init__(name, True, **kwargs)
        self.subregions: list[AbstractRegion] = []
        self._inner_finished = False

    def __iter__(self):
        return self.subregions.__iter__()

    def __getitem__(self, item):
        return self.subregions.__getitem__(item)

    @staticmethod
    def _wrapped(target: AbstractRegion, stop_level: int) -> 'AbstractDistrict':
        current_target = target
        index = 0
        while current_target.level < stop_level:
            current_target = AbstractDistrict(f'Wrapper #{index} of {target.na}')(current_target)
            index += 1
        return current_target

    def __add_subregions(self, new_subregions: list[AbstractRegion]) -> None:
        """This method should be called only once"""
        max_level = max([new_subregion.level for new_subregion in new_subregions])
        for new_subregion in new_subregions:
            new_subregion = self._wrapped(new_subregion, max_level)
            assert new_subregion.level == max_level, f'Wrapper fails'
            new_subregion.slaved(master=self)
            self.level = max_level + 1
            self.subregions.append(new_subregion)

    @classmethod
    def __connect(cls, root_level_port1: 'AbstractPort', root_level_port2: 'AbstractPort'):
        new_protocol = AbstractProtocol(root_level_port1, root_level_port2)
        master1, master2 = root_level_port1.master, root_level_port2.master
        assert master1 != master2, f'Cannot connect {master1} to itself'
        new_protocol.place_between(master1, master2)
        if master1.master and master2.master:
            if master1.master != master2.master:
                cls.__connect(master1, master2)

    @classmethod
    def _get_ports(cls, region1: AbstractRegion, region2: AbstractRegion) -> tuple[AbstractPort, AbstractPort]:
        """This method should be overridden if you want a different port type"""
        root_port1 = cls.port_type(name=f'AP[{region2}->{region1}]').slaved(master=region1)
        root_port2 = cls.port_type(name=f'AP[{region1}->{region2}]').slaved(master=region2)
        return root_port1, root_port2

    def __connect_integrated(self, region1: 'AbstractRegion', region2: AbstractRegion):
        # make sure they are connectable
        assert region1 != region2, f'Cannot connect {region1} to itself'
        assert region1.level == region2.level
        assert not isinstance(region1, AbstractDistrict) and not isinstance(region2, AbstractDistrict), \
            'Connection should be built on root level regions'
        examine_master1, examine_master2 = region1.master, region2.master
        while examine_master1 != examine_master2:
            assert examine_master1._inner_finished, f'A master of {region1}, {examine_master1}, is not yet finished'
            assert examine_master2._inner_finished, f'A master of {region2}, {examine_master2}, is not yet finished'
            examine_master1, examine_master2 = examine_master1.master, examine_master2.master
        assert examine_master1 == self, \
            f'{self} is not the lowest level common master for {region1} and {region2}'

        root_port1, root_port2 = self._get_ports(region1, region2)
        self.__connect(root_port1, root_port2)

    def __finish_construction(self) -> None:
        for subregion in self.subregions:
            subregion._generate_connection_dict()
        self._inner_finished = True

    def __call__(self, *regions: AbstractRegion, connections: Iterable[tuple[AbstractRegion, AbstractRegion]] = ()) \
            -> 'AbstractDistrict':
        assert not self._inner_finished, 'A district can only be constructed once'
        self.__add_subregions(list(regions))
        for connection in connections:
            self.__connect_integrated(*connection)
        self.__finish_construction()
        return self

    def __repr__(self):
        return red_text(f'AD_{self.na}')


if __name__ == '__main__':
    class _Test:
        super_host = AbstractDistrict('1st host')(
            (host1 := AbstractDistrict('2nd host1'))(
                (A := AbstractRegion('A')),
                (B := AbstractRegion('B')),
                (C := AbstractRegion('C')),
                (D := AbstractRegion('D')),
                connections=((A, B), (B, C), (C, D), (D, A))
            ),
            #(host2 := AbstractDistrict('2nd host2'))(
            #    (E := AbstractRegion('E')),
            #    (F := AbstractRegion('F')),
            #    (G := AbstractRegion('G')),
            #    (H := AbstractRegion('H')),
            #    connections=((E, F), (F, G), (G, H), (H, E))
            #),
            (E := AbstractRegion('E')),
            connections=((A, E),)
        )

        for region in host1.subregions:
            print(region.connect_dict)
            print(region.connected)

        print(host1.connection_info())
        print(A.find_ports(B))
        print(AbstractDistrict.port_type)
        print(Base.port_type)
