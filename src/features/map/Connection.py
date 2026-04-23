from __future__ import annotations

from ..parser.connection_data import ConnectionData
from .Hub import Hub


class Connection:
    """
        Description:
    Represents a physical link between two hubs in the map. It manages the
    relationship between connected nodes and enforces traffic constraints
    by defining the maximum number of drones that can traverse the link
    simultaneously.

        Attributes:
    hub1 -> The first Hub object associated with this connection.
    hub2 -> The second Hub object associated with this connection.
    max_link_capacity -> The maximum number of drones allowed on
                         this link per turn.
    """
    def __init__(
        self,
        data: ConnectionData,
        hubs: list[Hub],
        connections: list[Connection],
    ) -> None:
        self.hub1: Hub
        self.hub2: Hub
        self.max_link_capacity: int

        self.__create_connection(data, hubs, connections)

    def __create_connection(
        self,
        data: ConnectionData,
        hubs: list[Hub],
        connections: list[Connection],
    ) -> None:
        """
            Description:
        Validates the connection parameters, ensuring that the hubs exist,
        are not identical, and are not already connected. Upon validation,
        it establishes the bidirectional link by updating the connection
        lists of both participating hubs.

            Parameters:
        data -> The raw connection data to be validated and processed.
        hubs -> The list of hubs used to resolve name references to objects.
        connections -> The current connections used to prevent duplicate paths.

            Return value:
        None
        """

        if data.hub1 == data.hub2:
            raise ValueError(
                "Can't connnect a hub with himself "
                f"(connection: {data.hub1}-{data.hub2})"
            )

        hub1: list[Hub] = [hub for hub in hubs if hub.name == data.hub1]
        hub2: list[Hub] = [hub for hub in hubs if hub.name == data.hub2]

        if len(hub1) != 1:
            raise ValueError(
                f'"{data.hub1}" is not defined as a hub in the map'
            )

        if len(hub2) != 1:
            raise ValueError(
                f'"{data.hub2}" is not defined as a hub in the map'
            )

        if (
            len(
                [
                    c
                    for c in connections
                    if (
                        (c.hub1.name == data.hub1 and
                         c.hub2.name == data.hub2)
                        or
                        (c.hub1.name == data.hub2 and
                         c.hub2.name == data.hub1)
                    )
                ]
            )
            != 0
        ):
            raise ValueError(
                f"The connection between {data.hub1} and {data.hub2} "
                "is already defined"
            )

        if (
            not isinstance(data.max_link_capacity, int)
            or data.max_link_capacity < 0
        ):
            raise ValueError(
                "The number of drones must be a positive int "
                f"(max drones: {data.max_link_capacity})"
            )
        self.hub1 = hub1[0]
        self.hub2 = hub2[0]
        self.max_link_capacity = data.max_link_capacity

        self.hub1.connections.append(self)
        self.hub2.connections.append(self)
