from graph import Graph, Zone, Connection
from typing import List


class ParsingException(Exception):
    def __init__(self, msg: str = '', map: str = '', line: str = ''):
        self.msg = msg
        self.map = map
        self.line = line
        super().__init__(msg, map, line)


class Parser:
    @staticmethod
    def parse_map(map: str) -> Graph:
        error_list: List[ParsingException] = []
        graph: Graph = Graph()
        g_name: str = map.rsplit("/", 1)[-1].split('.')[0]
        nb_drones: str
        start_hub: Zone
        end_hub: Zone
        to_raise: bool = False
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
                        if len(row.split(':')) == 2:
                            tag, nb_drones = row.split(':')
                            if not tag.strip() == 'nb_drones' or not\
                               nb_drones.strip().isdigit():
                                to_raise = True
                    if to_raise:
                        raise ParsingException(f"Error on map '{g_name}': "
                                               f"line '{row}'")
                    row_count += 1
        except ParsingException as e:
            error_list.append(e)
        except OSError as e:
            raise e

        return graph

    @staticmethod
    def __parse_nb_drones(row: str, graph: Graph) -> int:
        tag: str
        nb_drones: str
        if len(row.split(':')) == 2:
            tag, nb_drones = row.split(':')
            if not tag.strip() == 'nb_drones' or not\
               nb_drones.strip().isdigit():
                raise ParsingException(f"Error on map '{graph.name}': "
                                       "expecting first line to be "
                                       "'nb_drones: <integer>', got: "
                                       f"'{row}'")
        return int(nb_drones)


if __name__ == "__main__":
    print(int('a'))