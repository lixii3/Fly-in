from __future__ import annotations
from fly_in.src.utils import ZoneType, ParsingColors, Tag
from typing import Final, TYPE_CHECKING
from fly_in.src.validation_models import HubData


if TYPE_CHECKING:
    from fly_in.src.drone import Drone


class ZoneException(Exception):
    """Exception raised when a zone operation fails."""

    def __init__(self, msg: str):
        """Initialize a zone-related exception.

        Args:
            msg (str): Error message describing the zone failure.
        """
        self.msg = msg
        super().__init__(msg)

    def __str__(self) -> str:
        """Return the exception message."""
        return self.msg


class Zone:
    """Represent a map zone and its capacity reservations."""

    def __init__(self, data: HubData) -> None:
        """Create a zone from validated hub data.

        Args:
            data (HubData): Validated hub definition.
        """
        self.__drones_in: list[Drone] = []
        self.__name: str = data.name
        self.__x: int = data.x
        self.__y: int = data.y
        zt = data.metadata.z_type
        self.__type: ZoneType = zt if zt is not None else ZoneType.NORMAL
        self.__cost: float = self.__type.value
        self.__color: ParsingColors = data.metadata.color
        self._tag: Tag = data.tag

        max_d = data.metadata.max_drones
        self.MAX_DRONES: Final[int] = max_d if max_d is not None else 1
        self.__reservations: dict[int, int] = {}

    # GETTERS
    def get_name(self) -> str:
        """Return the zone name."""
        return self.__name

    def get_x(self) -> int:
        """Return the zone's horizontal coordinate."""
        return self.__x

    def get_y(self) -> int:
        """Return the zone's vertical coordinate."""
        return self.__y

    def get_cost(self) -> float:
        """Return the movement cost associated with the zone."""
        return self.__cost

    def get_type(self) -> ZoneType:
        """Return the zone type."""
        return self.__type

    def get_color(self) -> ParsingColors:
        """Return the configured zone color."""
        return self.__color

    def get_coordinates(self) -> tuple[int, int]:
        """Return the zone coordinates."""
        return (self.__x, self.__y)

    def drone_in(self, drone: Drone) -> None:
        """Add a drone to the zone.

        Args:
            drone (Drone): Drone entering the zone.

        Raises:
            ZoneException: If the zone has no available capacity.
        """
        if not self.space_left():
            raise ZoneException(
                "Error: zone capacity is full, unable to "
                f"insert drone '{drone.ID}'"
            )
        self.__drones_in.append(drone)
        drone.set_where(self)

    def drone_out(self, drone: Drone) -> None:
        """Remove a drone from the zone.

        Args:
            drone (Drone): Drone leaving the zone.

        Raises:
            ZoneException: If the drone is not in this zone.
        """
        try:
            self.__drones_in.remove(drone)
        except ValueError:
            raise ZoneException(
                f"Error: drone '{drone.ID}' is not present in"
                f"zone '{self.__name}', unable to get it out"
            )
        drone.set_where(None)

    def space_left(self) -> int:
        """Return current physical capacity remaining in the zone."""
        if self.MAX_DRONES:
            return self.MAX_DRONES - len(self.__drones_in)
        return -1

    def space_left_at(self, turn: int) -> int:
        """Return reserved capacity remaining at a turn.

        Args:
            turn (int): Turn whose reservations should be checked.

        Returns:
            int: Number of available slots, or an unlimited sentinel for hubs.
        """
        if self._tag in [Tag.START_HUB, Tag.END_HUB]:
            return 999999

        reserved = self.__reservations.get(turn, 0)
        return self.MAX_DRONES - reserved

    def reserve(self, turn: int) -> None:
        """Reserve one zone slot for a turn.

        Args:
            turn (int): Turn in which the zone will be occupied.

        Raises:
            Exception: If the zone has no capacity at the requested turn.
        """
        if self.space_left_at(turn) <= 0:
            raise Exception(
                "Errore: impossibile prenotare la risorsa "
                f"{self.get_name()} al turno {turn}"
            )
        self.__reservations[turn] = self.__reservations.get(turn, 0) + 1
