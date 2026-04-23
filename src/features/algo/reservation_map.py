from typing import TypedDict

from ...utils.types import HubType
from ..map.Connection import Connection
from ..map.Hub import Hub


class ExploringDrone:
    """
        Description:
    the drones that are used in the pathfinding algorithme tha correspond
    to each of the branch of the algo, contain the info to retrace it's path

        Attributes:
    path -> a list of the hubs it has got to or
            None if for a turn it didn't moved
    connections -> a list of the connection it has used or
                   None if for a turn it didn't moved
    actual_hub -> the hub it is currently at
    in_transit_to_restricted -> if it in the middle of a restricted connection
    """
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
    """
        Description:
    the format of the dict that is used in the Turn class

        Attributes:
    name -> the name of the hub that stores the drones
    drone_in -> the number of drones that are in this hub for the turn
    max_drones -> the max number of the this hub can contain
    """
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
        """
            Description:
        return a ExploringDrone if it can go throught the given connection
        considering the state of the Turn else return None

            Parameters:
        drone -> the ExploringDrone that want to move
        move -> the connection the drone want to move throught

            Return value:
        a ExploringDrone if the given drone could move else return None
        """

        actual_hub: Hub = drone.actual_hub

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

        if move.hub1 == actual_hub:
            next_hub = move.hub2
        elif move.hub2 == actual_hub:
            next_hub = move.hub1
        else:
            return None

        if next_hub in drone.path:
            return None

        if next_hub.hub_type == HubType.BLOCKED or next_hub.max_drones == 0:
            return None

        if (next_hub.hub_type == HubType.RESTRICTED and
                not drone.in_transit_to_restricted):
            return ExploringDrone(
                [*drone.path, None],
                [*drone.connections, move],
                actual_hub,
                in_transit_to_restricted=True
            )

        hub_index: list[int] = [
            i for i in range(len(self.hubs))
            if self.hubs[i]["name"] == next_hub.name
        ]

        if not hub_index:
            return ExploringDrone(
                [*drone.path, next_hub],
                [*drone.connections, move],
                next_hub,
                in_transit_to_restricted=False
            )

        index: int = hub_index[0]
        if self.hubs[index]["drones_in"] < self.hubs[index]["max_drones"]:
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
    """
        Description:
    set a given drone in a reservation_map to put the path it used to
    in the reservation_map for the next_drones to not move where they
    can't

        Parameters:
    drone -> the drone that contain the path to set in the reservation_map
    turns -> the reservation_map that is a list of Turn
    """

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
