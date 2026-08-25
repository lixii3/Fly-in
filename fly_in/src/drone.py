from __future__ import annotations
from typing import Final, TYPE_CHECKING
from fly_in.src.utils import Tag, Action

if TYPE_CHECKING:
    from fly_in.src.zone import Zone
    from fly_in.src.connection import Connection

class Drone:
    _counter = 0

    def __init__(self) -> None:
        self.ID: Final[str] = f"D{Drone._counter}"
        self.__where: Zone | Connection = None
        self.__last_pos: Zone | Connection = None
        Drone._counter += 1
        self.speed = 1.0
        self.progress = 0.0
        self.path: list[tuple[Action, Zone | Connection, int]]= []

    def set_where(self, where: Zone | Connection | None) -> None:
        self.__last_pos = self.__where
        self.__where = where
        
    def set_last_pos(self, where: Zone | Connection | None) -> None:
        self.__last_pos = where
    
    def update_speed(self) -> None:
        where = self.get_where()
        self.speed = 1.0
        
        if where and type(where).__name__ == "Zone":
            self.speed /= float(where.get_type().value())

    def get_where(self) -> Zone | Connection:
        return self.__where
    
    def get_last_pos(self) -> Zone | Connection:
        return self.__last_pos
    
    def get_coordinates(self) -> tuple[float, float]:
        where = self.get_where()
        
        if where and type(where).__name__ == "Zone":
            return where.get_coordinates()
        elif where:
            return where.get_coordinates_at(self.progress)
            
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
        if where and type(where).__name__ == "Zone":
            return where.get_type() == Tag.END_HUB
        return False
    
    def at_start(self) -> bool:
        where = self.get_where()
        if where and type(where).__name__ == "Zone":
            return where.get_type() == Tag.START_HUB
        return False

    def update(self, base_step: float) -> None:
        where = self.get_where()
        
        if where and type(where).__name__ == "Connection":
            cost = where.get_zoneA().get_cost()
            actual_step = base_step / cost
            
            self.progress += actual_step
  
            if self.progress >= 1.0:
                self.progress = 1.0
                
                # Spostiamo il drone sul nodo di destinazione
                self.set_where(where.get_zoneB())
                self.progress = 0.0
                
                # Aggiorniamo la velocità in base al nuovo nodo raggiunto
                self.update_speed()