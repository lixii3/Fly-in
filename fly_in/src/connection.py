from __future__ import annotations
from fly_in.src.validation_models import ParsingColors, Tag
from fly_in.src.validation_models import ConnectionData, MetaData
from typing import Final, Iterable, TYPE_CHECKING, overload
from pydantic import ValidationError


if TYPE_CHECKING:
    from fly_in.src.zone import Zone
    from fly_in.src.drone import Drone
class ConnectionException(Exception):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)

    def __str__(self):
        return "ConnectionException: " + self.msg


class Connection:
    @overload
    def __init__(self, name: str, zoneA: Zone, zoneB: Zone,
                 color: str, max_link_capacity: int = 1) -> None:
        try:
            metadata: MetaData = MetaData(
                tag=Tag.CONNECTION,
                color=ParsingColors.getColor(color),
                max_link_capacity=max_link_capacity,
            )
            data: ConnectionData = ConnectionData(name=name, metadata=metadata)
        except ValidationError as e:
            raise ConnectionException(str(e))
        self.__init__(data, [zoneA, zoneB])

    def __init__(self, data: ConnectionData, zones: Iterable[Zone]) -> None:
        self.__name: Final[str] = data.name
        self.__arch: tuple[Zone, Zone] = ()
        self.__color = data.metadata.color
        self.MAX_LINK_CAPACITY: Final[int] = data.metadata.max_link_capacity
        self.__reservations: dict[int, int] = {}

        __tmparch: list[Zone] = []
        for z in zones:
            if z.get_name() == data.zoneA or z.get_name() == data.zoneB:
                __tmparch.append(z)
        if len(__tmparch) != 2:
            raise ConnectionException(
                f"Expecting zones ('{data.zoneA}', {data.zoneB}') to exist within the map."
            )
        self.__arch = tuple(__tmparch)

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
    
    def get_coordinates(self) -> tuple[int, int]:
        xa, ya = self.get_zoneA().get_coordinates()
        xb, yb = self.get_zoneB().get_coordinates()
        return ((xa + xb) // 2, (ya + yb) // 2)

    def space_left_at(self, turn: int) -> int:
        # Sottrai i droni già prenotati per quel turno specifico
        reserved = self.__reservations.get(turn, 0)
        return self.MAX_LINK_CAPACITY - reserved

    def reserve(self, turn: int) -> None:
        if self.space_left_at(turn) <= 0:
            raise ConnectionException(f"Errore: impossibile prenotare la risorsa {self.get_name()} al turno {turn}")
        self.__reservations[turn] = self.__reservations.get(turn, 0) + 1

