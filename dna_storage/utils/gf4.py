"""Small GF(4) arithmetic utilities for prototyping.

Representation:
- Elements as integers 0..3 corresponding to 0, 1, a, a+1 when constructed over GF(2) with
  primitive polynomial x^2 + x + 1.

Addition = XOR
Multiplication = precomputed table
"""

from typing import List

# addition in GF4 is XOR
def add(a: int, b: int) -> int:
    return a ^ b

# multiplication table using basis where a^2 = a + 1
MUL = [
    [0, 0, 0, 0],
    [0, 1, 2, 3],
    [0, 2, 3, 1],
    [0, 3, 1, 2],
]

def mul(a: int, b: int) -> int:
    return MUL[a][b]

INV = [None, 1, 3, 2]  # inverses: 1->1, 2->3, 3->2

def inverse(a: int) -> int:
    if a == 0:
        raise ZeroDivisionError("0 has no inverse in GF(4)")
    return INV[a]

def vec_add(v1: List[int], v2: List[int]) -> List[int]:
    return [add(a, b) for a, b in zip(v1, v2)]

def to_gf4_symbols(data: bytes) -> List[int]:
    """Convert bytes into list of GF4 symbols (2 bits per symbol)."""
    symbols: List[int] = []
    for b in data:
        # high 2 bits then low 2 bits repeatedly
        symbols.append((b >> 6) & 0x3)
        symbols.append((b >> 4) & 0x3)
        symbols.append((b >> 2) & 0x3)
        symbols.append(b & 0x3)
    return symbols

def from_gf4_symbols(symbols: List[int]) -> bytes:
    """Pack 4 GF4 symbols into a byte (2 bits each). If len(symbols) not multiple of 4, pad with zeros."""
    out = bytearray()
    s = symbols[:]
    # pad
    while len(s) % 4 != 0:
        s.append(0)
    for i in range(0, len(s), 4):
        b = (s[i] << 6) | (s[i+1] << 4) | (s[i+2] << 2) | s[i+3]
        out.append(b)
    return bytes(out)
