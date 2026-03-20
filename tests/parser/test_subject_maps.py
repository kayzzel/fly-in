from src.features.parser import MapData


def subject_maps_test_parsing() -> bool:

    MAPS: list[str] = [
        "maps/easy/01_linear_path.txt",
        "maps/easy/02_simple_fork.txt",
        "maps/easy/03_basic_capacity.txt",
        "maps/medium/01_dead_end_trap.txt",
        "maps/medium/02_circular_loop.txt",
        "maps/medium/03_priority_puzzle.txt",
        "maps/hard/01_maze_nightmare.txt",
        "maps/hard/02_capacity_hell.txt",
        "maps/hard/03_ultimate_challenge.txt",
        "maps/challenger/01_the_impossible_dream.txt",
    ]

    return_value: bool = True

    print("Starting Test for Subject Map")

    for subject_map in MAPS:
        print()
        print(f'\033[95mTEST "{subject_map}":\033[0m')

        try:
            map_data: MapData = MapData()

            map_data.parsing(subject_map)

            print(map_data)

        except Exception as err:
            print(f"\033[93m/!\\ {err.__class__.__name__}: {err}\033[0m")

            return_value = False

    return return_value


if __name__ == "__main__":
    subject_maps_test_parsing()
