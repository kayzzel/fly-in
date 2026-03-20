from ...utils.types import Color, HubType
from .connection_data import ConnectionData
from .hub_data import HubData


class MapData:
    def __init__(self) -> None:
        self.__drones_nb: int = 0
        self.__start_hub: HubData | None = None
        self.__end_hub: HubData | None = None
        self.__hubs: list[HubData] = []
        self.__connections: list[ConnectionData] = []

    def parsing(self, filename: str) -> None:

        # reseting the map data
        self.__drones_nb = 0
        self.__start_hub = None
        self.__end_hub = None
        self.__hubs = []
        self.__connections = []

        # Initialising the list that will store all the line
        lines: list[str] = []

        # Try to open the file and read all the lines in it
        try:
            with open(filename, "r") as file:
                lines = file.read().split("\n")

        # If it fails raise an error an early return with False
        except OSError as err:
            raise OSError(
                f'Couldn\'t open "{filename}" because:\n'
                f"Error {err.__class__.__name__}: {err}"
            )

        i: int = 0

        # Skip all the comments and empty lines at the start of the file
        while lines[i].startswith("#") or lines[i].strip() == "":
            i += 1

        # Look if the first line is the drones number
        if not lines[i].startswith("nb_drones: "):
            raise ValueError(
                "The file must start with the nb of drones "
                f"(line {i + 1})\n"
                f'"{lines[i]}"'
            )

        # Look if the value of drone number is a positive int
        if not lines[i][11::].isdigit():
            raise ValueError(
                "The number of drones must be a positive int "
                f"(line {i + 1})\n"
                f'"{lines[i]}"'
            )

        self.__drones_nb = int(lines[i][11::])

        i += 1

        # Itterating over all the line of the file to pars it
        for index in range(i, len(lines)):
            line: str = lines[index]

            # If the line is emtpy or is a comment (start with '#')
            # just ignore it
            if line.strip() == "" or line.startswith("#"):
                continue

            elif line.startswith("start_hub: "):

                # If the start_hub is already defined then throw an error
                if self.__start_hub:
                    raise ValueError(
                        f"Multiple definition of start_hub (line {index + 1})"
                    )

                self.__start_hub, error = self.pars_hub(line)

                if error:
                    raise ValueError(f'{error} (line {index + 1})\n"{line}"')

            elif line.startswith("end_hub: "):

                # If the end_hub is already defined then throw an error
                if self.__end_hub:
                    raise ValueError(
                        f"Multiple definition of end_hub (line {index + 1})"
                    )

                self.__end_hub, error = self.pars_hub(line)

                if error:
                    raise ValueError(f'{error} (line {index + 1})\n"{line}"')

            elif line.startswith("hub: "):
                hub, error = self.pars_hub(line)

                if error or not hub:
                    raise ValueError(f'{error} (line {index + 1})\n"{line}"')

                self.__hubs.append(hub)

            elif line.startswith("connection: "):
                connection, error = self.pars_connection(line)

                if error or not connection:
                    raise ValueError(f'{error} (line {index + 1})\n"{line}"')

                self.__connections.append(connection)

            # If the line start with none of the expected format
            # then raise an error
            else:
                raise ValueError(
                    f"Invalide line format: {line} (line {index + 1})\n"
                    f'"{line}"'
                )

        if not self.__start_hub:
            raise ValueError("No start_hub found in the file")

        if not self.__end_hub:
            raise ValueError("No end_hub found in the file")

        if not self.__connections:
            raise ValueError("No connections found in the file")

    def pars_hub(self, line: str) -> tuple[HubData | None, str | None]:

        part: list[str] = line.split(" ", 1)

        if len(part) == 1:
            return None, "Hub has no data to descibe it"

        data: list[str] = part[1].split(" ", 3)

        if len(data) < 3:
            return None, (
                "Not enought data to descibe the hub, "
                "need at least: name, x, y"
            )

        name: str = data[0]
        x: str = data[1]
        y: str = data[2]

        if " " in name or "-" in name:
            return None, (
                "Invalide char in hub name, "
                f"can't have ' ' or '-' in it (name: {name})"
            )

        if not (x[0] == "-" and x[1::].isdigit()) and not x.isdigit():
            return None, (
                "Invalide format for x, must be an integer " f"(x: {x})"
            )

        if not (y[0] == "-" and y[1::].isdigit()) and not y.isdigit():
            return None, (
                "Invalide format for y, must be an integer " f"(y: {y})"
            )

        if len(data) == 3:
            return HubData(name, int(x), int(y)), None

        metadata_array: str = data[3]

        if metadata_array[0] != "[" or metadata_array[-1] != "]":
            return None, (
                "Metadatas must be inside brackets -> [...] "
                f"(metadata: {metadata_array})"
            )

        metadatas: list[str] = metadata_array[1:-1].split(" ")

        zone: HubType = HubType.NORMAL
        color: Color | None = None
        max_drones: int = 1

        seted_key: list[str] = []

        for metadata in metadatas:
            data_split = metadata.split("=", 1)

            if len(data_split) != 2:
                return None, (
                    "Wrong format for metadata, need <key>=<value> "
                    f"(metadata: {metadata})"
                )

            key, value = data_split

            if key in seted_key:
                return None, (
                    f'The key "{key}" is already defined for this hub '
                    f"(metadatas: {metadatas})"
                )

            if key == "zone":
                if value not in HubType._value2member_map_:
                    return None, (
                        "The zone type is not in the defined one -> "
                        "normal, blocked, priority, restricted "
                        f"(zone type: {value})"
                    )

                zone = HubType(value)
                seted_key.append(key)

            elif key == "color":
                if value not in Color._value2member_map_:
                    return None, (
                        "The color is not in the defined one "
                        f"(color: {value})"
                    )

                color = Color(value)
                seted_key.append(key)

            elif key == "max_drones":
                if not value.isdigit():
                    return None, (
                        "The number of drones must be a positive int "
                        f"(max drones: {value})"
                    )

                max_drones = int(value)
                seted_key.append(key)
            else:
                return None, (
                    "the key is not in the authorised keys -> "
                    f"zone, color, max_drones (metadata: {metadata})"
                )
        return HubData(name, int(x), int(y), zone, color, max_drones), None

    def pars_connection(
        self, line: str
    ) -> tuple[ConnectionData | None, str | None]:

        part: list[str] = line.split(" ", 1)

        if len(part) <= 1:
            return None, "Connection has no data to descibe it"

        data: list[str] = part[1].split(" ", 1)

        connected_hub: list[str] = data[0].split("-")

        if len(connected_hub) > 2:
            return None, (
                "To many hubs to connect, only 2 needed "
                f"(connection: {data[0]})"
            )

        if len(connected_hub) < 2:
            return None, (
                "Less hubs thas needed to connect, 2 hubs needed "
                f"(connection: {data[0]})"
            )

        if connected_hub[0] == connected_hub[1]:
            return None, (
                "Can't connnect a hub with himself " f"(connection: {data[0]})"
            )

        if len(data) == 1:
            return ConnectionData(connected_hub[0], connected_hub[1]), None

        metadata: str = data[1]

        if metadata[0] != "[" or metadata[-1] != "]":
            return None, (
                "Metadatas must be inside brackets -> [...] "
                f"(metadata: {metadata})"
            )

        data_split = metadata[1:-1].split("=", 1)

        if len(data_split) != 2:
            return None, (
                "Wrong format for metadata, need <key>=<value> "
                f"(metadata: {metadata})"
            )

        key, value = data_split

        if key != "max_link_capacity":
            if not value.isdigit():
                return None, (
                    "the key is not in the authorised keys -> "
                    f"max_link_capacity (metadata: {metadata})"
                )

        if not value.isdigit():
            return None, (
                "The number of drones must be a positive int "
                f"(max drones: {value})"
            )

        return (
            ConnectionData(connected_hub[0], connected_hub[1], int(value)),
            None,
        )

    def __str__(self) -> str:
        value: str = ""
        value += f"drones_nb: {self.__drones_nb}\n"
        value += f"start_hub: {self.__start_hub}\n"
        value += f"end_hub: {self.__end_hub}\n"
        value += "HUBS:\n"
        if not self.__hubs:
            value += "\tNone\n"
        else:
            for hub in self.__hubs:
                value += f"\t{hub}\n"
        value += "CONNECTIONS:\n"
        if not self.__connections:
            value += "\tNone\n"
        else:
            for connection in self.__connections:
                value += f"\t{connection}\n"

        return value
