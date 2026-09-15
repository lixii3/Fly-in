from fly_in.src.graph import Graph, GraphException
from fly_in.src.utils import Tag, ZoneType
from fly_in.src.validation_models import MetaData, ConnectionData, \
    HubData, MapData
from typing import List, Dict, cast
from pydantic import ValidationError


class ParsingException(Exception):
    """Exception raised for an invalid map declaration."""

    def __init__(self, map_name: str = "",
                 line: int = -1,
                 msg: str | None = None,
                 fmsg: str = "") -> None:
        """Initialize a parsing error with optional map and line context.

        Args:
            map_name (str, optional): Name of the map being parsed.
            line (int, optional): Source line containing the error.
            msg (str | None, optional): Error description.
            fmsg (str, optional): Preformatted error message.
        """
        self.msg = msg
        self.map = map_name
        self.line = line
        self.fmsg = fmsg
        if self.fmsg == "":
            self.fmsg = f"Error on line {line} in map '{map_name}': {msg}"
        if line == -1:
            self.fmsg = f"Error in map '{map_name}': {msg}"
        super().__init__(self.fmsg, map_name, line)

    def __str__(self) -> str:
        """Return the formatted parsing error."""
        return "Parsing Exception: " + self.fmsg


class MultipleParsingExceptions(Exception):
    """Exception aggregating multiple map parsing errors."""

    def __init__(self, errors: list[ParsingException]) -> None:
        """Initialize an exception containing multiple parsing errors.

        Args:
            errors (list[ParsingException]): Errors collected during parsing.
        """
        self.errors = errors
        # Generiamo un messaggio riassuntivo che mostra il numero di errori
        self.msg = f"Parsing fallito: trovati {len(errors)} errori."
        super().__init__(self.msg)

    def __str__(self) -> str:
        """Return all contained parsing errors."""
        output: str = ""
        for e in self.errors:
            output += str(e) + "\n"
        return output


class Parser:
    """Parse map files into validated graph objects."""

    @staticmethod
    def parse_map(map: str) -> Graph:
        """Parse a map file into a graph.

        Args:
            map (str): Path to the map file.

        Returns:
            Graph: Graph created from the parsed map.

        Raises:
            ParsingException: If the file or map structure is invalid.
            MultipleParsingExceptions: If multiple line errors are found.
        """
        error_list: List[ParsingException] = []
        graph: Graph
        g_name: str = map.rsplit("/", 1)[-1].split(".")[0]
        nb_drones: int = -1
        hub_list: List[HubData] = []
        conn_list: List[ConnectionData] = []
        map_data: MapData
        nb_line: int = 1
        try:
            with open(map, "r") as file:
                row_count: int = 0
                for row in file:
                    row = row.split("#")[0]
                    if row.strip() == "":
                        nb_line += 1
                        continue
                    row_count += 1

                    # contollo prima riga
                    if row_count == 1 and row.startswith("nb_drones:"):
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
                        error_list.append(
                            ParsingException(
                                g_name, nb_line, "first line must "
                                "be 'nb_drones'"
                            )
                        )
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
        except OSError:
            raise ParsingException(msg="Map name not found in directory")

        # stampa errori e raise finale
        if len(error_list) > 0:
            raise MultipleParsingExceptions(error_list)
        try:
            map_data = MapData(
                name=g_name, nb_drones=nb_drones,
                hubs=hub_list, connections=conn_list)
        except ValidationError as e:
            raise ParsingException(
                map_name=g_name, msg=e.errors()[0].get("msg", "no message")
            )
        try:
            graph = Graph(map_data)
        except GraphException as e:
            raise ParsingException(map_name=g_name, msg=str(e))
        return graph

    @staticmethod
    def _parse_nb_drones(row: str) -> int:
        """Parse the drone count declaration.

        Args:
            row (str): Source row containing the declaration.

        Returns:
            int: Number of drones declared.

        Raises:
            ParsingException: If the declaration is malformed.
        """
        tag: str
        nb_drones: str
        if len(row.split(":")) == 2:
            tag, nb_drones = row.split(":")
            if not tag.strip() == "nb_drones":
                raise ParsingException(msg="first line must be nb_drones")
            elif not nb_drones.strip().isdigit():
                raise ParsingException(msg="nbr_drones must be a "
                                       "positive integer")
        return int(nb_drones)

    @staticmethod
    def _parse_zone(row: str, nb_drones: int) -> ConnectionData | HubData:
        """Parse a hub or connection row.

        Args:
            row (str): Source row to parse.
            nb_drones (int): Map drone count used for validation.

        Returns:
            ConnectionData | HubData: Validated parsed data.

        Raises:
            ParsingException: If the row or metadata is invalid.
        """
        line: str = row.split("[")[0]
        data: ConnectionData | HubData
        tag: Tag
        meta_line: str
        metadata: MetaData | None = None
        name: str = ""
        x: int = -1
        y: int = -1

        if ":" not in line:
            raise ParsingException(msg="Missing ':' after tag")
        _tag = Tag.get(line.split(":")[0])
        if _tag is None:
            raise ParsingException(msg="Invalid tag")
        else:
            tag = _tag

        line = line.split(":")[1]
        args = line.strip().split()

        # se e' una hub trovo x e y
        if tag != Tag.CONNECTION and len(args) == 3:
            name = args[0]
            try:
                x = int(args[1])
                y = int(args[2])
            except ValueError:
                raise ParsingException(msg="Invalid non integers coordinates")
        elif tag == Tag.CONNECTION and len(args) == 1:
            name = args[0]
        else:
            raise ParsingException(
                msg=f"Invalid line format for data of type {tag.value}"
            )

        if len(row.split("[")) == 2:
            meta_line = row.split("[")[1]
            if meta_line.count("]") == 1 and meta_line.strip().endswith("]"):
                meta_line = meta_line.split("]")[0]
                try:
                    metadata = Parser._parse_metadata(meta_line,
                                                      tag,
                                                      nb_drones)
                except ParsingException as e:
                    raise e
            else:
                raise ParsingException(msg="Invalid metadata format")
        if metadata is None:
            metadata = MetaData.default_meta(tag)
        try:
            if tag != Tag.CONNECTION:
                data = HubData(tag=tag, name=name, x=x, y=y, metadata=metadata)
            else:
                data = ConnectionData(tag=tag, name=name, metadata=metadata)
        except ValidationError as e:
            raise ParsingException(msg=e.errors()[0]["msg"])
        except ParsingException as e:
            raise e
        return data

    @staticmethod
    def _parse_metadata(row: str, tag: Tag, nb_drones: int) -> MetaData:
        """Parse bracketed metadata into a validated model.

        Args:
            row (str): Metadata contents without brackets.
            tag (Tag): Tag of the enclosing map item.
            nb_drones (int): Map drone count used for validation.

        Returns:
            MetaData: Validated metadata.

        Raises:
            ParsingException: If a metadata field is invalid.
        """
        data: MetaData
        _tags: tuple[str, str, str, str] = ("color", "zone",
                                            "max_drones",
                                            "max_link_capacity")
        meta_dict: Dict[str, Tag | ZoneType | int | str | None] = {}
        metadata: List[str] = row.split()
        key: str
        value: str

        if len(metadata) == 0:
            raise ParsingException(msg="Invalid empty metadata")

        for i in range(len(metadata)):
            tmp = metadata[i].strip()
            if (
                tmp.count("=") != 1
                or tmp.startswith("=")
                or tmp.endswith("=")
                or " " in tmp
            ):
                raise ParsingException(msg="Invalid metadata")
            key, value = tmp.split("=")
            if key not in _tags or key in meta_dict:
                raise ParsingException(msg="Invalid metadata")
            if key == "zone":
                meta_dict[key] = ZoneType.get(value)
                if meta_dict[key] is None:
                    raise ParsingException(msg="Invalid zone valuein "
                                           "metadata")
            elif key == "color":
                meta_dict[key] = str(value);
                if meta_dict[key] is None:
                    raise ParsingException(msg="Invalid color value metadata")
            elif key == "max_drones" or key == "max_link_capacity":
                try:
                    int(value)
                except ValueError:
                    raise ParsingException(msg="Invalid max_drones"
                                           "in metadata")
                meta_dict[key] = int(value)
        try:
            max_d: int | None = None if meta_dict["max_drones"] is None\
                else int(str(meta_dict["max_drones"]))
        except (KeyError, ValueError):
            max_d = None
        try:
            max_l: int | None = None if meta_dict["max_link_capacity"] is None\
                else int(str(meta_dict["max_link_capacity"]))
        except (KeyError, ValueError):
            max_l = None

        try:
            data = MetaData(
                tag=tag,
                z_type=cast(ZoneType, meta_dict.get("zone")),
                color=meta_dict.get("color", "white"),
                max_drones=max_d,
                max_link_capacity=max_l,
                nb_drones=nb_drones)
        except ValidationError as e:
            raise ParsingException(msg=e.errors()[0]["msg"])
        return data
