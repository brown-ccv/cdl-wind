import json
import argparse
from pathlib import Path

group_mapping = {
    "New England Offshore Wind Discussion": "NEOW",
    "Protect Our Coast - NJ Community Group": "PCNJ",
    "Protect Our Oceans MA": "PCMA",
    "Protect Our Coast - LINY": "PCLI",
    "Saltwater Scam": "SLSC",
    "Fishermen Steward": "FIST",
    "Save LBI": "SLBI",
    "LICFA": "LICF",  # Assuming LICFA maps to LICF as there's no separate code
    "ACK 4 Whales": "ACKW",
    "Fishermen against offshore wind: Maine Group": "FAWM",
}


def infer_group_code_from_path(file_path: str, group_mapping: dict = group_mapping) -> str | None:
    """Infers the Facebook group code from the file path based on directory names.

    Args:
        file_path (str): The path to the file.
        group_mapping (dict): A dictionary mapping group names to their codes.

    Returns:
        str: The inferred group code, or None if no match is found.
    """
    path = Path(file_path)
    for directory in path.parts:
        for group_name, group_code in group_mapping.items():
            if group_code.lower() in directory.lower() or group_name.lower() in directory.lower():
                return group_code
    return None


def assign_post_id(filename, id_file="post_ids.json", directory="screenshots", group_mapping: dict = group_mapping):
    """Assigns a unique post ID to a file based on its group (inferred from the path) and updates the ID record.

    Args:
        filename (str): The name of the file to assign an ID to, including (part of) the path.
        id_file (str, optional): The name of the file to store ID data. Defaults to "post_ids.json".
        directory (str, optional): The base directory containing the files. Defaults to "screenshots".
        group_mapping (dict): A dictionary mapping group names to their codes.

    Returns:
        tuple: The original filename and the assigned post ID, or (None, None) if an error occurred or the group couldn't be inferred.
    """
    try:
        # Infer group code from the file path
        group_code = infer_group_code_from_path(filename, group_mapping)
        if not group_code:
            print(f"Could not infer group code from path: {filename}")
            return None, None

        # Load existing ID data
        id_file_path = Path(id_file)
        if id_file_path.exists():
            with open(id_file_path, "r") as f:
                id_data = json.load(f)
        else:
            id_data = {}

        # Get the last assigned ID for the group, or initialize if new
        last_id = id_data.get(group_code, 0)
        next_id = last_id + 1

        # Format the new ID
        post_id = f"{group_code}-{next_id:04d}"

        # Update the ID data and save
        id_data[group_code] = next_id
        with open(id_file_path, "w") as f:
            json.dump(id_data, f)

        return filename, post_id

    except Exception as e:
        print(f"Error: {e}")
        return None, None


def process_directory(directory="screenshots", index_file="file_index.json"):
    """Processes all files within the specified directory and its subdirectories, creating an index.

    Args:
        directory (str): The directory to process.
        index_file (str): The name of the file to store the index.
    """
    directory_path = Path(directory)
    index = {}
    for file_path in directory_path.rglob("*"):
        if file_path.is_file():
            relative_path = str(file_path.relative_to(directory_path))
            original_filename = relative_path  # Store the original relative path
            filename, post_id = assign_post_id(original_filename)
            if filename and post_id:
                index[original_filename] = post_id

    # Save the index to a JSON file
    with open(index_file, "w") as f:
        json.dump(index, f, indent=4)
    print(f"Index saved to {index_file}")


def main():
    parser = argparse.ArgumentParser(description="Create an index of files with unique post IDs.")
    parser.add_argument(
        "--directory",
        default="screenshots",
        help="The directory to process. Defaults to 'screenshots'.",
    )
    parser.add_argument(
        "--index-file",
        default="file_index.json",
        help="The name of the file to store the index. Defaults to 'file_index.json'.",
    )
    args = parser.parse_args()

    process_directory(args.directory, args.index_file)
    print("Finished processing files.")


if __name__ == "__main__":
    main()
