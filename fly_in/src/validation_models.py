from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self
from typing import cast
from fly_in.src.utils import ParsingColors, Tag, ZoneType


class MetaData(BaseModel):
    """Validated metadata shared by hubs and connections."""

    tag: Tag
    z_type: ZoneType | None = None
    color: ParsingColors = ParsingColors.WHITE
    max_drones: int | None = Field(ge=0, default=None)
    max_link_capacity: int | None = Field(ge=0, default=None)
    nb_drones: int = 0

    @model_validator(mode="after")
    def validator(self) -> Self:
        """Validate and normalize metadata according to its tag."""
        if self.tag == Tag.CONNECTION and not self.max_link_capacity:
            self.max_link_capacity = 1
        if not self.tag == Tag.CONNECTION and self.max_link_capacity:
            raise ValueError("hubs expect 'max_link_capacity' "
                             "field to be None")
        if self.tag == Tag.START_HUB or self.tag == Tag.END_HUB:
            if (
                self.max_drones and self.max_drones < self.nb_drones
            ) or self.max_drones == 0:
                raise ValueError(
                    "Max drone capacity is forbidden for "
                    "hub of type estart/end"
                )
            # start e end devono essere normal
            if self.z_type is None:
                self.z_type = ZoneType.NORMAL
            elif self.z_type != ZoneType.NORMAL:
                raise ValueError("Start / end must be normal zones")

        if self.tag == Tag.CONNECTION and (self.z_type or self.max_drones):
            raise ValueError(
                "'connection' type_data expects "
                "fields 'max_drones' and 'zone' to be None"
            )
        if self.z_type == ZoneType.BLOCKED:
            self.max_drones = 0
        elif self.z_type is None and self.tag != Tag.CONNECTION:
            self.z_type = ZoneType.NORMAL
        return self

    @classmethod
    def default_meta(cls, tag: Tag) -> "MetaData":
        return MetaData(tag=tag)


class HubData(BaseModel):
    """Validated hub declaration from a map file."""

    tag: Tag
    name: str = Field(min_length=1)
    x: int = -1
    y: int = -1
    metadata: MetaData

    @model_validator(mode="after")
    def validator(self) -> Self:
        """Validate hub naming, metadata, and coordinates."""
        self.name = self.name.strip()
        if self.tag == Tag.CONNECTION:
            raise ValueError("Invalid value for tag")
        # se il nome contiene spazi o un dash
        elif " " in self.name or "-" in self.name:
            raise ValueError("Hub name can't contain spaces or dashes")
        if not self.metadata:
            max_d: int | None
            if self.tag != Tag.START_HUB and self.tag != Tag.END_HUB:
                max_d = 1
            else:
                max_d = None
            self.metadata = MetaData(
                tag=self.tag, z_type=ZoneType.NORMAL, max_drones=max_d
            )
        # se contiene metadata di tipo connection
        elif self.metadata and self.metadata.tag == Tag.CONNECTION:
            raise ValueError(f"Invalid metadata for hub: '{self.name}'")
        return self


class ConnectionData(BaseModel):
    """Validated connection declaration from a map file."""

    tag: Tag = Tag.CONNECTION
    name: str = Field(min_length=3)
    metadata: MetaData
    zoneA: str = ""
    zoneB: str = ""

    @model_validator(mode="after")
    def validator(self) -> Self:
        """Validate a connection name and derive its endpoint names."""
        self.name = self.name.strip()
        if not self.tag == Tag.CONNECTION:
            raise ValueError("Tag must be of type ParsingTags.CONNECTION")
        elif " " in self.name or self.name.count("-") != 1:
            raise ValueError(
                "Connection name can't contain spaces and must contain "
                "exactly one dash"
            )
        elif self.metadata and not self.metadata.tag == Tag.CONNECTION:
            raise ValueError(f"Invalid metadata for connection: '{self.name}'")
        if not self.metadata:
            self.metadata = MetaData(tag=Tag.CONNECTION, max_link_capacity=1)
        self.zoneA = self.name.split("-")[0]
        self.zoneB = self.name.split("-")[1]
        if not self.zoneA or not self.zoneB or (self.zoneA == self.zoneB):
            raise ValueError("Invalid self connection")
        return self


class MapData(BaseModel):
    """Validated complete map definition."""

    name: str = Field(min_length=1)
    nb_drones: int = Field(ge=0)
    hubs: list[HubData] = Field(min_length=2)
    connections: list[ConnectionData] = Field(min_length=1)

    @model_validator(mode="after")
    def validator(self) -> Self:
        """Validate map connectivity, uniqueness, and hub requirements."""
        has_start: int = 0
        has_end: int = 0
        names = [h.name for h in self.hubs]
        connA = [c.zoneA for c in self.connections]
        connB = [c.zoneB for c in self.connections]

        links = list(zip(connA, connB))
        visti: set[tuple[str, str]] = set()

        # check for duplicated connections (even if reversed)
        for ln in links:
            l1: tuple[str, str] = cast(tuple[str, str], tuple(ln))
            lrev: tuple[str, str] = (l1[1], l1[0])
            if l1 in visti or lrev in visti:
                raise ValueError(f"Duplicted connection: '{ln[0]}-{ln[1]}'")
            else:
                visti.add(l1)
                visti.add(lrev)

        for h in self.hubs:
            if h.tag == Tag.START_HUB:
                has_start += 1
            elif h.tag == Tag.END_HUB:
                has_end += 1
            # controllo che non ci siano hub duplicate
            if names.count(h.name) != 1:
                raise ValueError(f"Duplicated hub name in map: '{h.name}")

        if has_start != 1 or has_end != 1:
            raise ValueError("Map should have exactly one start "
                             "and one end hub")

        return self
