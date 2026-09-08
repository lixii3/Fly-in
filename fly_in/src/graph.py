from __future__ import annotations
from typing import Optional, Tuple, List
from fly_in.src.validation_models import MapData
from fly_in.src.utils import Tag, Action
from typing import List
from fly_in.src.connection import Connection, ConnectionException
from fly_in.src.zone import Zone
from fly_in.src.drone import Drone


coso = Optional[List[Tuple[Action, Zone | Connection, int]]]


class GraphException(Exception):
    """Exception raised when a graph operation fails."""

    def __init__(self, msg: str = ""):
        """Initialize a graph-related exception.

        Args:
            msg (str, optional): Error message. Defaults to "".
        """
        self.msg = msg
        super().__init__(msg)

    def __str__(self):
        """Return the exception message."""
        return self.msg


class Graph:
    """Represent zones, connections, and drones for one map."""

    def __init__(self, data: MapData):
        """Build a graph from validated map data.

        Args:
            data (MapData): Validated map definition.
        """
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

    # GETTERS
    def get_name(self) -> str:
        """Return the graph name."""
        return self.__name

    def get_nb_drones(self) -> int:
        """Return the number of drones configured for the graph."""
        return self.__nb_drones

    def get_zones(self) -> List["Zone"]:
        """Return all zones in the graph."""
        return self.__zones

    def get_start(self) -> Zone:
        """Return the graph's start hub."""
        return self.__start

    def get_end(self) -> Zone:
        """Return the graph's end hub."""
        return self.__end

    def get_connections(self) -> List[Connection]:
        """Return all graph connections."""
        return self.__connections

    def get_zone_connections(self, zone: Zone) -> List[Zone]:
        """Return zones directly connected to a zone.

        Args:
            zone (Zone): Zone whose neighbors should be found.

        Returns:
            List[Zone]: Directly connected neighboring zones.
        """
        connected: List[Zone] = []
        for c in self.__connections:
            if c.get_zoneA() == zone:
                connected.append(c.get_zoneB())
            elif c.get_zoneB() == zone:
                connected.append(c.get_zoneA())
        return connected

    def remove_connection(self, conn: Connection) -> None:
        """Remove a connection from the graph.

        Args:
            conn (Connection): Connection to remove.
        """
        try:
            self.__connections.remove(conn)
        except ValueError:
            GraphException(
                f"Error: unexistant '{conn.get_name()}' connection"
                f"in graph '{self.__name}'"
            )

    def get_drones(self) -> List[Drone]:
        """Return all drones assigned to the graph."""
        return self.__drones

    def add_drone(self, drone: Drone) -> None:
        """Add a drone and place it at the start hub.

        Args:
            drone (Drone): Drone to add.

        Raises:
            GraphException: If the drone is already in the graph.
        """
        if drone in self.__drones:
            raise GraphException(f"Drone '{drone.ID}' already in graph '{self.__name}'")
        drone.set_where(self.get_start())
        self.__drones.append(drone)

    def remove_zone(self, zone: Connection) -> None:
        """Remove a zone and its incident connections.

        Args:
            zone (Connection): Zone to remove.
        """
        try:
            self.__zones.remove(zone)
        except ValueError:
            GraphException(
                f"Error: unexistant '{zone.get_name()}' zonein graph '{self.__name}'"
            )
        for c in self.__connections:
            if c.get_zoneA() == zone or c.get_zoneB() == zone:
                try:
                    self.remove_connection(c)
                except GraphException as e:
                    raise e

    def graphInfo(self) -> str:
        """Return a human-readable description of the graph."""
        lines = [f"Graph: {self.__name}", f"Drones: {self.__nb_drones}", "Zones:"]

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
        """Return connections incident to a zone.

        Args:
            zone (Zone): Zone whose links should be found.

        Returns:
            list[Connection]: Incident connections.
        """
        links: list[Connection] = []
        for c in self.__connections:
            if c.get_zoneA() == zone or c.get_zoneB() == zone:
                links.append(c)
        return links

    @staticmethod
    def manhattan_distance(zoneA: Zone, zoneB: Zone) -> int:
        """Calculate Manhattan distance between two zones.

        Args:
            zoneA (Zone): First zone.
            zoneB (Zone): Second zone.

        Returns:
            int: Sum of absolute coordinate differences.
        """
        return abs(zoneA.get_x() - zoneB.get_x()) + abs(zoneA.get_y() - zoneB.get_y())

    def get_min_cost_path(
        self, start_zone: Zone, end_zone: Zone, start_turn: int = 0
    ) -> Optional[List[Tuple[Action, Zone | Connection, int]]]:
        """Find a capacity-aware minimum-cost path between two zones.

        Args:
            start_zone (Zone): Zone from which the route starts.
            end_zone (Zone): Destination zone.
            start_turn (int, optional): Turn at which searching starts.
                Defaults to 0.

        Returns:
            Optional[List[Tuple[Action, Zone | Connection, int]]]: Scheduled
                actions and resources, or None when no route exists.
        """
        import heapq

        queue: List[
            Tuple[
                float, int, int, float, str, Zone, Tuple[Action, Zone | Connection, int]
            ]
        ] = []
        counter = 0

        start_h = float(self.manhattan_distance(start_zone, end_zone))
        heapq.heappush(
            queue,
            (start_h, counter, start_turn, 0.0, start_zone.get_name(), start_zone, []),
        )

        visited: set[tuple[str, int]] = set()

        while queue:
            f_cost, _, current_turn, g_cost, _, current_zone, path = heapq.heappop(
                queue
            )

            if current_zone == end_zone:
                return path

            state = (current_zone.get_name(), current_turn)
            if state in visited:
                continue
            visited.add(state)

            # OPZIONE 1: WAIT
            if current_zone.space_left_at(current_turn + 1) > 0:
                next_path = path + [(Action.WAIT, current_zone, current_turn + 1)]
                counter += 1
                heapq.heappush(
                    queue,
                    (
                        f_cost + 1.0,
                        counter,
                        current_turn + 1,  # Il turno + 1
                        g_cost + 1.0,  # Il costo + 1
                        current_zone.get_name(),
                        current_zone,
                        next_path,
                    ),
                )

            for conn in self.get_links(current_zone):
                neighbor = (
                    conn.get_zoneA()
                    if conn.get_zoneB() == current_zone
                    else conn.get_zoneB()
                )

                if neighbor.get_type().name == "BLOCKED":
                    continue

                move_cost = float(neighbor.get_cost())  # Può essere 1.0, 2.0 o 0.9999

                # OPZIONE 2: MOVE (zone normal e priority)
                if move_cost <= 1.0:
                    if neighbor.space_left_at(current_turn + 1) > 0:
                        next_path = path + [(Action.MOVE, neighbor, current_turn + 1)]
                        counter += 1
                        new_turn = current_turn + 1
                        new_g_cost = g_cost + move_cost

                        h_cost = float(self.manhattan_distance(neighbor, end_zone))
                        new_f_cost = new_g_cost + h_cost

                        heapq.heappush(
                            queue,
                            (
                                new_f_cost,
                                counter,
                                new_turn,
                                new_g_cost,
                                neighbor.get_name(),
                                neighbor,
                                next_path,
                            ),
                        )

                # OPZIONE 3: TRANSIT (zone restricted)
                elif move_cost == 2.0:
                    if (
                        conn.space_left_at(current_turn + 1) > 0
                        and neighbor.space_left_at(current_turn + 2) > 0
                    ):
                        next_path = path + [
                            (Action.TRANSIT, conn, current_turn + 1),
                            (Action.MOVE, neighbor, current_turn + 2),
                        ]
                        counter += 1

                        # Movimento lungo 2 turni interi
                        new_turn = current_turn + 2
                        new_g_cost = g_cost + 2.0

                        h_cost = float(self.manhattan_distance(neighbor, end_zone))
                        new_f_cost = new_g_cost + h_cost

                        heapq.heappush(
                            queue,
                            (
                                new_f_cost,
                                counter,
                                new_turn,
                                new_g_cost,
                                neighbor.get_name(),
                                neighbor,
                                next_path,
                            ),
                        )

        return None
