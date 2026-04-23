from ...utils.types import HubType
from ..map.Map import Map
from ..map.Hub import Hub
from .reservation_map import Turn, ExploringDrone, set_drone_in_turns


def get_best_drone(
        drones: list[ExploringDrone],
        end_hub: Hub
                   ) -> ExploringDrone:
    """
        Description:
    after at least a drone finished the map it returns the better one
    that have finished considering the path len and the priority hub

        Parameters:
    drones -> list of ExploringDrone that have a path from the start to
              the end containing all the hubs it goes throught and None for
              the turns it waits
    end_hub -> the hub that is considered the goal to see which drone finished
               the map

        Return value:
    the ExploringDrone that has the best path
    """

    finished: list[ExploringDrone] = [
            drone for drone in drones if drone.actual_hub is end_hub
            ]

    if not finished:
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
    """
        Description:
    Take a drone and create a drone for each possible connections
    and let one in the hub if there is a hub it can't go

        Parameters:
    turn -> reservation_map that contains all the drones that are
            on hubs and the connection that are used for a turn
    drones -> list of ExploringDrone that have a path from the start to
              the end containing all the hubs it goes throught and None for
              the turns it waits
    drone -> the ExploringDrone that is used to create all the possibilitys
    """
    if drone.in_transit_to_restricted:
        last_connection = drone.connections[-1]
        if not last_connection:
            return

        new_drone = turn.move_drone(drone, last_connection)

        if new_drone:
            new_drone.connections[-1] = None
            drones.append(new_drone)
        return

    all_moved = True
    for connection in drone.actual_hub.connections:
        new_drone = turn.move_drone(drone, connection)
        if new_drone:
            drones.append(new_drone)
        else:
            all_moved = False

    if not all_moved:
        drones.append(ExploringDrone(
            [*drone.path, None],
            [*drone.connections, None],
            drone.actual_hub,
            drone.in_transit_to_restricted
        ))


def path_find(board: Map, turns: list[Turn]) -> ExploringDrone:
    """
        Description:
    while no drone finished it creates new drones with the move_turn func for
    each turn to simulate the path of each possible drone and keep only
    maximum 3 drones per hub to permit best moves considering the 2 time
    movement for the restricted hub and return the drone that has the best path

        Parameters:
    board -> a valid map with connection, hubs and drones
    turns -> A reservation_map that contains all the drones that
             are on hubs and the connection that are used for
             each turn

        Return value:
    return an ExploringDrone that have a path from the start to
    the end containing all the hubs it goes throught and None for
    the turns it waits
    """
    active_drones = [ExploringDrone([board.start_hub], [], board.start_hub)]
    turn_number = 0
    MAX_DRONES_PER_HUB = 3

    while not any(d.actual_hub == board.end_hub for d in active_drones):
        if turn_number >= len(turns):
            turns.append(Turn())

        turn = turns[turn_number]
        next_generation: list[ExploringDrone] = []

        for drone in active_drones:
            move_turn(turn, next_generation, drone)

        if not next_generation:
            raise RuntimeError("No valid path exists")

        by_hub: dict[str, list[ExploringDrone]] = {}
        for drone in next_generation:
            key = drone.actual_hub.name
            if key not in by_hub:
                by_hub[key] = []
            by_hub[key].append(drone)

        active_drones = []
        for _, drones in by_hub.items():
            sorted_drones = sorted(drones, key=lambda d: len(d.path))
            active_drones.extend(sorted_drones[:MAX_DRONES_PER_HUB])

        turn_number += 1

    best = get_best_drone(active_drones, board.end_hub)
    set_drone_in_turns(best, turns)
    return best


def algo(board: Map) -> None:
    """
        Description:
    get the best path for each drones using the pathfinder func considering
    the reservation_map and set them in the drones in the Map

        Parameters:
    board -> a valid map with connection, hubs and drones
    """
    turns: list[Turn] = []
    paths: list[list[Hub | None]] = []

    for _ in range(board.drones_nb):
        pathfinder: ExploringDrone = path_find(board, turns)
        paths.append(pathfinder.path)

    board.set_drones_steps(paths)
