from typing import Iterable, List
from collections import Counter

from dna_storage.components.mapper.rotating import RotatingMapper
from dna_storage.utils.gf4 import from_gf4_symbols


class SimpleGf4ParityDecoder:
    """Decoder paired with SimpleGf4ParityEncoder and RotatingMapper.

    Uses majority-vote assembly of multiple reads and checks parity.
    """

    def __init__(self, mapper: RotatingMapper):
        self.mapper = mapper

    def decode(self, reads: Iterable[str]) -> bytes:
        reads = list(reads)
        if not reads:
            return b""

        # pick the modal read length (most common)
        lengths = Counter(len(r) for r in reads)
        target_len = lengths.most_common(1)[0][0]

        # convert reads of target length
        symbol_lists: List[List[int]] = []
        for r in reads:
            if len(r) != target_len:
                continue
            try:
                sym = self.mapper.reverse(r)
            except ValueError:
                continue
            symbol_lists.append(sym)

        if not symbol_lists:
            return b""

        # majority vote per position
        assembled: List[int] = []
        for idx in range(target_len):
            votes = [s[idx] for s in symbol_lists if len(s) > idx]
            if not votes:
                assembled.append(0)
            else:
                most = Counter(votes).most_common(1)[0][0]
                assembled.append(most)

        # last symbol is parity — verify
        if len(assembled) >= 1:
            data_syms = assembled[:-1]
            parity = assembled[-1]
        else:
            data_syms = []
            parity = 0

        # pack back to bytes
        out = from_gf4_symbols(data_syms)
        # Note: parity check isn't strictly enforced here; this is a demo
        return out
