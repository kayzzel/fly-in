from ...utils.types import Color, HubType


class HubData:
    """
        Desciption:
    contain all the parsed data do create a Hub

        Attributes:
    name -> the name of the hub
    x -> the x coordinate of the hub
    y -> the y coordinate of the hub
    hub_type -> the type of hub it is
    color -> the color of the hub for the visualizer
    max_drones -> the max number of drones that can be
                  on this hub at the same time
    """
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        hub_type: HubType = HubType.NORMAL,
        color: Color | None = None,
        max_drones: int = 1,
    ) -> None:

        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.hub_type: HubType = hub_type
        self.color: Color | None = color
        self.max_drones: int = max_drones

    def __str__(self) -> str:
        return (
            f"{self.name}, ({self.x}, {self.y}) [{self.hub_type}, "
            f"{self.color}, {self.max_drones}]"
        )
