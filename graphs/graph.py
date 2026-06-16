from enum import Enum
from typing import List, Dict


class GraphException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class ZoneException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class ZoneType(Enum):
    START = ('start', 0)
    END = ('end', 0)
    NORMAL = ('normal', 1)
    BLOCKED = ('blocked', -1)
    RESTRICTED = ('restricted', 2)
    PRIORITY = ('priority', 1)


class Zone:
    def __init__(self, name: str,
                 zone: ZoneType = ZoneType.NORMAL,
                 max_drones: int = 1,
                 color: str = '#FFFFFF') -> None:
        self.__name: str = name
        self.__type: ZoneType = zone
        self.__max_drones: int = max_drones
        if self.__type == ZoneType.BLOCKED:
            self.__max_drones = 0
        elif self.__type == ZoneType.START or\
            self.__type == ZoneType.END:
            self.__max_drones = -1
        self.__color: str = color

        self.__drones_in = 0

    def get_name(self) -> str:
        return self.__name

    def get_type(self) -> ZoneType:
        return self.__type

    def get_max_drones(self) -> int:
        return self.__max_drones

    def get_color(self) -> str:
        return self.__color

    def increment_drones(self) -> None:
        self.__drones_in += 1

    def decrement_drones(self) -> None:
        self.__drones_in -= 1


class OrientedArch:
    def __init__(self, from_zone: Zone, to_zone: Zone) -> None:
        self.arch: tuple[Zone, Zone] = (from_zone, to_zone)
        self.cost: int = int(from_zone.get_type().value[1])

class Graph:
    def __init__(self, name: str):
        self.name = name
        self.zone_list: List[Zone] = []

    def add_start(self, start: Zone) -> None:
        '''Adds/overrwrites a starting zone to the graph'''
        if not start.get_type() == ZoneType.START:
            raise GraphException("Starting zone must be of type 'start', "
                                 "yours is of type "
                                 f"'{start.get_type().value[0]}'")
        self.start = start

    def add_end(self, end: Zone) -> None:
        '''Adds/overrwrites an ending zone to the graph'''
        if not end.get_type() == ZoneType.END:
            raise GraphException("Ending zone must be of type 'end', "
                                 "yours is of type "
                                 f"'{end.get_type().value['name']}'")
        self.end = end


if __name__ == "__main__":
    start = Zone('start', ZoneType.START, 2)
    start = Zone('start', ZoneType.START, 2)
    g = Graph('G')
    try:
        g.add_start(start)
    except GraphException as e:
        print(e)
