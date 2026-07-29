from __future__ import annotations
from typing import Final, TYPE_CHECKING
from fly_in.src.utils import ParsingTags


if TYPE_CHECKING:
    from fly_in.src.zone import Zone
    from fly_in.src.connection import Connection
class Drone:
    __counter = 0
    def __init__(self) -> None:
        self.ID: Final[str] = f"DR-0{str(self.__counter).zfill(4)}"
        self.__where: Zone | Connection = None
        self.__counter += 1

    def set_where(self, where: Zone | Connection | None) -> None:
        self.__where = where

    def get_where(self) -> Zone:
        return self.__where

    def at_end(self) -> bool:
        return self.__where.get_type() == ParsingTags.END_HUB
    
    def at_start(self) -> bool:
        return self.__where.get_type() == ParsingTags.START_HUB

# if __name__ == "__main__":
#     print(str(115).zfill(10))
