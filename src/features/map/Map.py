from ..parser.map_data import MapDataDict
from .Connection import Connection
from .Drone import Drone
from .Hub import Hub
from collections import deque


class Map:
    def __init__(self, data: MapDataDict) -> None:
        self.drones_nb: int
        self.start_hub: Hub
        self.end_hub: Hub
        self.hubs: list[Hub] = []
        self.connections: list[Connection] = []
        self.max_steps: int = 0

        self.__create_map(data)

    def __create_map(self, data: MapDataDict) -> None:

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

        if not Map.is_map_solvable(self):
            raise ValueError("Error: This map cannot be finished!")

        self.drones: list[Drone] = [
            Drone(i + 1, self.start_hub) for i in range(self.drones_nb)
        ]

    def is_map_solvable(self) -> bool:
        """
        Checks if a physical path exists between start_hub and end_hub.
        Ignores capacity and turn limits; only respects 'blocked' status.
        """
        start = self.start_hub
        target = self.end_hub

        # If either start or end is blocked, it's impossible
        if (
            start.hub_type.value == "blocked" or
            target.hub_type.value == "blocked"
                ):
            return False

        # Queue for BFS: stores the hub we are currently looking at
        queue = deque([start])

        # Keep track of visited hubs to avoid infinite loops
        visited = {start.name}

        while queue:
            current_hub = queue.popleft()

            # If we reached the target, the map is possible!
            if current_hub.name == target.name:
                return True

            # Check all connections for the current hub
            for conn in self.connections:

                if conn.max_link_capacity < 1:
                    continue
                # Find the "other" hub in the connection
                neighbor = None
                if conn.hub1.name == current_hub.name:
                    neighbor = conn.hub2
                elif conn.hub2.name == current_hub.name:
                    neighbor = conn.hub1

                # If we found neighbor we haven't visited and it's not blocked
                if neighbor and neighbor.name not in visited:
                    if (
                            neighbor.hub_type.value != "blocked" and
                            neighbor.max_drones > 0
                            ):
                        visited.add(neighbor.name)
                        queue.append(neighbor)

        # If the queue is empty and we never hit the target
        return False

    def set_drones_steps(self, paths: list[list[Hub | None]]) -> None:
        self.max_steps = 0
        for index in range(len(paths)):
            self.drones[index].assign_path(paths[index])
            if self.max_steps < len(paths[index]):
                self.max_steps = len(paths[index])

    def print_algo(self) -> None:
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
