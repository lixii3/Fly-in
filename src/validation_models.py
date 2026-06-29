from src.utils import ParsingTags, ParsingColors, ParsingZones
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self
from typing import List


class MetaData(BaseModel):
    tag: ParsingTags
    z_type: ParsingZones | None = None
    color: ParsingColors = ParsingColors.WHITE
    max_drones: int | None = Field(ge=0, default=None)
    max_link_capacity: int | None = Field(ge=0, default=None)

    @model_validator(mode="after")
    def validator(self) -> Self:

        if self.tag == ParsingTags.CONNECTION and not self.max_link_capacity:
            self.max_link_capacity = 1
        if not self.tag == ParsingTags.CONNECTION and self.max_link_capacity:
            raise ValueError("hubs expect "
                             "'max_link_capacity' field to be None")
        # start e end non hanno maxdrones e devono essere normal
        if (self.tag == ParsingTags.START_HUB or
            self.tag == ParsingTags.END_HUB) and self.z_type is None:
            self.z_type == ParsingZones.NORMAL

        if (self.tag == ParsingTags.START_HUB or
            self.tag == ParsingTags.END_HUB) and\
                (self.max_drones or self.z_type != ParsingZones.NORMAL or
                 self.z_type is not None):
            raise ValueError("Start / end hub can't have a "
                             "maximum number of drones allowed and must be normal zones")
        if self.tag == ParsingTags.CONNECTION and\
                (self.z_type or self.max_drones):
            raise ValueError("'connection' type_data expects "
                             "fields 'max_drones' and 'zone' to be None")
        if self.z_type == ParsingZones.BLOCKED:
            self.max_drones = 0
        return self


class HubData(BaseModel):
    tag: ParsingTags
    name: str = Field(min_length=1)
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    metadata: MetaData | None = None

    @model_validator(mode="after")
    def validator(self) -> Self:
        self.name = self.name.strip()
        if self.tag == ParsingTags.CONNECTION:
            raise ValueError("Invalid value for tag")
        # se il nome contiene spazi o un dash
        elif ' ' in self.name or '-' in self.name:
            raise ValueError("Hub name can't contain spaces or dashes")
        # se contiene metadata di tipo connection
        elif self.metadata and self.metadata.tag == ParsingTags.CONNECTION:
            ValueError(f"Invalid metadata for hub: '{self.name}'")

        return self


class ConnectionData(BaseModel):
    tag: ParsingTags = ParsingTags.CONNECTION
    name: str = Field(min_length=3)
    metadata: MetaData | None = None

    @model_validator(mode="after")
    def validator(self) -> Self:
        self.name = self.name.strip()
        if not self.tag == ParsingTags.CONNECTION:
            raise ValueError("Tag must be of type ParsingTags.CONNECTION")
        elif ' ' in self.name or self.name.count('-') != 1:
            raise ValueError("Connection name can't contain spaces "
                             "and must contain at most one dash")
        elif self.metadata and not self.metadata.tag == ParsingTags.CONNECTION:
            ValueError(f"Invalid metadata for connection: '{self.name}'")
        return self


class MapData(BaseModel):
    name: str = Field(min_length=1)
    nb_drones: int = Field(ge=0)
    hubs: List[HubData] = Field(min_length=2)
    connections: List[ConnectionData] = Field(min_length=1)

    @model_validator(mode="after")
    def validator(self) -> Self:
        has_start: int = 0
        has_end: int = 0
        names = [h.name for h in self.hubs]
        connA = [a.name.split('-')[0] for a in self.connections]
        connB = [b.name.split('-')[1] for b in self.connections]
        links = list(zip(connA, connB))
        for ln in links:
            if ln[0] == ln[1]:
                raise ValueError("Self loop detected: "
                                 f"'{ln[0]}-{ln[1]}'")

        for h in self.hubs:
            if h.tag == ParsingTags.START_HUB:
                has_start += 1
            elif h.tag == ParsingTags.END_HUB:
                has_end += 1
            # controllo che le hubs siano ben connesse
            if h.name not in connA or h.name not in connB:
                raise ValueError("Unreachable node")
            elif names.count(h.name) != 1:
                raise ValueError(f"Duplicated hub name in map: '{h.name}")

        if has_start != 1 or has_end != 1:
            raise ValueError("Map should have exactly one start "
                             "and one end hub")

        return self
