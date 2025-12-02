from typing import Iterable, List

from dna_storage.core.components import (
    Inputter,
    Encoder,
    Mapper,
    Channel,
    Decoder,
    Outputter,
    Aligner,
)


class Pipeline:
    """Orchestrate the flow from input -> encode -> map -> channel -> decode -> output.

    This class keeps things simple so users can swap implementations for each stage.
    """

    def __init__(
        self,
        inputter: Inputter,
        encoder: Encoder,
        mapper: Mapper,
        channel: Channel,
        decoder: Decoder,
        outputter: Outputter,
        aligner: Aligner | None = None,
        oligo_len: int = 150,
        overhead: int = 40,
    ) -> None:
        self.inputter = inputter
        self.encoder = encoder
        self.mapper = mapper
        self.channel = channel
        self.decoder = decoder
        self.outputter = outputter
        self.aligner = aligner
        # optional oligo sizing check (defaults chosen to practical values)
        self.oligo_len = oligo_len
        self.overhead = overhead

        # If an encoder exposes 'n' (codeword length in bytes), check whether
        # it fits typical oligo parameters and print a warning if not.
        try:
            from dna_storage.utils.oligo_utils import recommend_rs_parameters

            if hasattr(encoder, "n"):
                rec = recommend_rs_parameters(self.oligo_len, self.overhead)
                n_max = rec.get("n_max", 0)
                enc_n = getattr(encoder, "n")
                if enc_n > n_max:
                    print(
                        f"[pipeline warning] encoder.n={enc_n} may be too large for oligo_len={self.oligo_len} (n_max={n_max}); consider lowering n or increasing oligo_len/ reducing overhead"
                    )
        except Exception:
            # non-fatal: utilities may not be available or encoder is custom
            pass

    def run(self) -> object:
        # Read messages
        messages = list(self.inputter.read())

        # keep a copy of the original concatenated payload so we can trim
        # any decoder-side padding (decoders often reconstruct fixed k-byte
        # chunks and may produce a slightly longer stream).
        original_all = b"".join(messages)

        # Encode each message into codewords
        codewords = [self.encoder.encode(m) for m in messages]

        # Map codewords to DNA strings
        strands = [self.mapper.map(cw) for cw in codewords]

        # Transmit through channel
        reads = list(self.channel.transmit(strands))

        # optionally run an aligner if the pipeline provides one
        try:
            # aligner may or may not exist on the pipeline instance
            aligner = getattr(self, "aligner", None)
        except Exception:
            aligner = None

        if aligner is not None:
            # If there are multiple original strands we try grouping reads by
            # strand assuming the channel preserved order and produced roughly
            # equal copies per strand (eg SoupDuplicator). Otherwise fall back
            # to aligning all reads together.
            if len(strands) > 0 and len(reads) >= len(strands) and len(reads) % len(strands) == 0:
                copies = len(reads) // len(strands)
                grouped = []
                for i in range(len(strands)):
                    seg = reads[i * copies : (i + 1) * copies]
                    # aligner.align returns an iterable of consensus reads for the group
                    out = list(aligner.align(seg))
                    if out:
                        grouped.append(out[0])
                reads = grouped
            else:
                # align all reads together (legacy behaviour)
                reads = list(aligner.align(reads))

        # Decode back to bytes
        decoded = self.decoder.decode(reads)

        # Trim decoder output to the original payload length; some decoders
        # (eg. RS) always reconstruct fixed k-byte blocks and will produce
        # extra padding for the last block. Trim to match the original input
        # bytes for fair comparison and downstream writing.
        try:
            decoded = decoded[: len(original_all)]
        except Exception:
            # if slicing fails for some reason, keep original decoded
            pass

        # Try comparing with original (concatenate original messages)
        try:
            from dna_storage.utils.compare import compare_bytes, pretty_report

            # original_all already computed earlier
            cmp = compare_bytes(original_all, decoded)
            report = pretty_report(original_all, decoded)
        except Exception:
            cmp = None
            report = "(compare failed)"

        # Output decoded payload
        self.outputter.write(decoded)

        # Print comparison summary to stdout (only when outputter isn't silenced)
        try:
            outpath = getattr(self.outputter, "outpath", None)
        except Exception:
            outpath = None
        if outpath is None:
            print("--- compare report:\n" + report)
        return cmp
