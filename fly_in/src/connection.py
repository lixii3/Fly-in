from __future__ import annotations
from fly_in.src.validation_models import ParsingColors, ParsingTags
from fly_in.src.validation_models import ConnectionData, MetaData
from typing import Final, Iterable, TYPE_CHECKING
from pydantic import ValidationError


if TYPE_CHECKING:
    from fly_in.src.zone import Zone
    from fly_in.src.drone import Drone
class ConnectionException(Exception):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)

    def __str__(self):
        return self.msg


class Connection:
    def __init__(self, data: ConnectionData, zones: Iterable[Zone]) -> None:
        self.__name: Final[str] = data.name
        self.__arch: set[Zone, Zone] = set()
        self.__color = data.metadata.color
        self.MAX_LINK_CAPACITY: Final[int] = data.metadata.max_link_capacity
        self.__drones_in: list[Drone]

        for z in zones:
            if z.get_name() == data.zoneA or z.get_name() == data.zoneB:
                self.__arch.add(z)
        if len(self.__arch) != 2:
            raise ConnectionException(
                f"Expecting zones ('{data.zoneA}', {data.zoneB}') to exist within the map."
            )

    @classmethod
    def manual_connection(
        cls, name: str, zoneA: Zone, zoneB: Zone, color: str, max_link_capacity: int = 1
    ) -> Connection:
        try:
            metadata: MetaData = MetaData(
                tag=ParsingTags.CONNECTION,
                color=ParsingColors.getColor(color),
                max_link_capacity=max_link_capacity,
            )
            data: ConnectionData = ConnectionData(name=name, metadata=metadata)
        except ValidationError as e:
            raise e
        return cls(data, [zoneA, zoneB])

    # GETTERS
    def get_name(self) -> str:
        return self.__name

    def get_color(self) -> ParsingColors:
        return self.__color

    def get_arch(self) -> set[Zone]:
        return self.__arch

    def get_zoneA(self) -> Zone:
        return self.__arch[0]

    def get_zoneB(self) -> Zone:
        return self.__arch[1]

    def get_drones_in(self) -> list[Drone]:
        return self.__drones_in
    
    def space_left(self) -> int:
        return self.MAX_LINK_CAPACITY - len(self.__drones_in)

    def drone_in(self, drone: Drone) -> None:
        if not self.space_left():
            raise ConnectionException("Error: connection is full, "
                                      f"unable to insert drone '{drone.ID}'")
        self.__drones_in.append(drone)
        drone.set_where(self)

    def drone_out(self, drone: Drone) -> None:
        try:
            self.__drones_in.remove(drone)
        except ValueError:
            raise ConnectionException(f"Error: drone '{drone.ID}' is not present in"
                                      f"connection '{self.__name}', unable to get it out")
        drone.set_where(self.get_zoneB())
