from graph import Graph
from utils import ParsingColors, ParsingTags, ParsingZones
from validation_models import MetaData, ConnectionData, HubData, MapData
from typing import List, Dict
from pydantic import ValidationError
from typing_extensions import Self


class ParsingException(Exception):
    def __init__(self, map_name: str = '', line: int = 0, msg: str | None = None):
        self.msg = msg
        self.map = map_name
        self.line = line
        self.fmsg = f"Error on line {line} in map '{map_name}': {msg}"
        super().__init__(self.fmsg, map_name, line)


class Parser:

    @staticmethod
    def parse_map(map: str) -> Graph:
        error_list: List[ParsingException] = []
        graph: Graph
        g_name: str = map.rsplit("/", 1)[-1].split('.')[0]
        nb_drones: int
        hub_list: List[HubData] = []
        conn_list: List[ConnectionData] = []
        map_data: MapData
        nb_line: int = 1
        try:
            with open(map, 'r') as file:
                row_count: int = 0
                for row in file:
                    row = row.split('#')[0]
                    if row.strip() == '':
                        nb_line += 1
                        continue
                    row_count += 1

                    # contollo prima riga
                    if row_count == 1 and row.startswith('nb_drones:'):
                        try:
                            nb_drones = Parser._parse_nb_drones(row)
                        except ParsingException as e:
                            error_list.append(ParsingException(g_name,
                                                               nb_line,
                                                               e.msg))
                        else:
                            row_count += 1
                        nb_line += 1
                        continue
                    # se la prima riga che incontro non e' nb_drones
                    elif row and row_count >= 1 and not nb_drones:
                        error_list.append(ParsingException(g_name,
                                                           nb_line,
                                                           "first line must be 'nb_drones'"))
                        nb_line += 1
                        continue
                    try:
                        data = Parser._parse_zone(row)
                        if isinstance(data, HubData):
                            hub_list.append(data)
                        else:
                            conn_list.append(data)
                    except ParsingException as e:
                        error_list.append(ParsingException(g_name,
                                                           nb_line,
                                                           e.msg))
                    nb_line += 1
        except OSError as e:
            raise e

        # stampa errori e raise finale
        if len(error_list) > 0:
            for e in error_list:
                print(e.fmsg)
            raise ParsingException(msg="Try with a different map or fix this one pls!")
        try:
            map_data = MapData(name=g_name, nb_drones=nb_drones,
                           hubs=hub_list, connections=conn_list)
        except ValidationError as e:
            raise e
        graph = Graph(map_data)
        return graph

    @staticmethod
    def _parse_nb_drones(row: str) -> int:
        tag: str
        nb_drones: str
        if len(row.split(':')) == 2:
            tag, nb_drones = row.split(':')
            if not tag.strip() == 'nb_drones':
                raise ParsingException(msg="first line must be nb_drones")
            elif not nb_drones.strip().isdigit():
                raise ParsingException(msg="nbr_drones must be a positive integer")
        return int(nb_drones)

    @staticmethod
    def _parse_zone(row: str) -> ConnectionData | HubData:
        line: str = row.split('[')[0]
        data: ConnectionData | HubData
        tag: ParsingTags
        metadata: MetaData | None
        name: str = ""
        x: int = -1
        y: int = -1

        if ':' not in line:
            raise ParsingException(msg="Invalid tag")
        tag = ParsingTags.getTag(line.split(':')[0])
        if tag is None:
            raise ParsingException(msg="Invalid tag")
        line.split(':')[1]
        # se e' una hub trovo x e y
        args = line.strip().split(' ')
        if tag != ParsingTags.CONNECTION and len(args) == 3:
            name = args[0]
            try:
                x = int(line.strip().split(' ')[1])
                y = int(line.strip().split(' ')[2])
                if x < 0 or y < 0:
                    raise ValueError("Coordinates must be positive integers")
            except ValueError as e:
                raise ParsingException(msg=e.args[0])

        try:
            metadata = Parser._parse_metadata(row, tag)
            if tag != ParsingTags.CONNECTION:
                data = HubData(tag=tag, name=name, x=x, y=y, metadata=metadata)
            else:
                data = ConnectionData(tag=tag, name=name, metadata=metadata)
        except ValidationError as e:
            raise ParsingException(msg=e.errors())
        except ParsingException as e:
            raise e
        return data

    @staticmethod
    def _parse_metadata(row: str, tag: ParsingTags) -> MetaData:
        data: MetaData
        _tags: tuple = ('color', 'zone', 'max_drones', 'max_link_capacity')
        # controllo e tolgo le quadre
        if len(row.split('[')) == 2:
            line = row.split('[')[1]
            if not line.count("]") == 1 and not line.strip().endswith(']'):
                raise ParsingException(msg="Parser 144: invalid metadata")
            line = line.split("]")[0]
        else:
            raise ParsingException(msg="invalid metadata")

        meta_dict: Dict[str, str] = {}
        metadata: List[str] = line.split(' ')
        key: str
        value: str

        for i in range(len(metadata)):
            tmp = metadata[i].strip()
            if tmp.count('=') != 1 or tmp.startswith('=') or\
                tmp.endswith('=') or ' ' in tmp:
                raise ParsingException(msg="invalid metadata")
            key, value = tmp.split('=')
            if key not in _tags or key in meta_dict:
                raise ParsingException(msg="invalid metadata")
            if key == 'zone':
                meta_dict[key] = ParsingZones.getZone(value)
                if meta_dict[key] is None:
                    raise ParsingException(msg="invalid zone value in metadata")
            elif key == 'color':
                meta_dict[key] = ParsingColors.getColor(value)
                if meta_dict[key] is None:
                    raise ParsingException(msg="invalid color value metadata")
            elif key == 'max_drones' or key == 'max_link_capacity':
                try:
                    int(value)
                except ValueError:
                    raise ParsingException(msg="invalid max_drones in metadata")
        try:
            data = MetaData(tag=tag.value,
                            z_type=meta_dict.get('zone'),
                            color=meta_dict.get('color'),
                            max_drones=meta_dict.get('max_drones'),
                            max_link_capacity=meta_dict.get('max_link_capacity'))
        except ValidationError as e:
            print(e)
            raise ParsingException(f"invalid metadata for type {tag}")
        return data


if __name__ == "__main__":
    try:
        g: Graph = Parser.parse_map("maps/easy/01_linear_path.txt")
    except ParsingException as e:
        print(e.msg)
