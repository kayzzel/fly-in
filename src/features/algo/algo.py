from ...utils.types import HubType
from ..map.Map import Map
from ..map.Hub import Hub
from .reservation_map import Turn, ExploringDrone, set_drone_in_turns


def get_best_drone(
        drones: list[ExploringDrone],
        end_hub: Hub
                   ) -> ExploringDrone:

    finished: list[ExploringDrone] = [
            drone for drone in drones if drone.actual_hub is end_hub
            ]

    if not finished:  # Should never happen, but just in case
        raise ValueError("No drones reached the end hub")

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


def move_turn(
            turn: Turn,
            drones: list[ExploringDrone],
            drone: ExploringDrone
          ) -> None:
    # If drone is in transit to restricted hub, it MUST arrive this turn
    if drone.in_transit_to_restricted:
        # Get the last connection (the one leading to restricted hub)
        last_connection = drone.connections[-1]
        if not last_connection:
            return  # Invalid state, drone is lost

        # Try to enter the restricted hub
        new_drone = turn.move_drone(drone, last_connection)

        if new_drone:
            new_drone.connections[-1] = None  # depend on the max_link view
            drones.append(new_drone)
        # If move fails, drone is removed (path fails)
        return

    # Normal movement - try all connections
    all_moved = True
    for connection in drone.actual_hub.connections:
        new_drone = turn.move_drone(drone, connection)
        if new_drone:
            drones.append(new_drone)
        else:
            all_moved = False

    # If no moves were possible, keep the drone (stuck, but might move later)
    if not all_moved:
        drones.append(ExploringDrone(
            [*drone.path, None],
            [*drone.connections, None],
            drone.actual_hub,
            drone.in_transit_to_restricted
        ))


def path_find(board: Map, turns: list[Turn]) -> ExploringDrone:
    active_drones = [ExploringDrone([board.start_hub], [], board.start_hub)]
    turn_number = 0
    MAX_TURNS = 1000
    MAX_DRONES_PER_HUB = 3  # ✅ Keep top 3 paths per hub

    while not any(d.actual_hub == board.end_hub for d in active_drones):
        if turn_number >= MAX_TURNS:
            raise RuntimeError(f"No path found in turn limit max={MAX_TURNS}")

        if turn_number >= len(turns):
            turns.append(Turn())

        turn = turns[turn_number]
        next_generation: list[ExploringDrone] = []

        for drone in active_drones:
            move_turn(turn, next_generation, drone)

        if not next_generation:
            raise RuntimeError("No valid path exists")

        # ✅ Keep multiple drones per hub
        by_hub: dict[str, list[ExploringDrone]] = {}
        for drone in next_generation:
            key = drone.actual_hub.name
            if key not in by_hub:
                by_hub[key] = []
            by_hub[key].append(drone)

        # Keep best N paths per hub
        active_drones = []
        for hub_name, drones in by_hub.items():
            # Sort by path length, keep top N
            sorted_drones = sorted(drones, key=lambda d: len(d.path))
            active_drones.extend(sorted_drones[:MAX_DRONES_PER_HUB])

        turn_number += 1

    best = get_best_drone(active_drones, board.end_hub)
    set_drone_in_turns(best, turns)
    return best


def algo(board: Map) -> None:
    turns: list[Turn] = []
    paths: list[list[Hub | None]] = []

    for _ in range(board.drones_nb):
        pathfinder: ExploringDrone = path_find(board, turns)
        paths.append(pathfinder.path)

    board.set_drones_steps(paths)
