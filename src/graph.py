from enum import Enum
from typing import List, Dict
from src.validation_models import MapData


class GraphException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class Connection:
    def __init__(self, from_zone: Zone, to_zone: Zone) -> None:
        self.arch: tuple[Zone, Zone] = (from_zone, to_zone)
        self.cost: int = int(from_zone.get_type().value[1])


class Graph:
    def __init__(self, data: MapData):
        self.name = data.name
        self.__zone_list: List[Zone] = []

    def get_zones(self) -> List[Zone]:
        return self.__zone_list

        self.end = end
    



if __name__ == "__main__":
    start = Zone('start', ZoneType.START, 2)
    start = Zone('start', ZoneType.START, 2)
    g = Graph('G')
    try:
        g.add_start(start)
    except GraphException as e:
        print(e)
