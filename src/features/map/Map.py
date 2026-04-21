from ..parser.map_data import MapDataDict
from .Connection import Connection
from .Drone import Drone
from .Hub import Hub


class Map:
    def __init__(self, data: MapDataDict) -> None:
        self.drones_nb: int
        self.start_hub: Hub
        self.end_hub: Hub
        self.hubs: list[Hub] = []
        self.connections: list[Connection] = []
        self.max_steps: int = 0

        self.__create_map(data)

    def __create_map(self, data: MapDataDict) -> None:

        if not isinstance(data["drones_nb"], int) or data["drones_nb"] <= 0:
            raise ValueError('The "drones_nb" must be an int superior as 0')

        self.drones_nb = data["drones_nb"]

        try:
            for hub_data in data["hubs"]:
                self.hubs.append(Hub(hub_data, self.hubs))

        except ValueError as err:
            raise ValueError(err)

        try:
            if not data["start_hub"]:
                raise ValueError("Not start_hub provided")

            self.start_hub = Hub(data["start_hub"], self.hubs)

            if self.start_hub.max_drones < self.drones_nb:
                raise ValueError(
                    'The "max_drones" of the "start_hub"'
                    'must be at least the same as the "drones_nb"'
                )

        except ValueError as err:
            raise ValueError(err)

        try:
            if not data["end_hub"]:
                raise ValueError("Not end_hub provided")

            self.end_hub = Hub(
                data["end_hub"], self.hubs + [self.start_hub]
            )

            if self.end_hub.max_drones < 1:
                raise ValueError(
                    'The "max_drones" of the "start_hub"' "must be at least 1"
                )

        except ValueError as err:
            raise ValueError(err)

        try:
            for connection_data in data["connections"]:
                self.connections.append(
                    Connection(
                        connection_data,
                        [*self.hubs, self.start_hub, self.end_hub],
                        self.connections
                    )
                )

        except ValueError as err:
            raise ValueError(err)

        self.drones: list[Drone] = [
            Drone(i + 1, self.start_hub) for i in range(self.drones_nb)
        ]

    def set_drones_steps(self, paths: list[list[Hub | None]]) -> None:
        self.max_steps = 0
        for index in range(len(paths)):
            self.drones[index].assign_path(paths[index])
            if self.max_steps < len(paths[index]):
                self.max_steps = len(paths[index])
