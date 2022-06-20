from tools import REDTEXT, WHITETEXT


class AbstractProtocol:
    def __init__(self, region1: 'AbstractRegion', region2: 'AbstractRegion', *args, **kwargs):
        self.region1 = region1
        self.region2 = region2

    def other_side(self, origin: 'AbstractRegion') -> 'AbstractRegion':
        if origin == self.region1:
            return self.region2
        else:
            return self.region1

    def accessible_from(self, origin: 'AbstractRegion', current_distance: int = 0,
                        source_region_record: dict['AbstractRegion', int] = None):
        if source_region_record is None:
            source_region_record = {}

        res = {}
        source_region = self.other_side(origin)
        # print(f'Getting view of {source_region} through {self}')
        if source_region in source_region_record.keys() and current_distance >= source_region_record[source_region]:
            # print('Meet the track')
            return {}
        else:
            source_region_record[source_region] = current_distance
        for region, distance in source_region.accessible_from(self, current_distance, source_region_record).items():
            res[region] = distance + 1
        return res

    def place_between(self, region1, region2):
        region1.protocols.append(self)
        region1.connect_dict[self] = {}
        region2.protocols.append(self)
        region2.connect_dict[self] = {}

    def __repr__(self):
        return f'P[{self.region1}|{self.region2}]'


class AbstractRegion:
    def __init__(self, name: str, *args, add_self=True, **kwargs):
        self.na = name
        self.add_self = add_self
        self.finished = False
        self.protocols: list[AbstractProtocol] = []
        self.connect_dict: dict[AbstractRegion, tuple[int, list[AbstractProtocol]]] = {}

    def accessible_from(self, origin: AbstractProtocol = None, current_distance: int = 0,
                        source_region_record: dict['AbstractRegion', int] = None) -> dict['AbstractRegion', int]:
        # print(f'Getting accessible regions from {self} through protocols except {origin}')
        if source_region_record is None:
            source_region_record = {self: 0}

        res = {}
        if self.add_self:
            res = {self: 0}
        for protocol in self.protocols:
            if protocol != origin:
                # print(f'{self}, Processing Protocol:{protocol}')
                current_distance += 1  # the distance to the next region
                for region, distance in protocol.accessible_from(self, current_distance, source_region_record).items():
                    if region != self and (region not in res.keys() or distance < res[region]):
                        res[region] = distance
                        if origin is None:  # which means we are at the top level
                            self.connect_dict[protocol][region] = distance
        return res

    def finish_construction(self):
        print(f'Start to process {self}')
        self.accessible_from()
        self.finished = True
        print(f'########{self} finished')

    def find_protocol(self, target: 'AbstractRegion'):
        assert target != self
        return self.guidance_dict[target]

    def __repr__(self):
        return REDTEXT + self.na + WHITETEXT

    def detail_info(self):
        res = f'{self.na}. ' \
              f'Having protocols to: {", ".join([repr(protocol.other_side(self)) for protocol in self.protocols])}, '
        for region, distance in self.accessible_from().items():
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
        host.connect('A', 'B')
        host.connect('B', 'C')
        host.connect('C', 'D')
        host.connect('D', 'A')

        for region in host.regions.values():
            region.finish_construction()
        for region in host.regions.values():
            print(region.connect_dict)
