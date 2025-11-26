from typing import Iterable, List

from dna_storage.core.components import (
    Inputter,
    Encoder,
    Mapper,
    Channel,
    Decoder,
    Outputter,
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
    ) -> None:
        self.inputter = inputter
        self.encoder = encoder
        self.mapper = mapper
        self.channel = channel
        self.decoder = decoder
        self.outputter = outputter

    def run(self) -> object:
        # Read messages
        messages = list(self.inputter.read())

        # Encode each message into codewords
        codewords = [self.encoder.encode(m) for m in messages]

        # Map codewords to DNA strings
        strands = [self.mapper.map(cw) for cw in codewords]

        # Transmit through channel
        reads = list(self.channel.transmit(strands))

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
