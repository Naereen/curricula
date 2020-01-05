import os
import tempfile
from pathlib import Path
from typing import Optional

from . import process
from .files import delete_file

__all__ = ("count",)


def read_last_line(path: Path) -> str:
    """IR count appears at the end of the callgrind output."""

    with path.open("rb") as file:
        file.seek(0)
        file.seek(-2, os.SEEK_END)
        while file.read(1) != b"\n":
            file.seek(-2, os.SEEK_CUR)
        return file.readlines()[-1].decode()


def count(*args: str, stdin: bytes = None, timeout: float = None) -> Optional[int]:
    """Run callgrind on the program and return IR count."""

    _, out_path = tempfile.mkstemp(dir=Path().absolute())
    out_path = Path(out_path)
    process.run(
        "valgrind",
        "--tool=callgrind",
        f"--callgrind-out-file={out_path.parts[-1]}",
        *args,
        stdin=stdin,
        timeout=timeout)
    if out_path.exists():
        result = int(read_last_line(out_path).rsplit(maxsplit=1)[1])
        delete_file(out_path)
        return result
    return None