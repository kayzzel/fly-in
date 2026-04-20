from typing import TypedDict

from ...utils.types import HubType
from ..map.Connection import Connection
from ..map.Hub import Hub


class ExploringDrone:
    def __init__(
            self,
            path: list[Hub | None],
            connections: list[Connection | None],
            hub: Hub,
            in_transit_to_restricted: bool = False
                 ):
        self.path: list[Hub | None] = path
        self.connections: list[Connection | None] = connections
        self.actual_hub: Hub = hub
        self.in_transit_to_restricted: bool = in_transit_to_restricted


class HubUsage(TypedDict):
    name: str
    drones_in: int
    max_drones: int


class Turn:
    """
        Description:
    Store all the info of a turn for the algorithme to works well

        Attributes:
    moves -> a list of all the connection that has been parcoured this turn
    hubs -> a list of the name of all the hubs containing the drones,
            the number of drone in a hub and the max_capacity of it
    """
    def __init__(self) -> None:
        self.moves: list[Connection] = []
        self.hubs: list[HubUsage] = []

    def move_drone(
                self,
                drone: ExploringDrone,
                move: Connection
            ) -> ExploringDrone | None:

        actual_hub: Hub = drone.actual_hub

        # Check connection capacity
        connection_count: int = len([
                    c
                    for c in self.moves
                    if (
                        (c.hub1.name == move.hub1.name and
                         c.hub2.name == move.hub2.name)
                        or
                        (c.hub1.name == move.hub2.name and
                         c.hub2.name == move.hub1.name)
                    )
                ])

        if connection_count >= move.max_link_capacity:
            return None

        # Find next hub
        if move.hub1 == actual_hub:
            next_hub = move.hub2
        elif move.hub2 == actual_hub:
            next_hub = move.hub1
        else:
            return None

        # Check if blocked
        if next_hub.hub_type == HubType.BLOCKED or next_hub.max_drones == 0:
            return None

        # === NEW: If going to RESTRICTED hub, start 2-turn journey ===
        if (next_hub.hub_type == HubType.RESTRICTED and
                not drone.in_transit_to_restricted):
            # Turn 1: Start going to restricted hub
            return ExploringDrone(
                [*drone.path, None],  # None = in transit
                [*drone.connections, move],
                actual_hub,  # Stay at current hub
                in_transit_to_restricted=True  # Flag: must complete next turn
            )

        # Normal hub OR completing restricted hub entry (Turn 2)
        # Check hub capacity
        hub_index: list[int] = [
            i for i in range(len(self.hubs))
            if self.hubs[i]["name"] == next_hub.name
        ]

        if not hub_index:
            # Hub has space
            return ExploringDrone(
                [*drone.path, next_hub],
                [*drone.connections, move],
                next_hub,
                in_transit_to_restricted=False
            )

        index: int = hub_index[0]
        if self.hubs[index]["drones_in"] < self.hubs[index]["max_drones"]:
            # Hub has space
            return ExploringDrone(
                [*drone.path, next_hub],
                [*drone.connections, move],
                next_hub,
                in_transit_to_restricted=False
            )

        return None


def set_drone_in_turns(
        drone: ExploringDrone,
        turns: list[Turn]
                       ) -> None:

    for index in range(len(drone.path) - 1):
        turn: Turn = turns[index]
        hub: Hub | None = drone.path[index + 1]
        connection: Connection | None = drone.connections[index]

        if connection:
            turn.moves.append(connection)

        if not hub:
            continue

        hub_index: list[int] = [
                i for i in range(len(turn.hubs))
                if turn.hubs[i]["name"] == hub.name
            ]

        if not hub_index:
            turn.hubs.append({
                "name": hub.name,
                "drones_in": 1,
                "max_drones": hub.max_drones
                    })
        else:
            turn.hubs[hub_index[0]]["drones_in"] += 1
