from __future__ import annotations
from typing import Final, TYPE_CHECKING
from fly_in.src.utils import Tag, Action
from fly_in.src.zone import Zone

if TYPE_CHECKING:
    from fly_in.src.connection import Connection

class Drone:
    _counter = 0

    def __init__(self) -> None:
        self.ID: Final[str] = f"D{Drone._counter}"
        self.__where: Zone | Connection = None
        self.__last_pos: Zone | Connection = None
        Drone._counter += 1
        self.progress = 0.0
        self.path: list[tuple[Action, Zone | Connection, int]]= []

    def set_where(self, where: Zone | Connection | None) -> None:
        self.__last_pos = self.__where
        self.__where = where
        
    def set_last_pos(self, where: Zone | Connection | None) -> None:
        self.__last_pos = where


    def get_where(self) -> Zone | Connection:
        return self.__where
    
    def get_last_pos(self) -> Zone | Connection:
        return self.__last_pos
    
    def get_coordinates(self) -> tuple[float, float]:
        where = self.get_where()
        
        if where:
            return where.get_coordinates()
        return (0.0, 0.0)

    def get_action_at_turn(self, turn: int) -> tuple[Action, Zone | Connection, int]:
        for a, r, t in self.path:
            if t == turn:
                return (a, r, t)
        return (Action.NONE, None, 0)
            
    def set_path(self, path: list[tuple[Action, Zone | Connection, int]]) -> None:
        self.path = path

    def at_end(self) -> bool:
        where = self.get_where()
        if isinstance(where, Zone):
            return where == Tag.END_HUB
        return False
    
    def at_start(self) -> bool:
        where = self.get_where()
        if isinstance(where, Zone):
            return where == Tag.START_HUB
        return False


    
    @classmethod
    def zeroCounter(cls) -> None:
        cls._counter = 0