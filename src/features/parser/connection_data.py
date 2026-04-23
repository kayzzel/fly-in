class ConnectionData:
    """
        Desciption:
    contain all the parsed data do create a Connection

        Attributes:
    hub1 -> the name of the first hub of the connection
    hub2 -> the name of the second hub of the connection
    max_link_capacity -> the max number of drones that can go
                         throught the connection at the same time
    """
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
