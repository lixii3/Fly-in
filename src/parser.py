from src.graph import Graph
from src.utils import ParsingColors, ParsingTags, ParsingZones
from src.validation_models import MetaData, ConnectionData, HubData, MapData
from typing import List, Dict
from pydantic import ValidationError
from typing_extensions import Self


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
        hub_list: List[HubData] = []
        conn_list: List[ConnectionData] = []
        map_data: MapData
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
                    if row:
                        row_count += 1

                    # contollo prima riga
                    if row_count == 0 and row.startswith('nb_drones:'):
                        try:
                            nb_drones = Parser._parse_nb_drones(row)
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
                    elif row and row_count >= 1 and not nb_drones:
                        msg = f"Error on line {nb_line} of map '{name}': "
                        "first line must be 'nb_drones'"
                        error_list.append(ParsingException(g_name,
                                                           nb_line,
                                                           msg))
                        continue
                    try:
                        data = Parser._parse_zone(row)
                        if isinstance(data, HubData):
                            hub_list.append(data)
                        else:
                            conn_list.append(data)
                    except ParsingException:
                        error_list.append(ParsingException(g_name,
                                                           nb_line,
                                                           msg))
                    nb_line += 1
        except OSError as e:
            raise e
        map_data = MapData(name=g_name, nb_drones=nb_drones,
                           hubs=hub_list, connections=conn_list)
        graph = Graph(map_data)
        return graph

    @staticmethod
    def _parse_nb_drones(row: str) -> int:
        tag: str
        nb_drones: str
        if len(row.split(':')) == 2:
            tag, nb_drones = row.split(':')
            if not tag.strip() == 'nb_drones' or not\
               nb_drones.strip().isdigit():
                raise ParsingException()
        return int(nb_drones)

    @staticmethod
    def _parse_zone(row: str) -> ConnectionData | HubData:
        line: str = row.split('[')[0]
        # tags: List[str] = ['start_hub', 'end_hub', 'hub', 'connection']
        data: ConnectionData | HubData
        tag: ParsingTags
        metadata: MetaData | None
        name: str = ""
        x: int = -1
        y: int = -1

        if ':' not in line:
            raise ParsingException()
        tag = ParsingTags.getTag(line.split(':')[0])
        if tag is None:
            raise ParsingException()
        line.split(':')[1]
        # se e' una hub trovo x e y
        args = line.strip().split(' ')
        if tag != ParsingTags.CONNECTION and len(args) == 3:
            name = args[0]
            try:
                x = int(line.strip().split(' ')[1])
                y = int(line.strip().split(' ')[2])
            except ValueError:
                raise ParsingException()

        try:
            metadata = Parser._parse_metadata(row, tag)
            if tag != ParsingTags.CONNECTION:
                data = HubData(tag=tag, name=name, x=x, y=y, metadata=metadata)
            else:
                data = ConnectionData(tag=tag, name=name, metadata=metadata)
        except ValidationError:
            raise ParsingException()
        return data

    @staticmethod
    def _parse_metadata(row: str, tag: ParsingTags) -> MetaData:
        data: MetaData
        _tags: tuple = ('color', 'zone', 'max_drones', 'max_link_capacity')
        # controllo e tolgo le quadre
        if len(row.split('[')) == 2:
            line = row.split('[')[1]
            if not line.count("]") == 1 and not line.strip().endswith(']'):
                raise ParsingException()
            line = line.split("]")[0]
        else:
            raise ParsingException()

        meta_dict: Dict[str, str] = {}
        metadata: List[str] = line.split(' ')
        key: str
        value: str

        for i in range(len(metadata)):
            tmp = metadata[i].strip()
            if tmp.count('=') != 1 or tmp.startswith('=') or\
                tmp.endswith('=') or ' ' in tmp:
                raise ParsingException()
            key, value = tmp.split('=')
            if key not in _tags or meta_dict[key]:
                raise ParsingException()
            if key == 'zone':
                meta_dict[key] = ParsingZones.getZone(value)
                if meta_dict[key] is None:
                    raise ParsingException()
            elif key == 'color':
                meta_dict[key] = ParsingColors.getColor(value)
                if meta_dict[key] is None:
                    raise ParsingException()
            elif key == 'max_drones' or key == 'max_link_capacity':
                try:
                    int(value)
                except ValueError:
                    raise ParsingException()
        try:
            data = MetaData(tag=meta_dict.get('tag'),
                            z_type=meta_dict.get('zone'),
                            color=meta_dict.get('color'),
                            max_drones=meta_dict.get('max_drones'),
                            max_link_capacity=meta_dict.get('max_link_capacity'))
        except ValidationError:
            raise ParsingException()
        return data


if __name__ == "__main__":
    b = 'hub'
    print(b == ParsingTags.HUB)
