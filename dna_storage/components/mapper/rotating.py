from typing import List

# This mapper deterministically maps GF4 symbols (0..3) to bases A/C/G/T
# The mapping rotates depending on the previous base to avoid homopolymers often.

BASES = ["A", "C", "G", "T"]


class RotatingMapper:
    def __init__(self):
        pass

    def map(self, symbols: List[int]) -> str:
        out = []
        prev_idx = 0
        for s in symbols:
            # rotate mapping by prev_idx to reduce repeats
            base = BASES[(s + prev_idx) % 4]
            out.append(base)
            prev_idx = (prev_idx + 1) % 4
        return "".join(out)

    def reverse(self, dna: str) -> List[int]:
        symbols = []
        prev_idx = 0
        for b in dna:
            # find base index
            idx = BASES.index(b)
            s = (idx - prev_idx) % 4
            symbols.append(s)
            prev_idx = (prev_idx + 1) % 4
        return symbols
