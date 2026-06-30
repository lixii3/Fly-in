from __future__ import annotations
from zone import Zone
from validation_models import ConnectionData, MetaData
from validation_models import ParsingColors, ParsingTags
from typing import Final, Iterable
from pydantic import ValidationError


class ConnectionException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

class Connection:
    def __init__(self, data: ConnectionData, zones: Iterable[Zone]) -> None:
        self.__name = data.name
        self.__arch: set[Zone, Zone] = {}
        self.__color = data.metadata.color
        self.MAX_LINK_CAPACITY: Final[int] = data.metadata.max_link_capacity

        for z in zones:
            if z.get_name == data.zoneA or z.get_name == data.zoneB:
                self.__arch.add(z)
        if len(self.__arch) != 2:
            raise ConnectionException("Invalid zone list parameter")

    @classmethod
    def manual_connection(cls, name: str, zoneA: Zone, zoneB: Zone,
                 color: str, max_link_capacity: int = 1) -> Connection:
        try:
            metadata: MetaData = MetaData(tag=ParsingTags.CONNECTION,
                                          color=ParsingColors.getColor(color),
                                          max_link_capacity=max_link_capacity)
            data: ConnectionData = ConnectionData(name=name, metadata=metadata)
        except ValidationError as e:
             raise e
        return cls(data, [zoneA, zoneB])

    def get_name(self) -> str:
            return self.__name

    def get_color(self) -> str:
            return self.__color

    def get_arch(self) -> set[Zone]:
         return self.__arch

