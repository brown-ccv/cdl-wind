import argparse
import json
import logging
from collections import OrderedDict, defaultdict
from pathlib import Path
from pprint import pformat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

image_file_extensions = (
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
)

group_mapping = {
    "ACK_4_Whales": "ACKW",
    "Edge_Case_Tests": "MISC",
    "Fishermen_Steward": "FIST",
    "Fishermen_Against_Offshore_Wind": "FAWM",
    "Green_Oceans": "MISC",
    "LICFA": "LICF",
    "New_England_Fishermen_s_Stewardship_Association": "NEFS",  # added
    "New_England_Offshore_Wind_Discussion": "NEOW",
    "Protect_Our_Coast_LINY": "PCLI",
    "Protect_Our_Coast_NJ_community_group": "PCNJ",
    "Protect_Our_Oceans_MA": "PCMA",
    "Saltwater_Scam": "SLSC",
    "Save_LBI": "SLBI",
}


def infer_group_code_from_path(
    file_path: str | Path, group_mapping: dict = group_mapping
) -> str:
    path = Path(file_path)
    parent_dir = path.parent.name  # Extract the name of the parent directory
    return group_mapping.get(parent_dir, "MISC")


def get_next_post_id(group_code, index):
    """Computes the next available post ID for a group based on the existing index."""
    max_id = 0
    for filename, post_id in index.items():
        if post_id.startswith(group_code):
            try:
                current_id = int(post_id.split("-")[1])
                max_id = max(max_id, current_id)
            except ValueError:
                logger.warning(f"Invalid post ID format: {post_id}")
    return max_id + 1


def assign_post_id(
    filename: str | Path,
    index: OrderedDict,
    mapping: None | dict = group_mapping,
):
    if mapping is None:
        mapping = group_mapping
    else:
        with open(mapping, "r") as f:
            mapping = json.load(f)

    try:
        group_code = infer_group_code_from_path(filename, mapping)
        if not group_code:
            logger.warning(f"Could not infer group code from path: {filename}")
            return None

        next_id = get_next_post_id(group_code, index)
        post_id = f"{group_code}-{next_id:04d}"

        return post_id

    except Exception as e:
        logger.error(f"Error: {e}")
        return None


def is_image_file(file_path):
    return all([file_path.is_file(), file_path.suffix.lower() in image_file_extensions])


def process_directory(
    directory: str | Path, index_file: str | Path, mapping: Path | None
):
    directory_path = Path(directory)
    index_file_path = Path(index_file)

    if index_file_path.exists():
        with open(index_file_path, "r") as f:
            index = OrderedDict(json.load(f))  # Load as OrderedDict
    else:
        index = OrderedDict()

    for file_path in sorted(directory_path.rglob("*")):
        if is_image_file(file_path):
            logger.info("Processing file: %s", file_path)
            original_filename = str(file_path.relative_to(directory_path))
            if original_filename not in index:  # Only process new files
                post_id = assign_post_id(original_filename, index, mapping)
                if post_id:
                    index[original_filename] = post_id

    with open(index_file, "w") as f:
        json.dump(index, f, indent=4)
    logger.info(f"Index saved to {index_file}")


class Index(OrderedDict):
    def __init__(self, directory, index_file):
        # Load or create the index
        index = self.process_directory(directory=directory, index_file=index_file)
        super().__init__(index)

    @staticmethod
    def process_directory(
        directory: str | Path = "assets",
        index_file: str | Path = "file_index.json",
        mapping=None,
    ):
        directory_path = Path(directory)
        index_file_path = Path(index_file)

        if index_file_path.exists():
            with open(index_file_path, "r") as f:
                index = OrderedDict(json.load(f))
        else:
            index = OrderedDict()

        for file_path in sorted(directory_path.rglob("*")):
            process_file_condition = all(
                [file_path.is_file(), file_path.suffix.lower() in image_file_extensions]
            )
            if process_file_condition:
                logger.debug("Processing file: %s", file_path)
                original_filename = str(file_path.relative_to(directory_path))
                if original_filename not in index:
                    filename, post_id = assign_post_id(
                        original_filename, index, mapping
                    )
                    if filename and post_id:
                        index[original_filename] = post_id

        with open(index_file_path, "w") as f:
            json.dump(index, f, indent=4)
        return index

    def __str__(self):
        return pformat(self)

    @property
    def by_group(self):
        result = defaultdict(dict)
        for key, value in self.items():
            prefix, number = value.split("-")
            result[prefix][number] = key
        return result


def main():
    epilog = """Example:
    uv run index.py -d mydir -m mymapping.json -i mynewindex.json
    """
    parser = argparse.ArgumentParser(
        description="Create an index of files with unique post IDs.", epilog=epilog
    )
    parser.add_argument(
        "--directory",
        "-d",
        default="assets",
        help="The directory to process. Defaults to 'assets'.",
    )
    parser.add_argument(
        "--mapping",
        "-m",
        default=None,
        help="The directory to process. Defaults to 'assets'.",
    )
    parser.add_argument(
        "--index-file",
        "-i",
        default="file_index.json",
        help="The name of the file to store the index. Defaults to 'file_index.json'.",
    )
    args = parser.parse_args()

    process_directory(args.directory, args.index_file, args.mapping)
    logger.info("Finished processing files.")


if __name__ == "__main__":
    main()
