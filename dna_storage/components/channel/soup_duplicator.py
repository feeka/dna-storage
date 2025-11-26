import random
from typing import Iterable, List


class SoupDuplicator:
    """Given a set of strands, generate multiple duplicated reads (with optional noise added elsewhere).

    This component only duplicates each strand `copies` times and yields them. Low-level errors can be
    applied by other channel components or by combining this with IDSChannel.
    """

    def __init__(self, copies: int = 3):
        self.copies = copies

    def transmit(self, strands: Iterable[str]) -> Iterable[str]:
        for s in strands:
            for _ in range(self.copies):
                # produce an identical copy; channel may wrap/chain this
                yield s
