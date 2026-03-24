from ..parser.map_data import MapDataDict
from .Hub import Hub
from .Connection import Connection


class Map:
    def __init__(self, data: MapDataDict) -> None:
        self.__drones_nb: int = 0
        self.__start_hub: Hub | None = None
        self.__end_hub: Hub | None = None
        self.__hubs: list[Hub] = []
        self.__connections: list[Connection] = []

        self.__create_map(data)

    def __create_map(self, data: MapDataDict) -> None:

        try:
            for hub_data in data["hubs"]:
                self.__hubs.append(Hub(hub_data, self.__hubs))

        except ValueError as err:
            raise ValueError(err)
