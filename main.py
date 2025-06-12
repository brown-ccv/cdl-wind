from pathlib import Path
import argparse
import base64
import io
import logging

from PIL import Image
from tqdm import tqdm
from google import genai
from google.genai import types

from gemini import GeminiModel
from parser import process_response, convert_dicts_to_dataframe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler("app.log"),  # File output
    ],
)
logger = logging.getLogger(__name__)


def create_gemini_content(instructions, prompt, encoded_image):
    """
    Creates the content structure for the Gemini API request.

    Args:
        instructions (str): The instructions for the model.
        prompt (str): The prompt for the model.
        encoded_image (str): The base64 encoded image string.

    Returns:
        list: A list of types.Content objects ready for the Gemini API.
    """
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(text=instructions),
                types.Part(text=prompt),
                types.Part(
                    inline_data=types.Blob(
                        mime_type="image/png", data=base64.b64decode(encoded_image)
                    )
                ),
            ],
        )
    ]
    return contents


SAFETY_SETTINGS = [
    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
]


def create_generate_content_config(
    temperature=0, top_p=0.95, max_output_tokens=8192, response_modalities=["TEXT"]
):
    """
    Creates and returns a GenerateContentConfig object with predefined settings.

    Returns:
        types.GenerateContentConfig: A configured GenerateContentConfig object.
    """
    generate_content_config = types.GenerateContentConfig(
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_output_tokens,
        response_modalities=response_modalities,
        safety_settings=SAFETY_SETTINGS,
    )
    return generate_content_config


def load_image(image_path: Path) -> str | None:
    """Loads an image and returns it as a base64 encoded string."""
    try:
        with Image.open(image_path) as img:
            buffered = io.BytesIO()
            img.save(buffered, format=img.format)
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return img_str
    except Exception as _:
        logger.error(f"Error loading image {image_path}", exc_info=True)
        return None


def load_text_file(file_path: Path) -> str | None:
    """Loads the content of a text file."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception:
        logger.error(f"Error loading file {file_path}", exc_info=True)
        return None


def generate_analysis(client, model, image_folder, instructions, prompt, output_file):
    """Generates analysis for images in a folder based on instructions and prompt."""
    image_files = [f for f in image_folder.rglob("*") if f.is_file()]
    results = []

    for image_file in tqdm(image_files, desc=""):
        logger.info("Processing image %s", image_file)
        encoded_image = load_image(image_file)
        if encoded_image is None:
            continue

        contents = create_gemini_content(instructions, prompt, encoded_image)

        generate_content_config = types.GenerateContentConfig(
            temperature=0,
            top_p=0.95,
            max_output_tokens=8192,
            response_modalities=["TEXT"],
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT", threshold="OFF"
                ),
            ],
        )

        try:
            response = client.models.generate_content(
                model=model, contents=contents, config=generate_content_config
            )

            # Process the response
            response_text = response.text
            _result = process_response(response_text, image_file)
            if _result:
                _result["id"] = image_file
                # TODO: remove this with better prompt
                del _result["Image ID"]
                results.append(_result)
            else:
                logger.error("Error loading image %s", image_file, exc_info=True)

        except Exception as e:
            logger.error("Error processing image %s: %s", image_file, e)

    # Format and print the results
    results_df = convert_dicts_to_dataframe(results)

    # Move id column to leftmost position
    if "id" in results_df.columns:
        id_col = results_df.pop("id")
        results_df.insert(0, "id", id_col)

    results_df = results_df.drop_duplicates(subset=["id"])
    results_df.to_csv(output_file, index=False)


def main():
    """Main function to run the image analysis."""
    model_choices = [model.value for model in GeminiModel]
    parser = argparse.ArgumentParser(description="Analyze images using Gemini API.")
    parser.add_argument(
        "--image-folder",
        default="assets",
        help="Path to the folder containing images.",
        type=Path,
    )
    parser.add_argument(
        "--instructions-file",
        default="instruction.txt",
        help="Path to the instructions text file.",
        type=Path,
    )
    parser.add_argument(
        "--prompt-file",
        default="prompt.txt",
        help="Path to the prompt text file.",
        type=Path,
    )
    parser.add_argument(
        "--project", default="get-think-tank-urls", help="GCP project ID"
    )
    parser.add_argument("--location", default="us-central1", help="GCP location")
    parser.add_argument(
        "--model",
        default=GeminiModel.PRO_2_5_FLASH_PREVIEW.value,
        required=False,  # Make it mandatory for this simple example
        choices=model_choices,
        metavar="MODEL_IDENTIFIER",  # Helps in the --help message
        help=(
            "The Gemini model identifier to use. Choose from: "
            f"{', '.join(model_choices)}"
        ),
    )
    parser.add_argument("--output", help="Ouput file path", type=Path)

    args = parser.parse_args()

    client = genai.Client(vertexai=True, project=args.project, location=args.location)
    model = args.model
    instructions = load_text_file(args.instructions_file)
    prompt = load_text_file(args.prompt_file)

    if instructions and prompt:
        generate_analysis(
            client, model, args.image_folder, instructions, prompt, args.output
        )
    else:
        logger.error("Error: Could not load instructions or prompt.")


if __name__ == "__main__":
    main()
