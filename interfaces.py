from typing import IO


class NamedFile(IO[bytes]):
    name: str
