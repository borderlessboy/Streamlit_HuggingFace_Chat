"""Application configuration and settings."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Version information
VERSION = "1.2.0"
AUTHOR = "Borderlessboy"
LICENSE = "MIT"
COPYRIGHT = f"Copyright {datetime.now().year} {AUTHOR}"
DESCRIPTION = (
    "A Streamlit-based chat interface for the HuggingFace Inference API "
    "with advanced features"
)
REPOSITORY = "https://github.com/borderlessboy/huggingface-inference-chat"


# Cache settings
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", "1000"))
MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", "10"))
CACHE_VERSION = "v1.0.0"

# API settings
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30"))
DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-32B-Instruct"
HUGGING_FACE_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN")

# Redis settings
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "decode_responses": True,
}

# File handling settings
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(5 * 1024 * 1024)))
SUPPORTED_FILE_TYPES = {
    "txt",
    "py",
    "js",
    "java",
    "cpp",
    "h",
    "c",
    "css",
    "html",
    "json",
    "yaml",
    "yml",
    "md",
    "rs",
    "go",
    "ts",
    "jsx",
    "tsx",
    "sql",
    "sh",
    "bash",
    "r",
    "php",
    "rb",
    "swift",
    "kt",
    "scala",
}
SUPPORTED_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii"]

# Model parameters
DEFAULT_MODEL_PARAMS: Dict[str, Any] = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 1024,
    "rep_penalty": 1.1,
    "do_sample": True,
    "return_full_text": False,
}
