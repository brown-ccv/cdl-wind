## Getting Started

### Prerequisites

*   Python 3.12+
*   Google Cloud Project with the Vertex AI API enabled
*   Google Cloud credentials configured (e.g., using `gcloud auth application-default login`)

### Installation

1.  Clone the repository:

    ```bash
    git clone <url-to-this-repository>
    cd <your-repository-directory>
    ```

2.  **Install `uv`:**

    If you don't have `uv` installed, you can install it using `pip`:

    ```bash
    pip install uv
    ```

3.  **Initilaize the virtual environment:**

    ```bash
    uv sync
    ```

### Configuration

We recommend using this project within a Google Cloud project using a Google Cloud Shell session.

### Usage

1.  **Prepare Images:** Place the images you want to analyze in a folder (e.g., `assets`).
2.  **Prepare Instructions:** Create a text file (`instruction.txt`, for example) containing the instructions for the Gemini API. This should describe the overall task you want the API to perform.
3.  **Prepare Prompts:** Create a text file (`prompt.txt`, for example) containing the prompt for the Gemini API. This should define the specific information you want to extract from each image.

4.  **Run the Script:**
    There are two commands available `main.py` (serial) and `main-t.py` (threaded)

        ```bash
        $ uv run main.py --help
        usage: main.py [-h] [--image-folder IMAGE_FOLDER] [--instructions-file INSTRUCTIONS_FILE] [--prompt-file PROMPT_FILE] [--project PROJECT]
                    [--location LOCATION] [--model MODEL_IDENTIFIER] [--output OUTPUT]

        Analyze images using Gemini API.

        options:
        -h, --help            show this help message and exit
        --image-folder IMAGE_FOLDER
                                Path to the folder containing images.
        --instructions-file INSTRUCTIONS_FILE
                                Path to the instructions text file.
        --prompt-file PROMPT_FILE
                                Path to the prompt text file.
        --project PROJECT     GCP project ID
        --location LOCATION   GCP location
        --model MODEL_IDENTIFIER
                                The Gemini model identifier to use. Choose from: gemini-2.5-pro-preview-03-25, gemini-2.0-flash, gemini-2.0-flash-001,
                                gemini-2.0-flash-lite, gemini-2.0-flash-lite-001, gemini-2.0-pro-exp-02-05, gemini-2.0-flash-thinking-exp-01-21,
                                gemini-1.5-pro, gemini-1.5-pro-latest, gemini-1.5-pro-002, gemini-1.5-flash, gemini-1.5-flash-latest,
                                gemini-1.5-flash-002, gemini-1.5-flash-8b, gemini-1.5-flash-8b-latest, gemini-1.5-flash-8b-001, text-embedding-004,
                                gemini-embedding-exp, models/aqa
        --output OUTPUT       Ouput file path
        ```

    **Example:**

        ```bash
        uv run main.py --image-folder myimgs/ --instructions-file myinstruction.txt --prompt-file myprompt.txt --output myoutput.csv
        ```

    ### Other tooling
    - **Clean up file names**: images generated using screencapture apps may generate files names with strange invisible characters across different OSs. The `clean_names.py` recursively normalizes all file and directory names in a given directory.

        ```bash
        $ uv run clean_names.py --help
        usage: clean_names.py [-h] directory

        Rename files and directories, replacing spaces with underscores.

        positional arguments:
        directory   Directory to process (default: current directory)

        options:
        -h, --help  show this help message and exit

        Example: uv run clean_names.py mydirectory/
        ```

    - **File indexing**: Create a file index for the given `directory`. File names are encoded sequentially the provided `mapping`.
        ```bash
        $ uv run index.py --help
        usage: index.py [-h] [--directory DIRECTORY] [--mapping MAPPING]
                        [--index-file INDEX_FILE]

        Create an index of files with unique post IDs.

        options:
        -h, --help            show this help message and exit
        --directory DIRECTORY, -d DIRECTORY
                                The directory to process. Defaults to 'assets'.
        --mapping MAPPING, -m MAPPING
                                The directory to process. Defaults to 'assets'.
        --index-file INDEX_FILE, -i INDEX_FILE
                                The name of the file to store the index. Defaults to
                                'file_index.json'.

        Example: uv run index.py -d mydir -m mymapping.json -i mynewindex.json
        ```


    ## Limitations

*   **JSON Parsing:** The tool relies on the Gemini API returning responses in a JSON-like format. While the code includes error handling and attempts to parse imperfect JSON, there may be cases where the API's output is too malformed to be parsed correctly. This can be due to:
    *   Unescaped newline characters (`\n`)
    *   Unescaped double quotes (`"`)
    *   Control characters (e.g., `\u00a7`)
    *   Unclosed quotes
    These issues can lead to data loss or incomplete results. The tool will log these errors, including the problematic content, to the `app.log` file.  You may need to adjust your prompt or instructions to get more consistent JSON output from the API.