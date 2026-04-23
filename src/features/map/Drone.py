from __future__ import annotations

from .Hub import Hub


class Drone:
    """
        Description:
    Represents a drone navigating the zone network. It tracks its unique
    identity and the sequence of hubs it must visit to complete its mission,
    including handling complex movement logic for special zone types.

        Attributes:
    drone_id -> Unique integer identifier for the drone.
    path -> A list of Hub objects or None values (representing wait/transit)
            defining the drone's trajectory through the map.
    """

    def __init__(self, drone_id: int) -> None:
        self.drone_id: int = drone_id
        self.path: list[Hub | None] = []

    def assign_path(self, path: list[Hub | None]) -> None:
        """
            Description:
        Sets the planned flight path for the drone, which will be used to
        calculate movements during the simulation steps.

            Parameters:
        path -> A list containing the Hubs (or None) the drone will occupy
                at each step.

            Return value:
        None
        """
        self.path = path

    def get_move_at_step(self, step: int) -> None | str:
        """
            Description:
        Calculates the specific movement string for the drone at a given
        simulation turn. It handles standard moves to hubs and special
        2-turn transit moves required for entering restricted hubs.

            Parameters:
        step -> The current turn index in the simulation.

            Return value:
        A str formatted as "D<id>-<hub>" or "D<id>-<from>-<to>" for restricted
        entries, or None if the drone is stationary or has no move.
        """

        if step >= len(self.path):
            return None

        hub = self.path[step]

        next_hub = None

        if step + 1 < len(self.path):
            next_hub = self.path[step + 1]

        if (
                hub is None and next_hub and
                next_hub is not None and
                next_hub.hub_type.value == "restricted"
                ):
            last_hub: list[Hub] = [
                    hub for hub in self.path[:step] if hub is not None
                ]
            return f"D{self.drone_id}-{last_hub[-1].name}-{next_hub.name}"
        elif not hub:
            return None

        return f"D{self.drone_id}-{hub.name}"
