from sys import argv
from PyQt6.QtWidgets import QApplication

from src.features.map.Map import Map
from src.features.parser import MapData
from src.features.algo.algo import algo
from src.features.visualizer.map_visu import MainWindow


def main() -> None:

    if len(argv) != 2:
        print("Wrong usage of fly-in, usage:\n" "python3 fly_in.py <map>")
        return

    filename = argv[1]
    map_data: MapData = MapData()

    try:
        map_data.parsing(filename)
        map_info: Map = Map(map_data.get_map_data())
        algo(map_info)
        map_info.print_algo()

    except Exception as err:
        print(err)
        return

    app = QApplication([])
    window = MainWindow(map_info)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
