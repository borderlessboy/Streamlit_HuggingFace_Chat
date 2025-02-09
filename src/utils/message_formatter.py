"""Message formatting utilities that match enhanced-inference.py style."""

import re
from typing import List

from utils.logger import setup_logger

logger = setup_logger(__name__)


def clean_code_content(code: str) -> str:
    """Clean and format code content to match Claude.ai style."""
    # Remove artifacts
    code = re.sub(r",?\[object Object\]", "", code)

    # Split into lines
    lines = [line.rstrip() for line in code.split("\n")]

    # Remove empty lines and comma-only lines
    lines = [line for line in lines if line.strip() and not line.strip() == ","]

    # Track indentation
    formatted_lines = []
    current_indent = 0

    for line in lines:
        stripped = line.strip()

        # Handle empty lines
        if not stripped:
            formatted_lines.append("")
            continue

        # Increase indent after ':' unless it's a docstring
        if stripped.endswith(":") and not (
            stripped.startswith('"""') or stripped.startswith("'''")
        ):
            formatted_lines.append("    " * current_indent + stripped)
            current_indent += 1
            continue

        # Handle control flow statements
        if stripped.startswith(("elif ", "else:", "except:", "finally:")):
            current_indent = max(0, current_indent - 1)
            formatted_lines.append("    " * current_indent + stripped)
            if stripped.endswith(":"):
                current_indent += 1
            continue

        # Add regular line with current indentation
        formatted_lines.append("    " * current_indent + stripped)

    return "\n".join(formatted_lines)


def format_code_in_message(content: str) -> str:
    """Format code blocks with proper styling."""
    lines = content.split("\n")
    formatted_lines: List[str] = []
    in_code_block = False
    current_code_block: List[str] = []
    code_block_count = 0
    code_language = ""

    def clean_code_content(code: str) -> str:
        """Clean code content by removing artifacts and normalizing format."""
        # Remove [object Object] artifacts
        code = re.sub(r",?\s*\[object Object\],?\s*", "\n", code)
        code = re.sub(r"\[object Object\]", "", code)

        # Remove trailing/leading commas
        code = re.sub(r",\s*$", "", code, flags=re.MULTILINE)
        code = re.sub(r"^\s*,", "", code, flags=re.MULTILINE)

        # Remove extra blank lines
        code = re.sub(r"\n\s*\n\s*\n+", "\n\n", code)

        # Clean trailing whitespace
        code = "\n".join(line.rstrip() for line in code.splitlines())

        return code.strip()

    def normalize_indentation(code_lines: List[str]) -> str:
        """Normalize indentation of code block lines."""
        if not code_lines:
            return ""

        # Clean each line of [object Object] and empty lines before processing indentation
        code_lines = [
            line
            for line in code_lines
            if not line.strip() == "[object Object]"
            and line.strip()  # Remove completely empty lines between code
        ]

        if not code_lines:  # If all lines were removed, return empty string
            return ""

        # Find the minimum indentation level
        min_indent = float("inf")
        for line in code_lines:
            if line.strip():  # Only consider non-empty lines
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)

        if min_indent == float("inf"):
            min_indent = 0

        # Remove the common indentation from all lines
        normalized_lines = []
        for line in code_lines:
            if line.strip():  # Only process non-empty lines
                normalized_lines.append(line[min_indent:])

        return "\n".join(normalized_lines)

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("```"):
            if in_code_block:
                # End code block
                code = normalize_indentation(current_code_block)
                code = clean_code_content(code)

                # Escape HTML special characters
                code = (
                    code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                )

                language_class = (
                    f"language-{code_language}"
                    if code_language
                    else "language-plaintext"
                )

                formatted_lines.append(
                    f'<div class="code-block" data-language="{code_language or "text"}">'
                    f'<pre class="{language_class}"><code class="{language_class}">{code}</code></pre>'
                    f"</div>"
                )
                current_code_block = []
                in_code_block = False
                code_block_count += 1
                code_language = ""
            else:
                in_code_block = True
                code_language = stripped_line.replace("```", "").strip().lower()
                if code_language == "c++":
                    code_language = "cpp"
        elif in_code_block:
            if stripped_line != "[object Object]":
                current_code_block.append(line)
        else:
            if "`" in line:
                line = re.sub(
                    r"`([^`]+)`",
                    lambda m: f'<code class="inline-code">{m.group(1).replace("<", "&lt;").replace(">", "&gt;")}</code>',
                    line,
                )
            formatted_lines.append(line)

    return "\n".join(formatted_lines)
