"""File handling utilities."""

from typing import Any, Optional

from config.settings import MAX_FILE_SIZE, SUPPORTED_ENCODINGS, SUPPORTED_FILE_TYPES
from utils.logger import setup_logger

logger = setup_logger(__name__)


def process_uploaded_file(uploaded_file: Any) -> str:
    """Process an uploaded file and return its contents.

    Args:
        uploaded_file: The uploaded file object

    Returns:
        str: Formatted file contents or error message
    """
    try:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension not in SUPPORTED_FILE_TYPES:
            logger.error("Unsupported file type: %s", file_extension)
            return (
                f"Error: Unsupported file type '{file_extension}'. "
                f"Supported types: {', '.join(sorted(SUPPORTED_FILE_TYPES))}"
            )

        if not check_file_size(uploaded_file):
            return "Error: File size exceeds 5MB limit."

        file_content = read_file_content(uploaded_file)
        if not file_content:
            return "Error: Unable to read file contents."

        return format_file_content(file_content, file_extension)

    except Exception as e:
        logger.error("Error processing file: %s - %s", uploaded_file.name, str(e))
        return f"Error processing file: {str(e)}"


def check_file_size(uploaded_file: Any) -> bool:
    """Check if file size is within limits."""
    uploaded_file.seek(0, 2)
    file_size = uploaded_file.tell()
    uploaded_file.seek(0)

    if file_size > MAX_FILE_SIZE:
        logger.error("File too large: %s (%d bytes)", uploaded_file.name, file_size)
        return False
    return True


def read_file_content(uploaded_file: Any) -> Optional[str]:
    """Read file content with multiple encoding attempts."""
    content = uploaded_file.read()

    for encoding in SUPPORTED_ENCODINGS:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue

    logger.error("Failed to decode file with any encoding: %s", uploaded_file.name)
    return None


def format_file_content(content: str, extension: str) -> str:
    """Format file content for display."""
    return f"```{extension}\n{content}\n```"
