import re
from itertools import chain


def with_logs() -> list:
    def read_file_then_close(file):
        content = file.readlines()
        file.close()
        return content

    files = [open(f"part{i}.log", "r", encoding="utf8") for i in range(1, 7)] + [open("-1001390493223.txt", "r")]
    files = map(read_file_then_close, files)
    return list(chain.from_iterable(files))


def clean_msg(msg: str) -> str:
    return (
        msg.lower().strip()
            .replace("скажи жопа", "жопа")
            .replace("пидрида", "пидрила")
            .replace("или мойся", "иди мойся")
    )


def filter_msg(msg: str) -> bool:
    pings = re.compile(r"@[a-z0-9_]+", re.IGNORECASE)
    letters = re.compile(r"[a-zа-я0-9]", re.IGNORECASE)
    return (
            len(letters.findall(msg)) > 1 and
            len(msg) > 0 and
            len(pings.findall(msg)) == 0
    )


def clean():
    lines = list(
        filter(
            filter_msg,
            map(
                clean_msg,
                with_logs()
            )
        )
    )
    lines_no_dup = list(dict.fromkeys(lines))
    print(lines_no_dup)
    print("Before:", len(lines))
    print("After:", len(lines_no_dup))
    return lines_no_dup


if __name__ == '__main__':
    with open("-1001390493223_clean.txt", "w") as f:
        f.write("\n".join(clean()) + "\n")