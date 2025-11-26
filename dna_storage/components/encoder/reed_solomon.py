from typing import List
from dna_storage.utils import gf256
from dna_storage.utils.gf4 import to_gf4_symbols


class ReedSolomonEncoder:
    """Simple RS encoder over GF(256) using evaluation form.

    This encoder treats the input message bytes as polynomial coefficients
    (lowest-degree first) and evaluates the polynomial at n distinct nonzero points
    (1, 2, 3, ...). Returned codeword is a list of GF(256) bytes which we convert
    to GF(4) symbols for downstream mapping.

    Parameters:
    - n: codeword length in bytes
    - k: message length in bytes
    """

    def __init__(self, n: int = 32, k: int = 24):
        assert 1 <= k < n <= 255
        self.n = n
        self.k = k

        # choose evaluation points 1..n (must be nonzero and distinct)
        self.points = [i + 1 for i in range(n)]

    def encode(self, message: bytes) -> List[int]:
        # pad or trim message to length k
        msg = list(message[: self.k])
        if len(msg) < self.k:
            msg += [0] * (self.k - len(msg))

        # evaluate polynomial at each point
        codeword = [gf256.poly_eval(msg, x) for x in self.points]

        # convert bytes to GF4 symbols (2 bits per symbol) for mapping
        # Return a flat list of symbols
        syms = []
        for b in codeword:
            # pack 1 byte into 4 GF4 symbols
            syms.append((b >> 6) & 0x3)
            syms.append((b >> 4) & 0x3)
            syms.append((b >> 2) & 0x3)
            syms.append(b & 0x3)
        return syms
