"""Utility to lowercase JSON content for quicker case-insensitive searches.

This module provides a simple function to read a JSON file, convert its
contents to lowercase, and write the result to another file. It returns the
elapsed time so callers can measure performance during preprocessing."""

from pathlib import Path
import time


def lowercase_json(input_path: str = "result.json", output_path: str = "lower.json") -> float:
    """Lowercase the contents of *input_path* and write them to *output_path*.

    Parameters
    ----------
    input_path:
        Path to the source JSON file.
    output_path:
        Path where the lowercased JSON will be saved.

    Returns
    -------
    float
        The time taken in seconds to process the file.
    """
    start = time.time()
    data = Path(input_path).read_bytes().lower()
    Path(output_path).write_bytes(data)
    return time.time() - start


if __name__ == "__main__":  # pragma: no cover - simple script usage
    print(lowercase_json())
