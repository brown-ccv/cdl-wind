import pytest
from collections import OrderedDict
import json

from index import (
    infer_group_code_from_path,
    get_next_post_id,
    assign_post_id,
    process_directory,
)


@pytest.fixture
def assets_dir(tmp_path):
    """Creates a temporary directory structure for testing and returns its path."""
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "New England Offshore Wind Discussion").mkdir()
    (assets_dir / "Protect Our Coast - NJ Community Group").mkdir()
    (assets_dir / "Unknown Group").mkdir()

    # Create dummy files
    (assets_dir / "New England Offshore Wind Discussion" / "image1.png").touch()
    (assets_dir / "Protect Our Coast - NJ Community Group" / "image2.jpg").touch()
    (assets_dir / "Unknown Group" / "image3.gif").touch()
    (assets_dir / "not_an_image.txt").touch()

    return assets_dir


def test_infer_group_code_from_path():
    # Test cases for infer_group_code_from_path
    assert (
        infer_group_code_from_path(
            "assets/New England Offshore Wind Discussion/image.png"
        )
        == "NEOW"
    )
    assert (
        infer_group_code_from_path(
            "assets/Protect Our Coast - NJ Community Group/image.jpg"
        )
        == "PCNJ"
    )
    assert infer_group_code_from_path("assets/Unknown Group/image.gif") == "MISC"


def test_get_next_post_id():
    # Test cases for get_next_post_id
    index = OrderedDict(
        {
            "file1.png": "NEOW-0001",
            "file2.jpg": "NEOW-0002",
            "file3.png": "PCNJ-0001",
        }
    )
    assert get_next_post_id("NEOW", index) == 3
    assert get_next_post_id("PCNJ", index) == 2
    assert get_next_post_id("MISC", index) == 1


def test_assign_post_id():
    # Test cases for assign_post_id
    index = OrderedDict()
    post_id = assign_post_id(
        "assets/New England Offshore Wind Discussion/image.png", index
    )
    assert post_id == "NEOW-0001"

    index = OrderedDict(
        {"assets/New England Offshore Wind Discussion/image.png": "NEOW-0001"}
    )
    post_id = assign_post_id(
        "assets/New England Offshore Wind Discussion/image2.png", index
    )
    assert post_id == "NEOW-0002"

    post_id = assign_post_id("assets/Unknown Group/image.gif", index)
    assert post_id == "MISC-0001"


def test_process_directory(assets_dir):
    # Use the temporary directory created by the fixture
    index_file = assets_dir.parent / "file_index.json"

    # Process the directory
    process_directory(str(assets_dir), str(index_file))

    # Check the index file content
    with open(index_file, "r") as f:
        index = json.load(f)

    expected_index = {
        "New England Offshore Wind Discussion/image1.png": "NEOW-0001",
        "Protect Our Coast - NJ Community Group/image2.jpg": "PCNJ-0001",
        "Unknown Group/image3.gif": "MISC-0001",
    }
    assert index == expected_index

    # Process again to check if new files are added correctly
    (assets_dir / "New England Offshore Wind Discussion" / "image4.png").touch()
    process_directory(str(assets_dir), str(index_file))
    with open(index_file, "r") as f:
        index = json.load(f)
    expected_index["New England Offshore Wind Discussion/image4.png"] = "NEOW-0002"
    assert index == expected_index
