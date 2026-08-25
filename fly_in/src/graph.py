from __future__ import annotations
from typing import Optional, Tuple, List
from fly_in.src.validation_models import MapData
from fly_in.src.utils import Tag, Action
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
            if h.tag == Tag.START_HUB:
                self.__start = z
            elif h.tag == Tag.END_HUB:
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
            d.set_last_pos(self.__start)

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
    
    def get_zone_connections(self, zone: Zone) -> List[Zone]:
        connected: List[Zone] = []
        for c in self.__connections:
            if c.get_zoneA() == zone:
                connected.append(c.get_zoneB())
            elif c.get_zoneB() == zone:
                connected.append(c.get_zoneA())
        return connected

    def remove_connection(self, conn: Connection) -> None:
        try:
            self.__connections.remove(conn)
        except ValueError:
            GraphException(f"Error: unexistant '{conn.get_name()}' connection"
                           f"in graph '{self.__name}'")
    
    def get_drones(self) -> List[Drone]:
        return self.__drones
    
    def add_drone(self, drone: Drone) -> None:
        if drone in self.__drones:
            raise GraphException(f"Drone '{drone.ID}' already in graph '{self.__name}'")
        drone.set_where(self.get_start())
        self.__drones.append(drone)
    

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

    def get_min_cost_path(self, start_zone: Zone,
                          end_zone: Zone,
                          start_turn: int = 0) -> Optional[List[Tuple[Action, object, int]]]:
        import heapq
        
        queue = []
        current_zone: Zone
        current_turn: int
        path: List[Tuple[Action, object, int]] = []
        heapq.heappush(queue, (start_turn, start_turn, start_zone.get_name(), start_zone, []))
        
        visited: set[tuple[str, int]] = set()
        
        while queue:
            cost, current_turn, _, current_zone, path = heapq.heappop(queue)
            print("=" * 20 + f"turn: {current_turn}\npath: {path}")
            
            
            if current_zone == end_zone:
                return path
                
            state = (current_zone.get_name(), current_turn)
            if state in visited:
                continue
            visited.add(state)
            
            # se il drone atende un turno
            print(f"space left on next turn on zone {current_zone.get_name()}: {current_zone.space_left_at(current_turn + 1)}")
            if current_zone.space_left_at(current_turn + 1) > 0:
                heapq.heappush(queue, (
                    cost + 1, 
                    current_turn + 1, 
                    current_zone.get_name(), 
                    current_zone, 
                    path.append([(Action.WAIT, current_zone, current_turn + 1)])
                ))
                
            # se il drone si muove
            for conn in self.get_links(current_zone):
                # Trova il vicino
                neighbor = conn.get_zoneA() if conn.get_zoneB() == current_zone else conn.get_zoneB()
                
                if neighbor.get_type().name == "BLOCKED": 
                    continue
                    
                move_cost = neighbor.get_cost() # Ritorna 1 o 2
                
                if move_cost == 1:
                    # la zona deve essere liberata se richeide 1 turno solo
                    if neighbor.space_left_at(current_turn + 1) > 0:
                        heapq.heappush(queue, (
                            cost + 1,
                            current_turn + 1,
                            neighbor.get_name(),
                            neighbor,
                            path.append([(Action.MOVE, neighbor,
                                          current_turn + 1)])
                        ))
                
                elif move_cost == 2:
                    # Zona RESTRICTED 
                    # La connessione deve essere libera al turno T+1
                    # La zona di destinazione deve essere libera al turno T+2
                    if conn.space_left_at(current_turn + 1) > 0 and\
                        neighbor.space_left_at(current_turn + 2) > 0:
                        heapq.heappush(queue, (
                            cost + 2,
                            current_turn + 2,
                            neighbor.get_name(),
                            neighbor,
                            path.append([(Action.TRANSIT, conn, current_turn + 1),
                                         (Action.MOVE, neighbor, current_turn + 2)])
                        ))
                        
        return None
            

 
            
