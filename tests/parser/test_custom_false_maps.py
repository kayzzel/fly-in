from src.features.parser import MapData


def invalid_maps_test_parsing() -> bool:

    MAPS: list[str] = [
        "tests/parser/invalid_maps/map_1.txt",
        "tests/parser/invalid_maps/map_2.txt",
        "tests/parser/invalid_maps/map_3.txt",
        "tests/parser/invalid_maps/map_4.txt",
        "tests/parser/invalid_maps/map_5.txt",
        "tests/parser/invalid_maps/map_6.txt",
        "tests/parser/invalid_maps/map_7.txt",
        "tests/parser/invalid_maps/map_8.txt",
        "tests/parser/invalid_maps/map_9.txt",
        "tests/parser/invalid_maps/map_10.txt",
    ]

    return_value: bool = True

    print()
    print()
    print("Starting Test for Custom Invalid Maps")

    for subject_map in MAPS:
        print()
        print(f'\033[95mTEST "{subject_map}":\033[0m')

        try:
            map_data: MapData = MapData()

            map_data.parsing(subject_map)

            print("\033[93m/!\\ No error detected, invalid map\033[0m")

        except Exception as err:
            print(f"{err.__class__.__name__}: {err}")

            return_value = False

    return return_value


if __name__ == "__main__":
    invalid_maps_test_parsing()
