from __future__ import annotations
from .Hub import Hub
from ..parser.connection_data import ConnectionData


class Connection:
    def __init__(
            self,
            data: ConnectionData,
            hubs: list[Hub],
            connections: list[Connection]
                ) -> None:
        self.hub1: Hub
        self.hub2: Hub
        self.max_link_capacity: int

    def __create_connection(
                    self,
                    data: ConnectionData,
                    hubs: list[Hub],
                    connections: list[Connection]
                ) -> None:

        if data.hub1 == data.hub2:
            raise ValueError(
                "Can't connnect a hub with himself "
                f"(connection: {data.hub1}-{data.hub2})"
            )

        hub1: list[Hub] = [hub for hub in hubs if hub.name == data.hub1]
        hub2: list[Hub] = [hub for hub in hubs if hub.name == data.hub2]

        if len(hub1) != 1:
            raise ValueError(
                    "\"{data.hub1}\" is not defined as a hub in the map"
                    )

        if len(hub2) != 1:
            raise ValueError(
                    "\"{data.hub2}\" is not defined as a hub in the map"
                    )

        if len([
                c for c in connections
                if c.hub1 == data.hub1 and c.hub2 == data.hub2
                ]) != 0:
            raise ValueError(
                    f"The connection between {data.hub1} and {data.hub2} "
                    "is already defined"
                    )

        if (not isinstance(data.max_link_capacity, int) or
                data.max_link_capacity < 0):
            raise ValueError(
                    "The number of drones must be a positive int "
                    f"(max drones: {data.max_link_capacity})"
                )
