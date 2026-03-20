from .hub_data import HubData
from .connection_data import ConnectionData
from ... utils.types import Color, HubType


class MapData:
    def __init__(self):
        self.drone_nb: int = 0
        self.start_hub: HubData | None = None
        self.end_hub: HubData | None = None
        self.hubs: list[HubData] = []
        self.connections: list[ConnectionData] = []

    def parsing(self, filename: str) -> bool:

        # Initialising the list that will store all the line
        lines: list[str] = []

        # Try to open the file and read all the lines in it
        try:
            with open(filename, "r") as file:
                lines = file.read().split("\n")

        # If it fails print an error an early return with False
        except OSError as err:
            print(f"Couldn't open \"{filename}\" because:")
            print(f"Error {err.__class__.__name__}: {err}")
            return False

        # Itterating over all the line of the file to pars it
        for index in range(len(lines)):
            line: str = lines[index]

            # If the line is emtpy or is a comment (start with '#')
            # just ignore it
            if line.strip() == "" or line.startswith("#"):
                continue

            elif line.startswith("start_hub: "):

                # If the start_hub is already defined then throw an error
                if self.start_hub:
                    raise ValueError(
                        f"Multiple definition of start_hub (line {index + 1})"
                    )

                self.start_hub, err = self.pars_hub(line)

                if err:
                    raise ValueError(f"{err} (line {index + 1})\n\"{line}\"")

            elif line.startswith("end_hub: "):

                # If the end_hub is already defined then throw an error
                if self.end_hub:
                    raise ValueError(
                        f"Multiple definition of end_hub (line {index + 1})"
                    )

                self.end_hub, err = self.pars_hub(line)

                if err:
                    raise ValueError(f"{err} (line {index + 1})\n\"{line}\"")

            elif line.startswith("hub: "):
                hub, err = self.pars_hub(line)

                if err:
                    raise ValueError(f"{err} (line {index + 1})\n\"{line}\"")

                self.hubs.append(hub)

            elif line.startswith("connection: "):
                connection, err = self.pars_connection(line, self.hubs)

                if err:
                    raise ValueError(f"{err} (line {index + 1})\n\"{line}\"")

                self.connections.append(connection)

            # If the line start with none of the expected format
            # then raise an error
            else:
                raise ValueError(
                        f"Invalide line format: {line} (line {index + 1})\n"
                        f"\"{line}\""
                        )

        return True

    def pars_hub(
                self, line: str
            ) -> (HubData | None, str | None):

        part: list[str] = line.split(" ", 1)

        if len(part) == 1:
            return None, "Hub has no data to descibe it"

        data: list[str] = part[1].split(" ", 3)

        if len(data) > 3:
            return None, (
                    "Not enought data to descibe the hub, "
                    "need at least: name, x, y"
                )

        name, x, y = data

        if " " in name or "-" in name:
            return None, (
                    "Invalide char in hub name, "
                    f"can't have ' ' or '-' in it (name: {name})"
                )

        if not x.isdigit():
            return None, (
                    "Invalide format for x, must be a positive int "
                    f"(x: {x})"
                )

        if not y.isdigit():
            return None, (
                    "Invalide format for x, must be a positive int "
                    f"(x: {x})"
                )

        if len(data) == 3:
            return HubData(name, int(x), int(y))

        metadata_array: str = data[3]

        if metadata_array[0] != "[" or metadata_array[-1] != "]":
            return None, (
                    "Metadatas must be inside brackets -> [...] "
                    f"(metadata: {metadata_array})"
                )

        metadatas: list[str] = metadata_array[1:-2].split(" ")

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
                        f"The key \"{key}\" is already defined for this hub "
                        f"(metadatas: {metadatas})"
                        )

            if key == "zone":
                if value not in HubType:
                    return None, (
                            "The zone type is not in the defined one ->"
                            "normal, blocked, priority, restricted "
                            f"(zone type: {value})"
                            )

                zone = value
                seted_key.append(key)

            elif key == "color":
                if value not in Color:
                    return None, (
                            "The color is not in the defined one ->"
                            f"(color: {value})"
                            )

                color = value
                seted_key.append(key)

            elif key == "max_drones":
                if not value.isdigit():
                    return None, (
                            "The number of drones must be a positive int"
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
                self, line: str, hubs: list[HubData]
            ) -> (ConnectionData | None, str | None):
        pass


if __name__ == "__main__":
    map_data: MapData = MapData()

    map_data.parsing("maps/easy/01_linear_path.txt")
