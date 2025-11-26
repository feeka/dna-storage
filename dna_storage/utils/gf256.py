"""GF(256) arithmetic utilities using AES-style primitive 0x11d.

Provides add (xor), mul, div, pow, inverse, and helpers for polynomials.
"""
from typing import List

# primitive polynomial for GF(2^8)
PRIM = 0x11d

# build log/antilog tables for GF(256)
EXP = [0] * 512
LOG = [0] * 256

def _build_tables():
    x = 1
    for i in range(0, 255):
        EXP[i] = x
        LOG[x] = i
        x <<= 1
        if x & 0x100:
            x ^= PRIM
    # duplicate for overflow handling
    for i in range(255, 512):
        EXP[i] = EXP[i - 255]


_build_tables()


def add(a: int, b: int) -> int:
    return a ^ b


def mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return EXP[LOG[a] + LOG[b]]


def div(a: int, b: int) -> int:
    if b == 0:
        raise ZeroDivisionError()
    if a == 0:
        return 0
    return EXP[(LOG[a] - LOG[b]) % 255]


def pow_(a: int, power: int) -> int:
    if a == 0:
        return 0
    return EXP[(LOG[a] * power) % 255]


def inverse(a: int) -> int:
    if a == 0:
        raise ZeroDivisionError()
    return EXP[255 - LOG[a]]


def poly_eval(poly: List[int], x: int) -> int:
    """Evaluate polynomial (coeff list lowest->highest) at point x in GF256."""
    y = 0
    # Horner
    for coeff in reversed(poly):
        y = mul(y, x)
        y = add(y, coeff)
    return y


def poly_scale(poly: List[int], scalar: int) -> List[int]:
    return [mul(c, scalar) for c in poly]


def poly_add(p1: List[int], p2: List[int]) -> List[int]:
    # add coefficients
    n = max(len(p1), len(p2))
    out = [0] * n
    for i in range(n):
        a = p1[i] if i < len(p1) else 0
        b = p2[i] if i < len(p2) else 0
        out[i] = add(a, b)
    # trim trailing zeros
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def poly_mul(p1: List[int], p2: List[int]) -> List[int]:
    if not p1 or not p2:
        return [0]
    out = [0] * (len(p1) + len(p2) - 1)
    for i, a in enumerate(p1):
        if a == 0:
            continue
        for j, b in enumerate(p2):
            if b == 0:
                continue
            out[i + j] = add(out[i + j], mul(a, b))
    # trim
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out
