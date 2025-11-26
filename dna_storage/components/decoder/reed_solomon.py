from typing import Iterable, List
from dna_storage.utils import gf256
from dna_storage.utils.gf4 import from_gf4_symbols


def _lagrange_interpolate(xs: List[int], ys: List[int], degree: int) -> List[int]:
    """Interpolate polynomial of degree < degree from k points (xs, ys) over GF256.

    Returns coefficient list (lowest degree first) of length `degree`.
    """
    # polynomial accumulator
    poly = [0] * degree
    m = len(xs)
    # compute Lagrange interpolation using m points
    for i in range(m):
        xi = xs[i]
        yi = ys[i]

        # numerator polynomial starts as [1]
        num = [1]
        denom = 1

        for j in range(m):
            if j == i:
                continue
            xj = xs[j]
            # multiply numerator by (x - xj); in GF(2^m) (x - xj) = x + xj
            # poly (x - xj) representation (lowest-first) is [xj, 1]
            num = gf256.poly_mul(num, [xj, 1])
            # multiply denom by (xi - xj) which is xi + xj
            denom = gf256.mul(denom, gf256.add(xi, xj))

        # compute scale = yi / denom
        scale = gf256.mul(yi, gf256.inverse(denom))
        term = gf256.poly_scale(num, scale)
        poly = gf256.poly_add(poly, term)

    # trim/pad to degree
    if len(poly) < degree:
        poly += [0] * (degree - len(poly))
    return poly[:degree]
    if len(poly) < degree:
        poly += [0] * (degree - len(poly))
    return poly[:degree]


class ReedSolomonDecoder:
    """Erasure-capable RS decoder for the GF(256) evaluation-based encoder above.

    This decoder expects that each read corresponds to a full codeword (or that
    reads are already consensus-cleaned) and decodes the original message by
    interpolating the message polynomial from any k correct evaluations.
    """

    def __init__(self, n: int = 32, k: int = 24, mapper=None):
        assert 1 <= k < n <= 255
        self.n = n
        self.k = k
        self.points = [i + 1 for i in range(n)]
        self.mapper = mapper

    def decode(self, reads: Iterable[str]) -> bytes:
        reads = list(reads)
        if not reads:
            return b""

        results: List[bytes] = []

        for r in reads:
            if self.mapper is not None:
                # convert DNA to GF4 symbols then to byte array
                syms = self.mapper.reverse(r)
                codeword_bytes = list(from_gf4_symbols(syms))
            else:
                # assume read is raw bytes-like (not typical)
                codeword_bytes = list(r)

            # collect points available
            xs = []
            ys = []
            for idx, val in enumerate(codeword_bytes):
                if val is None:
                    continue
                xs.append(self.points[idx])
                ys.append(val)
                if len(xs) >= self.k:
                    break

            if len(xs) < self.k:
                # cannot reconstruct this read -> skip
                continue

            # interpolate polynomial of degree < k
            coeffs = _lagrange_interpolate(xs, ys, self.k)
            # pack coefficients into bytes
            out = bytes([c & 0xFF for c in coeffs])
            results.append(out)

        return b"".join(results)
