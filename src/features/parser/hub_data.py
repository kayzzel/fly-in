from ...utils.types import HubType, Color


class HubData:
    def __init__(
                self,
                name: str,
                x: int,
                y: int,
                hub_type: HubType = HubType.NORMAL,
                color: Color | None = None,
                max_drones: int = 1
            ) -> None:

        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.hub_type: HubType = hub_type
        self.color: Color | None = color
        self.max_drones: int = max_drones
