from fly_in.src.graph import Graph, GraphException
from fly_in.src.utils import ParsingColors, ParsingTags, ParsingZones
from fly_in.src.validation_models import MetaData, ConnectionData, HubData, MapData
from typing import List, Dict
from pydantic import ValidationError


class ParsingException(Exception):
    def __init__(self, map_name: str = '', line: int = -1,
                 msg: str | None = None):
        self.msg = msg
        self.map = map_name
        self.line = line
        self.fmsg = f"Error on line {line} in map '{map_name}': {msg}"
        if line == -1:
            self.fmsg = f"Error in map '{map_name}': {msg}"
        super().__init__(self.fmsg, map_name, line)

    def __str__(self):
        return self.fmsg

class MultipleParsingExceptions(Exception):
    def __init__(self, errors: list[ParsingException]):
        self.errors = errors
        # Generiamo un messaggio riassuntivo che mostra il numero di errori
        self.msg = f"Parsing fallito: trovati {len(errors)} errori."
        super().__init__(self.msg)

    def __str__(self):
        output: str = ""
        for e in self.errors:
            output += str(e) + '\n'
        return output

class Parser:

    @staticmethod
    def parse_map(map: str) -> Graph:
        error_list: List[ParsingException] = []
        graph: Graph
        g_name: str = map.rsplit("/", 1)[-1].split('.')[0]
        nb_drones: int = -1
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
                    elif row and row_count >= 1 and nb_drones == -1:
                        error_list.append(ParsingException(g_name,
                                                           nb_line,
                                                           "first line must be 'nb_drones'"))
                        nb_line += 1
                        continue
                    try:
                        data = Parser._parse_zone(row, nb_drones)
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
            raise MultipleParsingExceptions(error_list)
        try:
            map_data = MapData(name=g_name, nb_drones=nb_drones,
                               hubs=hub_list, connections=conn_list)
        except ValidationError as e:
            raise ParsingException(map_name=g_name, msg=e.errors()[0].get('msg',  "no message"))
        try:
            graph = Graph(map_data)
        except GraphException as e:
            raise ParsingException(map_name=g_name, msg=str(e))
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
    def _parse_zone(row: str, nb_drones: int) -> ConnectionData | HubData:
        line: str = row.split('[')[0]
        data: ConnectionData | HubData
        tag: ParsingTags
        meta_line: str
        metadata: MetaData = None
        name: str = ""
        x: int = -1
        y: int = -1


        if ':' not in line:
            raise ParsingException(msg="Missing ':' after tag")
        tag = ParsingTags.getTag(line.split(':')[0])
        if tag is None:
            raise ParsingException(msg="Invalid tag")

        line = line.split(':')[1]
        args = line.strip().split()

        # se e' una hub trovo x e y
        if tag != ParsingTags.CONNECTION and len(args) == 3:
            name = args[0]
            try:
                x = int(args[1])
                y = int(args[2])
            except ValueError as e:
                raise ParsingException(msg="Invalid non integers coordinates")
        elif tag == ParsingTags.CONNECTION and len(args) == 1:
            name = args[0]
        else:
            raise ParsingException(msg=f"Invalid line format for data of type {tag.value}")

        if len(row.split('[')) == 2:
            meta_line = row.split('[')[1]
            if meta_line.count("]") == 1 and meta_line.strip().endswith(']'):
                meta_line = meta_line.split("]")[0]
                try:
                    metadata = Parser._parse_metadata(meta_line, tag, nb_drones)
                except ParsingException as e:
                    raise e
            else:
                raise ParsingException(msg='Invalid metadata format')

        try:
            if tag != ParsingTags.CONNECTION:
                data = HubData(tag=tag, name=name, x=x, y=y, metadata=metadata)
            else:
                data = ConnectionData(tag=tag, name=name, metadata=metadata)
        except ValidationError as e:
            raise ParsingException(msg=e.errors()[0]['msg'])
        except ParsingException as e:
            raise e
        return data

    @staticmethod
    def _parse_metadata(row: str, tag: ParsingTags, nb_drones: int) -> MetaData:
        data: MetaData
        _tags: tuple = ('color', 'zone', 'max_drones', 'max_link_capacity')
        meta_dict: Dict[str, str] = {}
        metadata: List[str] = row.split()
        key: str
        value: str

        if len(metadata) == 0:
            raise ParsingException(msg="Invalid empty metadata")

        for i in range(len(metadata)):
            tmp = metadata[i].strip()
            if tmp.count('=') != 1 or tmp.startswith('=') or\
                tmp.endswith('=') or ' ' in tmp:
                raise ParsingException(msg="Invalid metadata")
            key, value = tmp.split('=')
            if key not in _tags or key in meta_dict:
                raise ParsingException(msg="Invalid metadata")
            if key == 'zone':
                meta_dict[key] = ParsingZones.getZone(value)
                if meta_dict[key] is None:
                    raise ParsingException(msg="Invalid zone value in metadata")
            elif key == 'color':
                meta_dict[key] = ParsingColors.getColor(value)
                if meta_dict[key] is None:
                    raise ParsingException(msg="Invalid color value metadata")
            elif key == 'max_drones' or key == 'max_link_capacity':
                try:
                    int(value)
                except ValueError:
                    raise ParsingException(msg="Invalid max_drones in metadata")
                meta_dict[key] = int(value)
        try:
            data = MetaData(tag=tag.value,
                            z_type=meta_dict.get('zone'),
                            color=meta_dict.get('color', ParsingColors.WHITE),
                            max_drones=meta_dict.get('max_drones', None),
                            max_link_capacity=meta_dict.get('max_link_capacity'),
                            nb_drones=nb_drones)
        except ValidationError as e:
            raise ParsingException(msg=e.errors()[0]['msg'])
        return data
