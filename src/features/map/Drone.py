from __future__ import annotations

from .Hub import Hub


class Drone:
    """Represents a drone navigating the zone network.

    Attributes:
        drone_id: Unique identifier.
        current_hub: The zone currently occupied, or None if in transit.
        path: Remaining planned path as a list of Hubs.
        in_transit_to: The restricted hub being traveled toward (2-turn move).
        delivered: Whether the drone has reached the end hub.
    """

    def __init__(self, drone_id: int) -> None:
        """Initialize a drone at the start hub."""
        self.drone_id: int = drone_id
        self.path: list[Hub | None] = []

    def assign_path(self, path: list[Hub | None]) -> None:
        """Assign a planned path (excluding the start hub)."""
        self.path = path

    def get_move_at_step(self, step: int) -> None | str:

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
