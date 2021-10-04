import logging
import re
from itertools import chain
from typing import List, TextIO

logging.basicConfig(level=logging.INFO)


def with_logs(chat_id: str, logs=None) -> List[str]:
    if logs is None:
        logs = []

    def read_file_then_close(file: TextIO) -> List[str]:
        content = file.readlines()
        file.close()
        return content

    files: List[TextIO] = logs + [open(f"{chat_id}.txt", "r")]
    return list(chain.from_iterable(map(read_file_then_close, files)))


def sanitize(msg: str) -> str:
    return (
        msg.lower()
        .strip()
        .replace("скажи жопа", "жопа")
        .replace("пидрида", "пидрила")
        .replace("или мойся", "иди мойся")
        .replace("хуй", "x*й")
    )


def valid(msg: str) -> bool:
    pings: re.Pattern = re.compile(r"@[a-z0-9_]+", re.IGNORECASE)
    letters: re.Pattern = re.compile(r"\w", re.IGNORECASE)
    return (
        len(letters.findall(msg)) > 0
        and 0 < len(msg) <= 500
        and len(pings.findall(msg)) == 0
        and not msg.startswith("/")
    )


def clean_chat_data(chat_id) -> List[str]:
    lines: List[str] = list(filter(valid, map(sanitize, with_logs(chat_id))))
    lines_no_dup: List[str] = list(dict.fromkeys(lines))
    logging.debug("Before:", len(lines))
    logging.debug("After:", len(lines_no_dup))
    return lines_no_dup
