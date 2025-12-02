from typing import Iterable, List
from dna_storage.components.mapper.rotating import RotatingMapper
from dna_storage.components.encoder.reed_solomon import ReedSolomonEncoder
from dna_storage.components.decoder.reed_solomon import ReedSolomonDecoder
from dna_storage.utils.gf4 import from_gf4_symbols, to_gf4_symbols


class RSInnerChannel:
    """Channel wrapper that applies a Reed-Solomon inner-code per strand.

    For each incoming DNA strand, we reverse to GF4 symbols, pack to bytes,
    run RS encoder (n,k) producing a longer codeword which is then mapped back
    to DNA and sent to the inner channel. On the receive path we run the RS
    decoder and map recovered bytes back to DNA strings that are returned.

    This is a simple per-strand inner-code, useful to compare where the RS
    protection lives (encoder stage vs channel stage).
    """

    def __init__(self, inner_channel: object, n: int, k: int, mapper: RotatingMapper | None = None):
        assert 1 <= k < n <= 255
        self.inner = inner_channel
        self.n = n
        self.k = k
        self.mapper = mapper or RotatingMapper()

        # create encoder/decoder helpers
        self.rs_enc = ReedSolomonEncoder(n=n, k=k)
        self.rs_dec = ReedSolomonDecoder(n=n, k=k, mapper=self.mapper)

    def transmit(self, strands: Iterable[str]) -> Iterable[str]:
        # encode each incoming strand into an RS-coded strand
        encoded = []
        for s in strands:
            # convert DNA -> GF4 -> bytes
            syms = self.mapper.reverse(s)
            msg = from_gf4_symbols(syms)

            # RS encode (returns GF4 symbols for codeword)
            cw_syms = self.rs_enc.encode(msg)

            # map back to DNA
            encoded_dna = self.mapper.map(cw_syms)
            encoded.append(encoded_dna)

        # send encoded strands through inner channel
        reads = list(self.inner.transmit(encoded))

        # decode reads (RS decoder returns bytes concatenated for successfully decoded reads)
        # We'll run decode on the read set and then split the result into k-byte blocks
        decoded_bytes = self.rs_dec.decode(reads)

        # split into chunks of k bytes and map back to DNA strings
        chunks: List[bytes] = [decoded_bytes[i : i + self.k] for i in range(0, len(decoded_bytes), self.k)]
        out = []
        for chunk in chunks:
            syms = to_gf4_symbols(chunk)
            out.append(self.mapper.map(syms))

        return out
