from graph import Graph, Zone, Connection
from typing import List, Dict
from enum import Enum


class ParsingTags(Enum):
    START_HUB = "start_hub"
    END_HUB = "end_hub"
    HUB = "hub"
    CONNECTION = "connection"
    TAGS = [START_HUB, END_HUB, HUB, CONNECTION]


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
    def parse_zone(row: str) -> Dict[str, str]:
        tags: List[str] = ["start_hub", "end_hub", "hub", "connection"]

        zone_dict: Dict[str, str] = {}
        zone_data: List[str]
        metadata: List[str]
        tag: str
        row = row.strip()
        try:
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

        except ParsingException as e:
            raise e
        return zone_dict

    @staticmethod
    def __parse_metadata(row: str) -> Dict[str, str]:
        tags: tuple = ("zone", "color", "max_drones")
        meta_dict: Dict[str, str] = {}
        metadata: List[str] = row.split(' ')
        metadata = [d for d in metadata
                    if d.strip().startswith(tags)]
        
        return meta_dict


if __name__ == "__main__":
    b = True if '  '.replace(' ', '') else False
    print(b)
