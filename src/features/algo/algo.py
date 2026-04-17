from ...utils.types import HubType
from ..map.Map import Map
from ..map.Hub import Hub
from .reservation_map import Turn, ExploringDrone, set_drone_in_turns


def move_turn(
            turn: Turn,
            drones: list[ExploringDrone],
            drone: ExploringDrone
          ) -> None:
    all_moved: bool = True

    for connection in drone.actual_hub.connections:
        new_drone: ExploringDrone | None = turn.move_drone(drone, connection)

        if not new_drone:
            all_moved = False

        else:
            drones.append(new_drone)

    if all_moved:
        drones.remove(drone)


def get_best_drone(
        drones: list[ExploringDrone],
        end_hub: Hub
                   ) -> ExploringDrone:

    finished: list[ExploringDrone] = [
            drone for drone in drones if drone.actual_hub is end_hub
            ]

    if len(finished) == 1:
        return finished[0]

    nbr_of_turn: int = len(finished[0].path)

    for index in range(nbr_of_turn):
        prioritary: list[ExploringDrone] = [
            drone
            for drone in finished
            if (hub := drone.path[index]) is not None
            and hub.hub_type == HubType.PRIORITY
        ]

        if prioritary:
            if len(prioritary) == 1:
                return prioritary[0]

            finished = prioritary

    return finished[0]


def algo(
    routes: Map,
    turns: list[Turn]
        ) -> ExploringDrone:

    drones: list[ExploringDrone] = [
                ExploringDrone([routes.start_hub], [], routes.start_hub)
            ]

    turn_number: int = 0

    while not [
        drone for drone in drones if drone.actual_hub == routes.end_hub
    ]:
        turn: Turn

        if len(turns) > turn_number:
            turn = turns[turn_number]
        else:
            turn = Turn()
            turns.append(turn)

        for drone in drones:
            move_turn(turn, drones, drone)
            turn_number += 1

    best_drone: ExploringDrone = get_best_drone(drones, routes.end_hub)
    set_drone_in_turns(best_drone, turns)

    return best_drone
