from ...utils.types import HubType
from ..map.Connection import Connection
from ..map.Hub import Hub


# Hubs -> list[(name, drone_in, max_capacity)]
Hubs = list[tuple[str, int, int]]


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

    def can_drone_move(self, actual_hub: Hub, move: Connection) -> bool:
        """
            Description:
        Look at the turn state to see if the drone can go to a certain hub
        return True if it can else return Flase

            Parammeters:
        actual_hub -> The hub the drone is currently on
        move -> The connection the drone will take to move

            Return Value:
        return a Bool, True if the drone can go to the hub next turn and false
        if the drone can't
        """

        # Count the number of time this connection is taken in this turn
        connection_count: int = len(
                [connection for connection in self.moves if connection == move]
            )

        # if the number of drones passing by the connection is equal or higher
        # than the max_link_capacity then return False
        if connection_count >= move.max_link_capacity:
            return False

        # Get the next hub from the connection
        next_hub: Hub = move.hub1
        if move.hub1 == actual_hub:
            next_hub = move.hub2

        # Test if the actual_hub is part of the Connection, if not return False
        elif move.hub2 != actual_hub:
            return False

        # Test if the next hub can be accessed, if not return False
        if next_hub.hub_type == HubType.RESTRICTED or next_hub.max_drones == 0:
            return False

        # Get the hub_infos from name
        hub_info = [hub for hub in self.hubs if hub[0] == next_hub.name]

        # if ther is not hub_info for this one that mean that there is no drone
        # on it so we can be sure it can be accessed
        if not hub_info:
            return True

        # Look if the number of drone in the hub if less than the number
        # of drones if can contain, if so return True
        if hub_info[0][1] < hub_info[0][2]:
            return True

        # Return False if none of the case has append
        return False
