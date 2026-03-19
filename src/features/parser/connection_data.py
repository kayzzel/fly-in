from .hub_data import HubData


class ConnectionData:
    def __init__(
                self,
                hub1: HubData,
                hub2: HubData,
                max_link_capacity: int = 1,
            ):

        self.hub1: HubData = hub1
        self.hub2: HubData = hub2
        self.max_link_capacity: int = max_link_capacity
