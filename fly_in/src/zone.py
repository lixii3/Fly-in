from __future__ import annotations
from fly_in.src.utils import ZoneType, ParsingColors, Tag
from typing import Final, TYPE_CHECKING
from fly_in.src.validation_models import HubData


if TYPE_CHECKING:
    from fly_in.src.drone import Drone

class ZoneException(Exception):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)
    
    def __str__(self):
        return self.msg


class Zone:
    def __init__(self, data: HubData) -> None:
        self.__drones_in: list[Drone] = []
        self.__name = data.name
        self.__x = data.x
        self.__y = data.y
        self.__type = data.metadata.z_type
        self.__cost = self.__type.value
        self.__color = data.metadata.color
        self._tag = data.tag
        
        max_d = data.metadata.max_drones
        self.MAX_DRONES: Final[int] = max_d if not max_d == None else 1
        self.__reservations: dict[int, int] = {}

    ##### GETTERS #######
    def get_name(self) -> str:
        return self.__name

    def get_x(self) -> int:
        return self.__x

    def get_y(self) -> int:
        return self.__y
    
    def get_cost(self) -> int:
        return self.__cost
    
    def get_type(self) -> ZoneType:
        return self.__type

    def get_color(self) -> ParsingColors:
        return self.__color
    
    def get_coordinates(self) -> tuple[int, int]:
        return (self.__x, self.__y)

    def drone_in(self, drone: Drone) -> None:
        if not self.space_left():
            raise ZoneException("Error: zone capacity is full, "
                                      f"unable to insert drone '{drone.ID}'")
        self.__drones_in.append(drone)
        drone.set_where(self)

    def drone_out(self, drone: Drone) -> None:
        try:
            self.__drones_in.remove(drone)
        except ValueError:
            raise ZoneException(f"Error: drone '{drone.ID}' is not present in"
                                f"zone '{self.__name}', unable to get it out")
        drone.set_where(None)

    def space_left(self) -> int:
        if self.MAX_DRONES:
            return self.MAX_DRONES - len(self.__drones_in)
        return -1

    def space_left_at(self, turn: int) -> int:
        if self._tag in [Tag.START_HUB, Tag.END_HUB]:
            return 999999
        
        reserved = self.__reservations.get(turn, 0)
        return self.MAX_DRONES - reserved

    def reserve(self, turn: int) -> None:
        if self.space_left_at(turn) <= 0:
            raise Exception(f"Errore: impossibile prenotare la risorsa {self.get_name()} al turno {turn}")
        self.__reservations[turn] = self.__reservations.get(turn, 0) + 1