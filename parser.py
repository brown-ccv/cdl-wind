import json
import logging
import re
from functools import reduce
from pprint import pp

import pandas as pd
from json_repair import repair_json

logger = logging.getLogger(__name__)


def parse_json_like_output(output_text, image_name=None):
    """
    Parses a JSON-like string into a Python dictionary.

    Args:
        output_text: The string output from the AI, resembling a JSON dictionary.

    Returns:
        A Python dictionary representing the parsed data, or None if parsing fails.
    """
    try:
        # Remove any leading/trailing whitespace and newlines
        output_text = output_text.strip()

        # Handle cases where the AI might include extra characters or newlines
        # before or after the curly braces, or markdown code blocks.
        if output_text.startswith("```json") and output_text.endswith("```"):
            output_text = output_text[7:-3].strip()
        elif not output_text.startswith("{") or not output_text.endswith("}"):
            # Attempt to find the dictionary within the string
            match = re.search(r"\{.*\}", output_text, re.DOTALL)
            if match:
                output_text = match.group(0)
            else:
                logger.error("Error: Could not find a dictionary within the output.")
                return None

        # Replace single quotes with double quotes for valid JSON
        output_text = repair_json(output_text.replace("'", '"'))

        # Load the string as a JSON object
        data = json.loads(output_text)
        return data

    except json.JSONDecodeError:
        img_name = f"for image {image_name}." if image_name else "."
        problematic_content = f"\nProblematic content:\n{output_text}"
        log_message = f"Error: Invalid JSON format {img_name}{problematic_content}"
        logger.error(log_message, exc_info=True)
        return None
    except Exception:
        base_message = "An unexpected error occurred while processing text"
        log_message = f"{base_message} from {image_name}." if image_name else "."
        logger.error(log_message, exc_info=True)
        return None


def process_response(response_text, image_name=None):
    """
    Processes the raw response text from the AI, parses it into a dictionary,
    and returns a structured dictionary.

    Args:
        response_text: The raw text response from the AI.

    Returns:
        A dictionary containing the parsed data, or None if parsing fails.
    """
    parsed_data = parse_json_like_output(response_text, image_name)
    if parsed_data:
        return parsed_data
    else:
        return None


def convert_dicts_to_dataframe(list_of_dicts):
    """
    Converts a list of dictionaries into a single pandas DataFrame.

    Args:
        list_of_dicts (list): A list where each element is a dictionary with the same keys.

    Returns:
        pd.DataFrame: A concatenated DataFrame with all dictionaries as rows.
    """

    # Convert each dictionary to a DataFrame (one row per dict)
    def dict_to_df(d):
        return pd.DataFrame({k: [v] for k, v in d.items()})

    list_of_dfs = list(map(dict_to_df, list_of_dicts))

    # Concatenate all DataFrames vertically (like vcat)
    final_df = reduce(
        lambda x, y: pd.concat([x, y], axis=0, ignore_index=True), list_of_dfs
    )

    return final_df


if __name__ == "__main__":
    txt = '```json\n{\n    "Image ID": "75.png",\n    "1": "Protect Our Coast - NJ Community Group",\n    "2": "To those who love boating and fishing on Long Island and along the entire United States coastline, even extending into our Great Lakes and the Gulf of Mexico. ... See more",\n    "3": "38",\n    "4": "Cannot determine from image",\n    "5": "Yes",\n    "6": "The image shows a large body of water with many wind turbines in the background.",\n    "7": "Mike Jacobs",\n    "8": "Yes",\n    "9": "January 25, 2024",\n    "10": "Oppose",\n    "11": "No",\n    "12": "Scenic beauty: impacts on views/beauty/aesthetic quality of the land or seascape",\n    "13": "Scenic beauty",\n    "14": "No",\n    "15": "Climate solutions won’t work",\n    "16": "Cannot determine from image",\n    "17": "Climate policies are ineffective"\n}\n```'
    pp(process_response(txt))
    data = [
        {"1": "A", "2": "B", "id": "file1.png"},
        {"1": "C", "2": "D", "id": "file2.png"},
    ]

    df = convert_dicts_to_dataframe(data)
    print(df)
