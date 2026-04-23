from ..parser.map_data import MapDataDict
from .Connection import Connection
from .Drone import Drone
from .Hub import Hub
from collections import deque


class Map:
    """
        Description:
    The core data structure representing the drone simulation environment.
    It manages the lifecycle of hubs, connections, and drones, and provides
    the interface for running algorithms and validating map connectivity.

        Attributes:
    drones_nb -> Total number of drones to be managed.
    start_hub -> The entry point for all drones.
    end_hub -> The target destination for all drones.
    hubs -> List of intermediate zones (normal, priority, restricted, blocked).
    connections -> List of paths linking the various hubs.
    max_steps -> The duration of the longest drone path in the simulation.
    """
    def __init__(self, data: MapDataDict) -> None:
        self.map_name: str = data["map_name"]
        self.drones_nb: int
        self.start_hub: Hub
        self.end_hub: Hub
        self.hubs: list[Hub] = []
        self.connections: list[Connection] = []
        self.max_steps: int = 0

        self.__create_map(data)

    def __create_map(self, data: MapDataDict) -> None:
        """
            Description:
        Internal method that populates the Map attributes
        (hubs, connections, drones) from the data dictionary
        and performs initial validation on drone capacity.

            Parameters:
        data -> The dictionary containing raw map data to be processed.
        """

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

            if self.end_hub.max_drones < self.drones_nb:
                raise ValueError(
                    'The "max_drones" of the "end_hub"'
                    'must be at least the same as the "drones_nb"'
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

        if not self.is_map_solvable():
            raise ValueError("Error: This map cannot be finished!")

        self.drones: list[Drone] = [
            Drone(i + 1) for i in range(self.drones_nb)
        ]

    def is_map_solvable(self) -> bool:
        """
            Description:
        Uses a Breadth-First Search (BFS) algorithm to determine if a physical
        path exists from the start_hub to the end_hub, respecting 'blocked'
        zones and minimum capacities.

            Return value:
        A bool indicating True if the end_hub is reachable, False otherwise.
        """
        start = self.start_hub
        target = self.end_hub

        if (
            start.hub_type.value == "blocked" or
            target.hub_type.value == "blocked"
                ):
            return False

        queue = deque([start])

        visited = {start.name}

        while queue:
            current_hub = queue.popleft()

            if current_hub.name == target.name:
                return True

            for conn in self.connections:

                if conn.max_link_capacity < 1:
                    continue
                neighbor = None
                if conn.hub1.name == current_hub.name:
                    neighbor = conn.hub2
                elif conn.hub2.name == current_hub.name:
                    neighbor = conn.hub1

                if neighbor and neighbor.name not in visited:
                    if (
                            neighbor.hub_type.value != "blocked" and
                            neighbor.max_drones > 0
                            ):
                        visited.add(neighbor.name)
                        queue.append(neighbor)

        return False

    def set_drones_steps(self, paths: list[list[Hub | None]]) -> None:
        """
            Description:
        Assigns calculated paths to each drone in the map and updates the
        global max_steps count for the simulation.

            Parameters:
        paths -> A list of lists where each sub-list contains the sequence
                 of Hubs (or None for wait states) for a drone.
        """
        self.max_steps = 0
        for index in range(len(paths)):
            self.drones[index].assign_path(paths[index])
            if self.max_steps < len(paths[index]):
                self.max_steps = len(paths[index])

        self.print_algo()

    def print_algo(self) -> None:
        """
            Description:
        Iterates through the simulation steps and prints the drone movements
        to the terminal in the required format (P<id>-<hub_name>)
        """
        print("----", self.map_name, "----\n")
        for i in range(1, self.max_steps):
            first: bool = True
            for drone in self.drones:
                move: str | None = drone.get_move_at_step(i)
                if not move:
                    continue

                if first:
                    first = False
                    print(move, end="")

                else:
                    print(" " + move, end="")

            print()
        print()
