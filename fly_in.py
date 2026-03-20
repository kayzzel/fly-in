from src.features.parser import MapData
from sys import argv


def main() -> None:

    if len(argv) != 2:
        print(
                "Wrong usage of fly-in, usage:\n"
                "python3 fly_in.py <map>"
              )
        return

    filename = argv[1]

    map_data: MapData = MapData()

    try:
        map_data.parsing(filename)

    except Exception as err:
        print(err)
        return

    print(map_data)
    return


if __name__ == "__main__":
    main()
