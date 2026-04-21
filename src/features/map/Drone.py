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

    def __init__(self, drone_id: int, start_hub: Hub) -> None:
        """Initialize a drone at the start hub."""
        self.drone_id: int = drone_id
        self.path: list[Hub | None] = []
        self.in_transit_to: Hub | None = None  # for restricted 2-turn moves
        self.delivered: bool = False
        self.current_hub: Hub | None = start_hub
        self.path_step: int = 0

    @property
    def is_in_transit(self) -> bool:
        """True if the drone is mid-flight toward a restricted zone."""
        return self.in_transit_to is not None

    def assign_path(self, path: list[Hub | None]) -> None:
        """Assign a planned path (excluding the start hub)."""
        self.path = path

    def step(self) -> str | None:
        """Advance the drone by one turn.

        Returns:
            A string like 'D1-zoneName' or 'D1-hub1_hub2' if moving,
            or None if the drone stays in place.
        """
        if self.delivered or not self.path:
            return None

        if self.path[0] is None:
            self.path_step += 1
            return None

        # Second turn of a restricted zone transit: must land
        if self.is_in_transit:
            target = self.in_transit_to
            self.current_hub = target
            self.in_transit_to = None
            if target is not None and target == self.path[0]:
                self.path_step += 1
            return f"D{self.drone_id}-{target.name}" if target else None

        next_hub = self.path[0]

        # First turn of a restricted zone: enter transit
        if next_hub.hub_type.value == "restricted":
            assert self.current_hub is not None
            transit_label = f"{self.current_hub.name}_{next_hub.name}"
            self.in_transit_to = next_hub
            self.current_hub = None
            self.path_step += 1
            return f"D{self.drone_id}-{transit_label}"

        # Normal 1-turn move
        self.current_hub = next_hub
        self.path_step += 1
        return f"D{self.drone_id}-{next_hub.name}"
