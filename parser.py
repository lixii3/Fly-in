from graph import Graph, Zone, Connection
from typing import List, Dict
from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class ParsingTags(Enum):
    START_HUB = "start_hub"
    END_HUB = "end_hub"
    HUB = "hub"
    CONNECTION = "connection"


class ParsingZones(Enum):
    START = "start"
    END = "end"
    NORMAL = "normal"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class ParsingColors(Enum):
    RED = "#FF0000"
    GREEN = "#00FF00"
    BLUE = "#0000FF"
    YELLOW = "#FFFF00"
    WHITE = "#FFFFFF"
    PINK = "#E994D7"


class MetaData(BaseModel):
    type_data: str = Field(min_length=3)
    zone: ParsingZones | None = None
    color: ParsingColors = ParsingColors.WHITE
    max_drones: int | None = Field(ge=0, default=None)
    max_link_capacity: int | None = Field(ge=0, default=None)

    @model_validator(mode="after")
    def validator(self) -> Self:
        self.type_data = self.type_data.lower()
        if self.type_data not in ["hub", "connection"]:
            raise ValueError("Expecting type_data to be "
                             "either 'hub' or 'connection'")
        elif self.type_data == "hub" and self.max_link_capacity:
            raise ValueError("'hub' type_data expects "
                             "field 'max_link_capacity' to be None")
        elif self.type_data == 'connection' and self.zone or self.max_drones:
            raise ValueError("'connection' type_data expects "
                             "fields 'max_drones' and 'zone' to be None")
        
        return self


class HubData(BaseModel):
    tag: ParsingTags
    name: str = Field(min_length=1)
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    metadata: MetaData | None

    @model_validator(mode="after")
    def validator(self) -> Self:
        return self


class MapData(BaseModel):
    nb_drones: int = Field(ge=0)
    hubs: List[HubData] = Field(min_length=2)


class ParsingException(Exception):
    def __init__(self, map: str = '', line: int = 0, msg: str | None = None):
        self.msg = f"Error on line '{line}' in map {map}"\
                   if msg is None else msg
        self.map = map
        self.line = line
        super().__init__(self.msg, map, line)


class Parser:

    @staticmethod
    def parse_map(map: str) -> Graph:
        error_list: List[ParsingException] = []
        msg: str
        graph: Graph = Graph()
        g_name: str = map.rsplit("/", 1)[-1].split('.')[0]
        nb_drones: int
        start_hub: Zone
        end_hub: Zone
        to_raise: bool = False
        nb_line: int = 0
        try:
            with open(map, 'r') as file:
                row_count: int = 0
                for row in file:
                    tag: str = ''
                    name: str = ''
                    x: int = -1
                    y: int = -1
                    if row.strip() == '' or len(row.split('#', 1)) == 1:
                        continue
                    row = row.split('#', 1)[0]

                    # contollo prima riga
                    if row_count == 0 and row.startswith('nb_drones:'):
                        try:
                            nb_drones = Parser.__parse_nb_drones(row)
                        except ParsingException:
                            msg = f"Error on line {nb_line} of map '{g_name}':"
                            " first line must be 'nb_drones'"
                            error_list.append(ParsingException(g_name,
                                                               nb_line,
                                                               msg))
                        else:
                            row_count += 1
                        continue
                    
                    # se la prima riga che incontro non e' nb_drones
                    if row and row_count >= 1 and not nb_drones:
                        msg = f"Error on line {nb_line} of map '{name}': "
                        "first line must be 'nb_drones'"
                        error_list.append(ParsingException(g_name,
                                                           nb_line,
                                                           msg))



                    if to_raise:
                        raise ParsingException()
                    nb_line += 1
        except OSError as e:
            raise e

        return graph

    @staticmethod
    def __parse_nb_drones(row: str) -> int:
        tag: str
        nb_drones: str
        if len(row.split(':')) == 2:
            tag, nb_drones = row.split(':')
            if not tag.strip() == 'nb_drones' or not\
               nb_drones.strip().isdigit():
                raise ParsingException()
        return int(nb_drones)

    @staticmethod
    def __parse_zone(row: str) -> Dict[str, str]:
        tags: List[str] = ["start_hub", "end_hub", "hub", "connection"]

        zone_dict: Dict[str, str] = {}
        zone_data: List[str]
        metadata: List[str]
        tag: str
        row = row.strip()
        if len(row.split('[')) >= 1:
            zone_data = row.split("[")[0].split(' ')
            zone_data = [d for d in zone_data if d.replace(' ', '')]
            if len(row.split('[')) == 2:
                Parser.__parse_metadata(zone_data[1].split("]")[0])
        else:
            raise ParsingException()

        if len(row.split(':')) != 2:
            raise ParsingException
        if row.split(':')[0].strip() not in tags:
            raise ParsingException
        
        return zone_dict

    @staticmethod
    def __parse_metadata(row: str) -> Dict[str, str]:
        meta_dict: Dict[str, str] = {}
        metadata: List[str] = row.split(' ')
        key: str
        value: str

        for i in range(len(metadata)):
            tmp = metadata[i]
            if not tmp.strip():
                metadata.pop(i)
            elif not tmp.strip().startswith(tags):
                raise ParsingException()
            else:
                metadata[i] = tmp.strip()

        for d in metadata:
            if len(d.split('=')) == 2:
                key, value = d.split('=')
                value = value.strip()
            else:
                raise ParsingException()
            if key == "zone" and value not in t_zone:
                raise ParsingException()
            elif key == "color" and value not in colors:
                raise ParsingException()
            elif key == "max_drones" and not value.isdigit():
                raise ParsingException()
            if not meta_dict[key]:
                meta_dict[key] = value
            else:
                raise ParsingException()
        return meta_dict


if __name__ == "__main__":
    b = True if "    ".strip() else False
    print(b)
