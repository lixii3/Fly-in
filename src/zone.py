from src.utils import ParsingZones
from src.validation_models import HubData

# class ZoneException(Exception):
#     def __init__(self, msg: str):
#         super().__init__(msg)


class Zone:
    def __init__(self, data: HubData) -> None:
        self.__drones_in = 0
        self.__name = data.name
        self.__x = data.x
        self.__y = data.y
        if data.metadata.z_type == ParsingZones.NORMAL:
            self.__type == ParsingZones.NORMAL
        else:
            self.__type = data.metadata.z_type
        self.__cost = self.__type.value[1]
        self._color = data.metadata.color
        self.__max_drones = data.metadata.max_drones

    # def get_name(self) -> str:
    #     return self.__name

    # def get_type(self) -> ParsingZones:
    #     return self.__type

    # def get_max_drones(self) -> int:
    #     return self.__max_drones

    # def get_color(self) -> str:
    #     return self.__color

    # def increment_drones(self) -> None:
    #     self.__drones_in += 1

    # def decrement_drones(self) -> None:
    #     self.__drones_in -= 1