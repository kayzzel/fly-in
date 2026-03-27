from pathlib import Path

import pytest

from src.features.parser import MapData
from src.features.map.Map import Map

# Anchors
TEST_DIR = Path(__file__).parent  # tests/parser/
ROOT_DIR = TEST_DIR.parent.parent  # project root


def _should_parse(path: Path) -> Map:
    map_data = MapData()
    map_data.parsing(str(path))
    map_struct: Map = Map(map_data.get_map_data())
    return map_struct


# ── invalid maps ─────────────────────────────────────────────────────────────


INVALID_MAPS = [
    TEST_DIR / "invalid_maps" / f"map_{i}.txt" for i in range(1, 11)
]


@pytest.mark.parametrize(
    "map_path", INVALID_MAPS, ids=[f"map_{i}" for i in range(1, 11)]
)
def test_invalid_map_raises(map_path: Path) -> None:
    with pytest.raises(Exception):
        _should_parse(map_path)


# ── valid custom maps ────────────────────────────────────────────────────────


VALID_MAPS = [TEST_DIR / "valid_maps" / f"map_{i}.txt" for i in range(1, 11)]


@pytest.mark.parametrize(
    "map_path", VALID_MAPS, ids=[f"map_{i}" for i in range(1, 11)]
)
def test_valid_map_parses(map_path: Path) -> None:
    map_data: Map = _should_parse(map_path)
    assert map_data is not None


# ── subject maps ─────────────────────────────────────────────────────────────


SUBJECT_MAPS = [
    ROOT_DIR / "maps/easy/01_linear_path.txt",
    ROOT_DIR / "maps/easy/02_simple_fork.txt",
    ROOT_DIR / "maps/easy/03_basic_capacity.txt",
    ROOT_DIR / "maps/medium/01_dead_end_trap.txt",
    ROOT_DIR / "maps/medium/02_circular_loop.txt",
    ROOT_DIR / "maps/medium/03_priority_puzzle.txt",
    ROOT_DIR / "maps/hard/01_maze_nightmare.txt",
    ROOT_DIR / "maps/hard/02_capacity_hell.txt",
    ROOT_DIR / "maps/hard/03_ultimate_challenge.txt",
    ROOT_DIR / "maps/challenger/01_the_impossible_dream.txt",
]


SUBJECT_IDS = [p.stem for p in SUBJECT_MAPS]


@pytest.mark.parametrize("map_path", SUBJECT_MAPS, ids=SUBJECT_IDS)
def test_subject_map_parses(map_path: Path) -> None:
    map_data: Map = _should_parse(map_path)
    assert map_data is not None
