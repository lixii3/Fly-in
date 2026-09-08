from __future__ import annotations
from fly_in.src.validation_models import ParsingColors, Tag
from fly_in.src.validation_models import ConnectionData, MetaData
from typing import Final, Iterable, TYPE_CHECKING, overload, cast
from pydantic import ValidationError


if TYPE_CHECKING:
    from fly_in.src.zone import Zone


class ConnectionException(Exception):
    """Exception raised when a connection operation fails."""

    def __init__(self, msg: str):
        """Initialize a connection-related exception.

        Args:
            msg (str): Error message describing the connection failure.
        """
        self.msg = msg
        super().__init__(msg)

    def __str__(self):
        """Return the formatted exception message."""
        return "ConnectionException: " + self.msg


class Connection:
    """Represent a link between two zones and its turn reservations."""

    @overload
    def __init__(
        self,
        name: str,
        zoneA: Zone,
        zoneB: Zone,
        color: str,
        max_link_capacity: int = 1,
    ) -> None:
        """Create a connection from endpoint zones and display settings."""
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
        """Create a connection from validated data and its endpoint zones.

        Args:
            data (ConnectionData): Validated connection definition.
            zones (Iterable[Zone]): Zones available in the map.
        """
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
                f"Expecting zones ('{data.zoneA}', {data.zoneB}') "
                "to exist within the map."
            )
        self.__arch = cast(tuple["Zone", "Zone"], tuple(__tmparch))

    # GETTERS
    def get_name(self) -> str:
        """Return the connection name."""
        return self.__name

    def get_color(self) -> ParsingColors:
        """Return the configured connection color."""
        return self.__color

    def get_arch(self) -> tuple[Zone, Zone]:
        """Return the two zones connected by this connection."""
        return self.__arch

    def get_zoneA(self) -> Zone:
        """Return the first endpoint zone."""
        return self.__arch[0]

    def get_zoneB(self) -> Zone:
        """Return the second endpoint zone."""
        return self.__arch[1]

    def get_coordinates(self) -> tuple[int, int]:
        """Return the midpoint coordinates of the endpoint zones."""
        xa, ya = self.get_zoneA().get_coordinates()
        xb, yb = self.get_zoneB().get_coordinates()
        return ((xa + xb) // 2, (ya + yb) // 2)

    def space_left_at(self, turn: int) -> int:
        """Return capacity remaining for a specific turn.

        Args:
            turn (int): Turn whose reservations should be checked.

        Returns:
            int: Number of available connection slots.
        """
        # Sottrai i droni già prenotati per quel turno specifico
        reserved = self.__reservations.get(turn, 0)
        return self.MAX_LINK_CAPACITY - reserved

    def reserve(self, turn: int) -> None:
        """Reserve one connection slot for a turn.

        Args:
            turn (int): Turn in which the connection will be used.

        Raises:
            ConnectionException: If the connection is at capacity.
        """
        if self.space_left_at(turn) <= 0:
            raise ConnectionException("Errore: impossibile prenotare la "
                                      f"risorsa {self.get_name()} "
                                      f"al turno {turn}")
        self.__reservations[turn] = self.__reservations.get(turn, 0) + 1
