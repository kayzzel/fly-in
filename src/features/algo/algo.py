from ...utils.types import HubType
from ..map.Connection import Connection
from ..map.Hub import Hub
from ..map.Map import Map


# Hubs -> list[(name, drone_in, max_capacity)]
Hubs = list[tuple[str, int, int]]


class ExploringDrone:
    def __init__(self, path: list[Hub], hub: Hub):
        self.path: list[Hub] = path
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
    def __init__(self, hubs: Hubs):
        self.moves: list[Connection] = []
        self.hubs: Hubs

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
                if self.hubs[i][0] == next_hub.name
            ]

        # if there is not hub_index for this one that mean
        # that there is no drone
        # on it so we can be sure it can be accessed
        if not hub_index:
            return ExploringDrone([drone.path[:], next_hub], next_hub)

        # Look if the number of drone in the hub if less than the number
        # of drones if can contain, if so return True
        index: int = hub_index[0]

        if self.hub[index][1] < hub_index[index][2]:
            return ExploringDrone([drone.path[:], next_hub], next_hub)

        # Return False if none of the case has append
        return None


def move_turn(
        routes: Map,
        drones: list[ExploringDrone],
        drone: ExploringDrone
              ):
    all_moved: bool = True

    for connection in 

    if all_moved:
        drones.remove(drone)


def algo(routes: Map):

    drones: list[ExploringDrone] = [ExploringDrone(routes.start_hub)]

    while not [
        drone for drone in drones if drone.actual_hub == routes.end_hub
    ]:
