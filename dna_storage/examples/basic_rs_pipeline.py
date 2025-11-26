import os

from dna_storage.core.pipeline import Pipeline
from dna_storage.components.inputter.file_inputter import FileInputter
from dna_storage.components.encoder.dna_rs_gf4 import SimpleGf4ParityEncoder
from dna_storage.components.mapper.rotating import RotatingMapper
from dna_storage.components.channel.soup_duplicator import SoupDuplicator
from dna_storage.components.channel.ids_channel import IDSChannel
from dna_storage.components.decoder.dna_rs_gf4_decoder import SimpleGf4ParityDecoder
from dna_storage.components.outputter.yaml_outputter import YamlOutputter


EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), "example_input.txt")


def make_example_file():
    if not os.path.exists(EXAMPLE_PATH):
        with open(EXAMPLE_PATH, "w", encoding="utf-8") as fh:
            fh.write("Hello from dna_storage example pipeline!\nThis demonstrates a toy GF(4) parity encoder and simple channel.\n")


class ChainedChannel:
    def __init__(self, *layers):
        self.layers = layers

    def transmit(self, strands):
        out = strands
        for layer in self.layers:
            out = layer.transmit(out)
        return out


def main():
    make_example_file()

    inputter = FileInputter(EXAMPLE_PATH, chunk_size=32)
    encoder = SimpleGf4ParityEncoder()
    mapper = RotatingMapper()

    # compose channel: duplicate copies per strand then apply IDS mutations
    dup = SoupDuplicator(copies=5)
    ids = IDSChannel(sub_p=0.01, del_p=0.005, seed=2025)
    channel = ChainedChannel(dup, ids)

    decoder = SimpleGf4ParityDecoder(mapper)
    outputter = YamlOutputter()

    pipeline = Pipeline(inputter, encoder, mapper, channel, decoder, outputter)
    pipeline.run()


if __name__ == "__main__":
    main()
