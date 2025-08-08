"""Utility helpers for working with exported Telegram messages."""

from typing import List, Sequence

import orjson
from timeit import default_timer as timer


def load_messages(path: str = "./result.json"):
    """Load raw message objects from a JSON export."""
    with open(path, "rb") as fin:
        data = fin.read()
        pj = orjson.loads(data)
        return pj["messages"]


def time_elapsed(start_time: float) -> str:
    """Return milliseconds elapsed since *start_time* as a string."""
    return f"{(timer() - start_time) * 1000:.2f}"


def extract_text(element) -> str:
    """Recursively extract text from nested Telegram JSON structures."""
    if isinstance(element, list):
        return "".join(map(extract_text, element))
    if isinstance(element, dict) and "text" in element:
        return extract_text(element["text"])
    if isinstance(element, str):
        return element
    return ""


def get_messages(path: str = "./result.json") -> List[str]:
    """Return a list of message texts from the export."""
    messages = load_messages(path)
    extracted_messages = [
        {"id": message["id"], "text": extract_text(message)} for message in messages
    ]
    return [extract_text(message) for message in extracted_messages]


def list_builder(indices: Sequence[int]) -> str:
    """Format a sequence of message IDs as a bulleted list."""
    indices = list(indices)
    string = ""
    len_indices = len(indices)
    if len_indices > 1:
        for n, x in enumerate(indices):
            y = "[{}](https://t.me/c/1083858375/{})".format(x, x)
            if n < len_indices - 1:
                string += "├ " + y + "\n"
            else:
                string += "└ " + y
    else:
        string += "└ " + str(indices[0])
    return string
