from .test_custom_false_maps import invalid_maps_test_parsing
from .test_custom_maps import valid_maps_test_parsing
from .test_subject_maps import subject_maps_test_parsing


def test_parsing() -> None:
    print(
        """
choose the test you want to do:
    -> subject maps        (1)
    -> valid custom maps   (2)
    -> invalid custom maps (3)
    -> all                 (4)
    """
    )

    choice: str = input("choice: ")

    if choice == "1":
        subject_maps_test_parsing()

    elif choice == "2":
        valid_maps_test_parsing()

    elif choice == "3":
        invalid_maps_test_parsing()

    elif choice == "4":
        subject_maps_test_parsing()
        valid_maps_test_parsing()
        invalid_maps_test_parsing()

    else:
        print("/!\\ INVALID choice")


if __name__ == "__main__":
    test_parsing()
