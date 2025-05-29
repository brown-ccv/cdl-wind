"""Convert `file names with spaces.ext` to `file_names_with_spaces.ext`"""

import argparse
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def replace_space_like(text, replacement="_"):
    """Replaces all Unicode whitespace characters with a replacement character."""
    return re.sub(r"\s", replacement, text)


def rename_spaces(directory):
    """Renames files and directories in the specified directory (or the current directory if none is provided) and its subdirectories, replacing spaces with underscores."""

    directory_path = Path(directory)
    if not directory_path.exists():
        logging.error("Directory '%s' not found.", directory_path)
        return

    for path in directory_path.rglob("*"):
        new_name = replace_space_like(path.name)
        new_path = path.with_name(new_name)
        try:
            path.rename(new_path)
            logging.debug("Renamed %s to '%s'", path, new_path)
        except OSError as e:
            logging.error("Error renaming '%s': %s", path, e)


def main():
    parser = argparse.ArgumentParser(
        description="Rename files and directories, replacing spaces with underscores."
    )
    parser.add_argument(
        "directory",
        help="Directory to process (default: current directory)",
    )
    args = parser.parse_args()

    rename_spaces(args.directory)


if __name__ == "__main__":
    main()
