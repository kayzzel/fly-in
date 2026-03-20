from enum import Enum


class Color(str, Enum):
    RED = "red"


class HubType(str, Enum):
    """
        Description:
    define the diferent types of hub there is in the project

        Values:
    NORMAL -> Standard hub (cost -> 1)
    BLOCKED -> Can access this hub
    PRIORITY -> prefered hub, same cost as NORMAL
    RESTRICTED -> dangerous hub (cost -> 2)
    """
    NORMAL = "normal"
    BLOCKED = "blocked"
    PRIORITY = "priority"
    RESTRICTED = "restricted"
