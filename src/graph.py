from zone import Zone
from connection import Connection
from typing import List
from validation_models import MapData


class GraphException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class Graph:
    def __init__(self, data: MapData):
        self.__name = data.name
        self.__nb_drones = data.nb_drones
        self.__zones: List[Zone] = []
        self.__connections: List[Connection] = []

        for h in data.hubs:
            self.__zones.append(Zone(h))
        for c in data.connections:
            self.__connections.append(Connection(c, self.__zones))

    ##### GETTERS #######
    def get_name(self) -> str:
        return self.__name
    
    def get_nb_drones(self) -> int:
        return self.__nb_drones

    def get_zones(self) -> List[Zone]:
        return self.__zones

    def get_connections(self) -> List[Connection]:
        return self.__connections



if __name__ == "__main__":
   pass