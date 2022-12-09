from typing import IO
from discord import ApplicationContext


class FailMessagedContext(ApplicationContext):
    fail_message: str


class NamedFile(IO[bytes]):
    name: str
