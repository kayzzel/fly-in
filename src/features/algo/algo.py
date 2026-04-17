from typing import TypedDict

from ...utils.types import HubType
from ..map.Connection import Connection
from ..map.Hub import Hub
from ..map.Map import Map


# Hubs -> list[(name, drone_in, max_capacity)]
class HubUsage(TypedDict):
    name: str
    drones_in: int
    max_drones: int


class ExploringDrone:
    def __init__(
            self,
            path: list[Hub | None],
            connections: list[Connection | None],
            hub: Hub
                 ):
        self.path: list[Hub | None] = path
        self.connections: list[Connection | None] = connections
        self.actual_hub: Hub = hub


class Turn:
    """
        Description:
    Store all the info of a turn for the algorithme to works well

        Attributes:
    moves -> a list of all the connection that has been parcoured this turn
    hubs -> a list of the name of all the hubs containing the drones,
            the number of drone in a hub and the max_capacity of it
    """
    def __init__(self):
        self.moves: list[Connection] = []
        self.hubs: list[HubUsage]

    def move_drone(
                self,
                drone: ExploringDrone,
                move: Connection
            ) -> ExploringDrone | None:
        """
            Description:
        Look at the turn state to see if the drone can go to a certain hub
        Move the drone to the hub if it can and return a int to signal how
        the move happend

            Parammeters:
        drone -> The drone that want to move
        move -> The connection the drone will take to move

            Return Value:
        return an ExploringDrone if it could create one else return None
        """

        actual_hub: Hub = drone.actual_hub

        # Count the number of time this connection is taken in this turn
        connection_count: int = len(
                [connection for connection in self.moves if connection == move]
            )

        # if the number of drones passing by the connection is equal or higher
        # than the max_link_capacity then return False
        if connection_count >= move.max_link_capacity:
            return None

        # Get the next hub from the connection
        next_hub: Hub = move.hub1
        if move.hub1 == actual_hub:
            next_hub = move.hub2

        # Test if the actual_hub is part of the Connection, if not return False
        elif move.hub2 != actual_hub:
            return None

        # Test if the next hub can be accessed, if not return False
        if next_hub.hub_type == HubType.BLOCKED or next_hub.max_drones == 0:
            return None

        # Get the hub_indexs from name
        hub_index: list[int] = [
                i for i in range(len(self.hubs))
                if self.hubs[i]["name"] == next_hub.name
            ]

        # if there is not hub_index for this one that mean
        # that there is no drone
        # on it so we can be sure it can be accessed
        if not hub_index:
            return ExploringDrone(
                        [*drone.path, next_hub],
                        [*drone.connections, move],
                        next_hub
                    )

        # Look if the number of drone in the hub if less than the number
        # of drones if can contain, if so return True
        index: int = hub_index[0]

        if self.hubs[index]["drones_in"] < self.hubs[index]["max_drones"]:
            return ExploringDrone(
                        [*drone.path, next_hub],
                        [*drone.connections, move],
                        next_hub
                    )

        # Return False if none of the case has append
        return None


def move_turn(
            turn: Turn,
            drones: list[ExploringDrone],
            drone: ExploringDrone
          ) -> None:
    all_moved: bool = True

    for connection in drone.actual_hub.connections:
        new_drone: ExploringDrone | None = turn.move_drone(drone, connection)

        if not new_drone:
            all_moved = False

        else:
            drones.append(new_drone)

    if all_moved:
        drones.remove(drone)


def get_best_drone(
        drones: list[ExploringDrone],
        end_hub: Hub
                   ) -> ExploringDrone:

    finished: list[ExploringDrone] = [
            drone for drone in drones if drone.actual_hub is end_hub
            ]

    if len(finished) == 1:
        return finished[0]

    nbr_of_turn: int = len(finished[0].path)

    for index in range(nbr_of_turn):
        prioritary: list[ExploringDrone] = [
            drone
            for drone in finished
            if (hub := drone.path[index]) is not None
            and hub.hub_type == HubType.PRIORITY
        ]

        if prioritary:
            if len(prioritary) == 1:
                return prioritary[0]

            finished = prioritary

    return finished[0]


def set_drone_in_turns(
        drone: ExploringDrone,
        turns: list[Turn]
                       ) -> None:

    for index in range(len(drone.connections)):
        turn: Turn = turns[index]
        hub: Hub | None = drone.path[index]
        connection: Connection | None = drone.connections[index]

        if connection:
            turn.moves.append(connection)

        if not hub:
            continue

        hub_index: list[int] = [
                i for i in range(len(turn.hubs))
                if turn.hubs[i]["name"] == hub
            ]

        if not hub_index:
            turn.hubs.append({
                "name": hub.name,
                "drones_in": 1,
                "max_drones": hub.max_drones
                    })
        else:
            turn.hubs[hub_index[0]]["drones_in"] += 1


def algo(
    routes: Map,
    turns: list[Turn]
        ) -> ExploringDrone:

    drones: list[ExploringDrone] = [
                ExploringDrone([routes.start_hub], [], routes.start_hub)
            ]

    turn_number: int = 0

    while not [
        drone for drone in drones if drone.actual_hub == routes.end_hub
    ]:
        turn: Turn

        if len(turns) > turn_number:
            turn = turns[turn_number]
        else:
            turn = Turn()
            turns.append(turn)

        for drone in drones:
            move_turn(turn, drones, drone)
            turn_number += 1

    best_drone: ExploringDrone = get_best_drone(drones, routes.end_hub)

    return best_drone
