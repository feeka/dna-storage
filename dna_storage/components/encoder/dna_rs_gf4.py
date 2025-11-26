from typing import List
from dna_storage.utils.gf4 import to_gf4_symbols, add


class SimpleGf4ParityEncoder:
    """Toy encoder that converts bytes -> GF4 symbols and appends a single parity symbol.

    This is NOT a full RS encoder; it's a simple parity-based (1-symbol) ECC to illustrate the framework.
    """

    def encode(self, message: bytes) -> List[int]:
        symbols = to_gf4_symbols(message)
        parity = 0
        for s in symbols:
            parity = add(parity, s)
        symbols.append(parity)
        return symbols
