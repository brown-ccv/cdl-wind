from enum import StrEnum


class GeminiModel(StrEnum):
    """
    Enumeration of available Google Gemini model names (as of approx. April 2025).
    Members behave like strings, representing the model identifier directly.
    """

    # --- Gemini 2.5 ---
    PRO_2_5_PREVIEW = "gemini-2.5-pro-preview-05-06"
    PRO_2_5_FLASH_PREVIEW = "gemini-2.5-flash-preview-05-20"
    # --- Gemini 2.0 ---
    FLASH_2_0 = "gemini-2.0-flash"
    FLASH_2_0_STABLE = "gemini-2.0-flash-001"
    FLASH_LITE_2_0 = "gemini-2.0-flash-lite"
    FLASH_LITE_2_0_STABLE = "gemini-2.0-flash-lite-001"
    PRO_2_0_EXPERIMENTAL = "gemini-2.0-pro-exp-02-05"
    FLASH_THINKING_EXPERIMENTAL = "gemini-2.0-flash-thinking-exp-01-21"
    # --- Gemini 1.5 ---
    PRO_1_5 = "gemini-1.5-pro"
    PRO_1_5_LATEST = "gemini-1.5-pro-latest"
    PRO_1_5_002 = (
        "gemini-1.5-pro-002"  # Using only the latest specific stable for brevity
    )
    FLASH_1_5 = "gemini-1.5-flash"
    FLASH_1_5_LATEST = "gemini-1.5-flash-latest"
    FLASH_1_5_002 = (
        "gemini-1.5-flash-002"  # Using only the latest specific stable for brevity
    )
    FLASH_1_5_8B = "gemini-1.5-flash-8b"
    FLASH_1_5_8B_LATEST = "gemini-1.5-flash-8b-latest"
    FLASH_1_5_8B_001 = "gemini-1.5-flash-8b-001"
    # --- Embedding Models ---
    EMBEDDING_004 = "text-embedding-004"
    EMBEDDING_EXP = "gemini-embedding-exp"
    # --- Other Models ---
    AQA = "models/aqa"
