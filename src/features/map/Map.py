from ..parser.map_data import MapDataDict
from .Connection import Connection
from .Drone import Drone
from .Hub import Hub


class Map:
    def __init__(self, data: MapDataDict) -> None:
        self.__drones_nb: int
        self.__start_hub: Hub
        self.__end_hub: Hub
        self.__hubs: list[Hub] = []
        self.__connections: list[Connection] = []

        self.__create_map(data)

    def __create_map(self, data: MapDataDict) -> None:

        if not isinstance(data["drone_nb"], int) or data["drone_nb"] <= 0:
            raise ValueError('The "drone_nb" must be an int superior as 0')

        self.__drone_nb = data["drone_nb"]

        try:
            for hub_data in data["hubs"]:
                self.__hubs.append(Hub(hub_data, self.__hubs))

        except ValueError as err:
            raise ValueError(err)

        try:
            if not data["start_hub"]:
                raise ValueError("Not start_hub provided")

            self.__start_hub = Hub(data["start_hub"], self.__hubs)

            if self.__start_hub.max_drones < self.__drone_nb:
                raise ValueError(
                    'The "max_drones" of the "start_hub"'
                    'must be at least the same as the "drone_nb"'
                )

        except ValueError as err:
            raise ValueError(err)

        try:
            if not data["end_hub"]:
                raise ValueError("Not end_hub provided")

            self.__end_hub = Hub(
                data["end_hub"], self.__hubs + [self.__start_hub]
            )

            if self.__end_hub.max_drones < 1:
                raise ValueError(
                    'The "max_drones" of the "start_hub"' "must be at least 1"
                )

        except ValueError as err:
            raise ValueError(err)

        try:
            for connection_data in data["connections"]:
                self.__connections.append(
                    Connection(
                        connection_data, self.__hubs, self.__connections
                    )
                )

        except ValueError as err:
            raise ValueError(err)

        self.__drones: list[Drone] = [
            Drone(i + 1, self.__start_hub) for i in range(self.__drone_nb)
        ]
