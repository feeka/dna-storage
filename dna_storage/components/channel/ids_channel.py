import random
from typing import Iterable


class IDSChannel:
    """Basic substitution/insertion/deletion (IDS) channel for DNA reads.

    For now it supports substitutions and deletions (no insertions for simplicity).
    """

    def __init__(self, sub_p: float = 0.02, del_p: float = 0.01, seed: int | None = None):
        self.sub_p = sub_p
        self.del_p = del_p
        if seed is not None:
            random.seed(seed)

    def _mutate(self, s: str) -> str:
        out = []
        for ch in s:
            if random.random() < self.del_p:
                # delete this base
                continue
            if random.random() < self.sub_p:
                # substitute with another base
                choices = [b for b in "ACGT" if b != ch]
                ch = random.choice(choices)
            out.append(ch)
        return "".join(out)

    def transmit(self, strands: Iterable[str]) -> Iterable[str]:
        for s in strands:
            yield self._mutate(s)
