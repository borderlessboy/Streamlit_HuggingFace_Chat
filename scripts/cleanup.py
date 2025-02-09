#!/usr/bin/env python3
"""Script to clean up cache and temporary files from the project."""

import os
import shutil
from pathlib import Path
from typing import List, Set

# Directories to remove
DIRS_TO_REMOVE: Set[str] = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
    ".cache",
    ".streamlit",
    "redis-data",
    "htmlcov",
    "build",
    "dist",
    "*.egg-info",
}

# Files to remove
FILES_TO_REMOVE: Set[str] = {
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.rdb",
    ".coverage",
    "*.swp",
    "*.swo",
    ".DS_Store",
}


def find_files_to_remove(start_path: Path = Path(".")) -> List[Path]:
    """Find all files that match the patterns to remove."""
    files_to_remove: List[Path] = []

    for pattern in FILES_TO_REMOVE:
        files_to_remove.extend(start_path.rglob(pattern))

    return files_to_remove


def find_dirs_to_remove(start_path: Path = Path(".")) -> List[Path]:
    """Find all directories that match the patterns to remove."""
    dirs_to_remove: List[Path] = []

    for dir_name in DIRS_TO_REMOVE:
        dirs_to_remove.extend(start_path.rglob(dir_name))

    return dirs_to_remove


def cleanup() -> None:
    """Remove all cache files and directories."""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("🧹 Starting cleanup process...")

    # Remove files
    files = find_files_to_remove()
    for file in files:
        try:
            file.unlink()
            print(f"✓ Removed file: {file}")
        except Exception as e:
            print(f"✗ Failed to remove file {file}: {e}")

    # Remove directories
    dirs = find_dirs_to_remove()
    for dir_path in dirs:
        try:
            shutil.rmtree(dir_path)
            print(f"✓ Removed directory: {dir_path}")
        except Exception as e:
            print(f"✗ Failed to remove directory {dir_path}: {e}")

    print("\n🎉 Cleanup completed!")
    print(f"Removed {len(files)} files and {len(dirs)} directories.")


if __name__ == "__main__":
    cleanup()
