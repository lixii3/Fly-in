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
    
    def printGraph(self) -> str:
        lines = [
            f"Graph: {self.__name}",
            f"Drones: {self.__nb_drones}",
            "Zones:"
        ]

        for zone in self.__zones:
            lines.append(
                f"  - {zone.get_name()}: x={zone.get_x()}, y={zone.get_y()}, "
                f"type={zone.get_type().name}, cost={zone.get_cost()}, "
                f"color={zone.get_color().name}, max_drones={zone.MAX_DRONES}"
            )

        lines.append("Connections:")
        for connection in self.__connections:
            zone_names = sorted([z.get_name() for z in connection.get_arch()])
            lines.append(
                f"  - {connection.get_name()}: {zone_names[0]} <-> {zone_names[1]}, "
                f"color={connection.get_color()}, max_link_capacity={connection.MAX_LINK_CAPACITY}"
            )

        return "\n".join(lines)

