from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Connection import Connection

from ...utils.types import Color, HubType
from ..parser.hub_data import HubData


class Hub:
    def __init__(self, data: HubData, hubs: list[Hub]) -> None:
        self.name: str
        self.x: int
        self.y: int
        self.hub_type: HubType
        self.color: Color | None
        self.max_drones: int
        self.connections: list["Connection"] = []

        self.__create_hub(data, hubs)

    def __create_hub(self, data: HubData, hubs: list[Hub]) -> None:

        hubs_names: list[str] = [hub.name for hub in hubs]

        if data.name in hubs_names:
            raise ValueError(
                f'Hub "{data.name}" is already defined in the Hub list'
            )

        if data.hub_type not in HubType._value2member_map_:
            raise ValueError(
                "The zone type is not in the defined one -> "
                "normal, blocked, priority, restricted "
                f"(zone type: {data.hub_type})"
            )

        if data.color not in Color._value2member_map_ and data.color:
            raise ValueError(
                "The color is not in the defined one " f"(color: {data.color})"
            )

        if not isinstance(data.max_drones, int) or data.max_drones < 0:
            raise ValueError(
                "The number of drones must be a positive int "
                f"(max drones: {data.max_drones})"
            )

        self.name = data.name
        self.x = data.x
        self.y = data.y
        self.hub_type = data.hub_type
        self.color = data.color
        self.max_drones = data.max_drones
