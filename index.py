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
    "New England Offshore Wind Discussion": "NEOW",
    "Protect Our Coast - NJ Community Group": "PCNJ",
    "Protect Our Coast NJ Community Group": "PCNJ",
    "Protect Our Oceans MA": "PCMA",
    "Protect Our Coast - LINY": "PCLI",
    "Protect Our Coast LINY": "PCLI",
    "Saltwater Scam": "SLSC",
    "Fishermen Steward": "FIST",
    "Save LBI": "SLBI",
    "LICFA": "LICF",  # Assuming LICFA maps to LICF as there's no separate code
    "ACK 4 Whales": "ACKW",
    "Fishermen against offshore wind: Maine Group": "FAWM",
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
    filename,
    index,  # Pass the index as an argument
    group_mapping: dict = group_mapping,
):
    try:
        group_code = infer_group_code_from_path(filename, group_mapping)
        if not group_code:
            logger.warning(f"Could not infer group code from path: {filename}")
            return None, None

        next_id = get_next_post_id(group_code, index)
        post_id = f"{group_code}-{next_id:04d}"

        return filename, post_id

    except Exception as e:
        logger.error(f"Error: {e}")
        return None, None


def process_directory(
    directory: str | Path = "assets", index_file: str | Path = "file_index.json"
):
    directory_path = Path(directory)
    index_file_path = Path(index_file)

    if index_file_path.exists():
        with open(index_file_path, "r") as f:
            index = OrderedDict(json.load(f))  # Load as OrderedDict
    else:
        index = OrderedDict()

    for file_path in sorted(directory_path.rglob("*")):
        process_file_condition = all(
            [file_path.is_file(), file_path.suffix.lower() in image_file_extensions]
        )
        if process_file_condition:
            logger.info("Processing file: %s", file_path)
            original_filename = str(file_path.relative_to(directory_path))
            if original_filename == "ACK 4 Whales/bar copy.png":
                breakpoint()
            if original_filename not in index:  # Only process new files
                filename, post_id = assign_post_id(
                    original_filename, index
                )  # Pass index
                if filename and post_id:
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
        directory: str | Path = "assets", index_file: str | Path = "file_index.json"
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
                original_filename = str(file_path.relative_to(directory_path))
                if original_filename not in index:
                    filename, post_id = assign_post_id(original_filename, index)
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
    parser = argparse.ArgumentParser(
        description="Create an index of files with unique post IDs."
    )
    parser.add_argument(
        "--directory",
        "-d",
        default="assets",
        help="The directory to process. Defaults to 'assets'.",
    )
    parser.add_argument(
        "--index-file",
        "-i",
        default="file_index.json",
        help="The name of the file to store the index. Defaults to 'file_index.json'.",
    )
    args = parser.parse_args()

    process_directory(args.directory, args.index_file)
    logger.info("Finished processing files.")


if __name__ == "__main__":
    main()
