from __future__ import annotations
from fly_in.src.validation_models import MapData
from fly_in.src.utils import ParsingTags
from typing import List
from fly_in.src.connection import Connection, ConnectionException
from fly_in.src.zone import Zone
from fly_in.src.drone import Drone


class GraphException(Exception):
    def __init__(self, msg: str = ""):
        self.msg = msg
        super().__init__(msg)

    def __str__(self):
        return self.msg


class Graph:
    def __init__(self, data: MapData):
        self.__name = data.name
        self.__nb_drones = data.nb_drones
        self.__zones: List[Zone] = []
        self.__connections: List[Connection] = []
        self.__drones: List[Drone] = []

        for h in data.hubs:
            z = Zone(h)
            if h.tag == ParsingTags.START_HUB:
                self.__start = z
            elif h.tag == ParsingTags.END_HUB:
                self.__end = z
            self.__zones.append(z)
        for c in data.connections:
            try:
                self.__connections.append(Connection(c, self.__zones))
            except ConnectionException as e:
                raise GraphException(str(e))
        for _ in range(data.nb_drones):
            d = Drone()
            self.__drones.append(d)
            d.set_where(self.__start)

    ##### GETTERS #######
    def get_name(self) -> str:
        return self.__name
    
    def get_nb_drones(self) -> int:
        return self.__nb_drones

    def get_zones(self) -> List['Zone']:
        return self.__zones
    
    def get_start(self) -> Zone:
        return self.__start
    
    def get_end(self) -> Zone:
        return self.__end

    def get_connections(self) -> List[Connection]:
        return self.__connections
    
    def get_drones(self) -> List[Drone]:
        return self.__drones
    
    def add_drone(self, drone: Drone) -> None:
        if drone in self.__drones:
            raise GraphException(f"Drone '{drone.ID}' already in graph '{self.__name}'")
        drone.set_where(self.get_start())
        self.__drones.append(drone)
    
    def remove_connection(self, conn: Connection) -> None:
        try:
            self.__connections.remove(conn)
        except ValueError:
            GraphException(f"Error: unexistant '{conn.get_name()}' connection"
                           f"in graph '{self.__name}'")

    def remove_zone(self, zone: Connection) -> None:
        try:
            self.__zones.remove(zone)
        except ValueError:
            GraphException(f"Error: unexistant '{zone.get_name()}' zone"
                           f"in graph '{self.__name}'")
        for c in self.__connections:
            if c.get_zoneA() == zone or c.get_zoneB() == zone:
                try:
                    self.remove_connection(c)
                except GraphException as e:
                    raise e

    def graphInfo(self) -> str:
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
                f"color={connection.get_color().name}, max_link_capacity={connection.MAX_LINK_CAPACITY}"
            )

        return "\n".join(lines)

    def get_links(self, zone: Zone) -> list[Connection]:
        links: list[Connection] = []
        for c in self.__connections:
            if c.get_zoneA() == zone or c.get_zoneB() == zone:
                links.append(c)
        return links

    def get_min_cost_path(self):
        stack: list[Zone] = []
        visited: list[Zone] = []
        curr: Zone
        links: list[Connection]
        stack.append(self.__start)
        while len(stack) > 0:
            curr = stack[-1]
            visited.append(self.__start)
            links = self.get_connections(curr)
            # rimuovo conns tra zone gia visitate
            for l in links:
                if l.get_zoneA() in visited and l.get_zoneB in visited:
                    links.remove(l)
            

 
            
