"""Convert `file names with spaces.ext` to `file_names_with_spaces.ext`"""

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def rename_spaces(directory):
    """Renames files and directories in the specified directory (or the current directory if none is provided) and its subdirectories, replacing spaces with underscores."""

    directory_path = Path(directory)
    if not directory_path.exists():
        logging.error("Directory '%s' not found.", directory_path)
        return

    for path in directory_path.rglob("*"):
        if " " in path.name:
            new_name = path.name.replace(" ", "_")
            new_path = path.with_name(new_name)
            try:
                path.rename(new_path)
                logging.info(f"Renamed '{path}' to '{new_path}'")
            except OSError as e:
                logging.error(f"Error renaming '{path}': {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Rename files and directories, replacing spaces with underscores."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to process (default: current directory)",
    )
    args = parser.parse_args()

    rename_spaces(args.directory)


if __name__ == "__main__":
    main()
