"""
Generate safe dummy files for ransomware simulation testing.

This script creates sample files only inside the local "test_folder"
directory. It is intended for educational use in a controlled sandbox.

Run:
    python generate_test_files.py
"""

from __future__ import annotations

import random
from datetime import datetime
from pathlib import Path


# Project-local sandbox folder. The script only writes inside this directory.
TEST_FOLDER = Path(__file__).resolve().parent / "test_folder"

# Required names plus extra files to ensure we create at least 10 files.
FILE_NAMES = [
    "test1.txt",
    "test2.txt",
    "test3.txt",
    "sample1.log",
    "demo1.doc",
    "image1.jpg",  # Text content on purpose for safe simulation testing.
    "notes_a.txt",
    "notes_b.txt",
    "report1.csv",
    "session.json",
    "audit.tmp",
    "readme_test.md",
]

SAMPLE_LINES = [
    "This is safe test data for sandbox cybersecurity practice.",
    "Hybrid ransomware simulation project dummy content.",
    "No real or sensitive files are used in this environment.",
    "Event sample: file created for training and testing.",
    "Log sample: normal write operation in test folder.",
]


def build_file_content(file_name: str) -> str:
    """Create small random text content for each dummy file."""
    line_count = random.randint(3, 7)
    selected = [random.choice(SAMPLE_LINES) for _ in range(line_count)]
    return (
        f"File: {file_name}\n"
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}\n"
        f"Sandbox: {TEST_FOLDER.name}\n\n"
        + "\n".join(selected)
        + "\n"
    )


def main() -> None:
    # Create the sandbox folder automatically if it does not already exist.
    TEST_FOLDER.mkdir(parents=True, exist_ok=True)

    created_count = 0

    for name in FILE_NAMES:
        path = TEST_FOLDER / name
        path.write_text(build_file_content(name), encoding="utf-8")
        created_count += 1

    print(f"Created {created_count} test files in: {TEST_FOLDER}")


if __name__ == "__main__":
    main()
