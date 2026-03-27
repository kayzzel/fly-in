from sys import argv

from src.features.map.Map import Map
from src.features.parser import MapData


def main() -> None:

    if len(argv) != 2:
        print("Wrong usage of fly-in, usage:\n" "python3 fly_in.py <map>")
        return

    filename = argv[1]

    map_data: MapData = MapData()

    try:
        map_data.parsing(filename)
        map_info: Map = Map(map_data.get_map_data())

    except Exception as err:
        print(err)
        return

    print(map_info)
    print(map_data)
    return


if __name__ == "__main__":
    main()
