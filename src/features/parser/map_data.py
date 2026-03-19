from .hub_data import HubData
from .connection_data import ConnectionData


class MapData:
    def __init__(self):
        self.drone_nb: int = 0
        self.start_hub: HubData | None = None
        self.end_hub: HubData | None = None
        self.hubs: list[HubData] = []
        self.connections: list[ConnectionData] = []

    def parsing(self, filename: str) -> bool:

        lines: list[str] = []

        try:
            with open(filename, "r") as file:
                lines = file.read().split("\n")

        except OSError as err:
            print(f"Couldn't open \"{filename}\" because:")
            print(f"Error {err.__class__.__name__}: {err}")
            return False

        return True

    def pars_hub(
                self, line: str, line_nbr: int
            ) -> HubData | None:
        pass

    def pars_connection(
                self, line: str, line_nbr: int
            ) -> ConnectionData | None:

        pass
