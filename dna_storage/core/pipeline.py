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
    ) -> None:
        self.inputter = inputter
        self.encoder = encoder
        self.mapper = mapper
        self.channel = channel
        self.decoder = decoder
        self.outputter = outputter
        self.aligner = aligner

    def run(self) -> object:
        # Read messages
        messages = list(self.inputter.read())

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

        # Try comparing with original (concatenate original messages)
        try:
            from dna_storage.utils.compare import compare_bytes, pretty_report

            original_all = b"".join(messages)
            cmp = compare_bytes(original_all, decoded)
            report = pretty_report(original_all, decoded)
        except Exception:
            cmp = None
            report = "(compare failed)"

        # Output decoded payload
        self.outputter.write(decoded)

        # Print comparison summary to stdout and return details to caller
        print("--- compare report:\n" + report)
        return cmp
