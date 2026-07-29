from fly_in.src.utils import ParsingZones, ParsingColors
from fly_in.src.validation_models import HubData
from typing import Final

# class ZoneException(Exception):
#     def __init__(self, msg: str):
#         super().__init__(msg)


class Zone:
    def __init__(self, data: HubData) -> None:
        self.__drones_in = 0
        self.__name = data.name
        self.__x = data.x
        self.__y = data.y
        self.__type = data.metadata.z_type
        self.__cost = self.__type.value
        self.__color = data.metadata.color
        self.MAX_DRONES: Final[int]= data.metadata.max_drones

    ##### GETTERS #######
    def get_name(self) -> str:
        return self.__name

    def get_x(self) -> int:
        return self.__x

    def get_y(self) -> int:
        return self.__y
    
    def get_cost(self) -> int:
        return self.__cost
    
    def get_type(self) -> ParsingZones:
        return self.__type

    def get_color(self) -> ParsingColors:
        return self.__color
    
    def get_coordinates(self) -> tuple[int, int]:
        return (self.__x, self.__y)

    def increment_drones(self) -> None:
        self.__drones_in += 1

    def decrement_drones(self) -> None:
        self.__drones_in -= 1