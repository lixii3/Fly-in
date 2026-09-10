from __future__ import annotations
from typing import Final, TYPE_CHECKING
from fly_in.src.utils import Tag, Action
from fly_in.src.zone import Zone

if TYPE_CHECKING:
    from fly_in.src.connection import Connection


class Drone:
    """Represent a drone and its scheduled movement path."""

    _counter = 0

    def __init__(self) -> None:
        """Create a drone with a unique identifier and empty route."""
        self.ID: Final[str] = f"D{Drone._counter}"
        self.__where: Zone | Connection | None = None
        self.__last_pos: Zone | Connection | None = None
        Drone._counter += 1
        self.progress = 0.0
        self.path: list[tuple[Action, Zone | Connection, int]] = []

    def set_where(self, where: Zone | Connection | None) -> None:
        """Update the drone location while retaining its previous location.

        Args:
            where (Zone | Connection | None): New location or no location.
        """
        self.__last_pos = self.__where
        self.__where = where

    def set_last_pos(self, where: Zone | Connection | None) -> None:
        """Set the drone's previous location.

        Args:
            where (Zone | Connection | None): Previous location to store.
        """
        self.__last_pos = where

    def get_where(self) -> Zone | Connection | None:
        """Return the drone's current location."""
        return self.__where

    def get_last_pos(self) -> Zone | Connection | None:
        """Return the drone's previous location."""
        return self.__last_pos

    def get_coordinates(self) -> tuple[float, float]:
        """Return the current location coordinates, or the origin if unset."""
        where = self.get_where()

        if where:
            return where.get_coordinates()
        return (0.0, 0.0)

    def get_action_at_turn(self,
                           turn: int) -> tuple[Action,
                                               Zone | Connection |
                                               None,
                                               int]:
        """Return the scheduled action for a turn.

        Args:
            turn (int): Turn whose action should be retrieved.

        Returns:
            tuple[Action, Zone | Connection, int]: Action, resource, and turn,
                or an empty action when no action is scheduled.
        """
        for a, r, t in self.path:
            if t == turn:
                return (a, r, t)
        return (Action.NONE, None, 0)

    def set_path(self, path: list[tuple[Action,
                                        Zone | Connection,
                                        int]]) -> None:
        """Replace the drone's scheduled path.

        Args:
            path (list[tuple[Action, Zone | Connection, int]]): \
                Scheduled moves.
        """
        self.path = path

    def at_end(self) -> bool:
        """Return whether the drone is currently at the end hub."""
        where = self.get_where()
        if isinstance(where, Zone):
            return where._tag == Tag.END_HUB
        return False

    def at_start(self) -> bool:
        """Return whether the drone is currently at the start hub."""
        where = self.get_where()
        if isinstance(where, Zone):
            return where._tag == Tag.START_HUB
        return False

    @classmethod
    def zeroCounter(cls) -> None:
        """Reset the class-wide drone identifier counter."""
        cls._counter = 0
