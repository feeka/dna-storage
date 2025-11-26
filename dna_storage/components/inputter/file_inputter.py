from typing import Iterable


class FileInputter:
    """Read a file and yield messages as bytes chunks.

    Parameters:
    - path: path to file
    - chunk_size: bytes per message
    """

    def __init__(self, path: str, chunk_size: int = 16):
        self.path = path
        self.chunk_size = chunk_size

    def read(self) -> Iterable[bytes]:
        with open(self.path, "rb") as fh:
            while True:
                chunk = fh.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk
