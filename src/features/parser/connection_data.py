class ConnectionData:
    def __init__(
        self,
        hub1: str,
        hub2: str,
        max_link_capacity: int = 1,
    ) -> None:

        self.hub1: str = hub1
        self.hub2: str = hub2
        self.max_link_capacity: int = max_link_capacity

    def __str__(self) -> str:
        return f"{self.hub1} -> {self.hub2} [{self.max_link_capacity}]"
