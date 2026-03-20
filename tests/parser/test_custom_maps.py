from src.features.parser import MapData


def valid_maps_test_parsing() -> bool:

    MAPS: list[str] = [
        "tests/parser/valid_maps/map_1.txt",
        "tests/parser/valid_maps/map_2.txt",
        "tests/parser/valid_maps/map_3.txt",
        "tests/parser/valid_maps/map_4.txt",
        "tests/parser/valid_maps/map_5.txt",
        "tests/parser/valid_maps/map_6.txt",
        "tests/parser/valid_maps/map_7.txt",
        "tests/parser/valid_maps/map_8.txt",
        "tests/parser/valid_maps/map_9.txt",
        "tests/parser/valid_maps/map_10.txt",
    ]

    return_value: bool = True

    print()
    print()
    print("Starting Test for Custom Valid Maps")

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
    valid_maps_test_parsing()
