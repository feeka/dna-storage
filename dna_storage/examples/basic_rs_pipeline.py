import os

from dna_storage.core.pipeline import Pipeline
from dna_storage.components.inputter.file_inputter import FileInputter
from dna_storage.components.encoder.reed_solomon import ReedSolomonEncoder
from dna_storage.components.mapper.rotating import RotatingMapper
from dna_storage.components.channel.soup_duplicator import SoupDuplicator
from dna_storage.components.channel.ids_channel import IDSChannel
from dna_storage.components.aligner.simple_aligner import SimpleAligner
from dna_storage.components.decoder.reed_solomon import ReedSolomonDecoder
from dna_storage.utils.oligo_utils import recommend_rs_parameters, pretty_recommendation
from dna_storage.components.outputter.yaml_outputter import YamlOutputter


EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), "example_input.txt")


def make_example_file():
    if not os.path.exists(EXAMPLE_PATH):
        with open(EXAMPLE_PATH, "w", encoding="utf-8") as fh:
            fh.write("Simple")


class ChainedChannel:
    def __init__(self, *layers):
        self.layers = layers

    def transmit(self, strands):
        out = strands
        for layer in self.layers:
            out = layer.transmit(out)
        return out


def main():
    #make_example_file()

    # Oligo sizing / RS parameter recommendation
    oligo_len = 100
    overhead = 20
    print(pretty_recommendation(oligo_len, overhead))
    rec = recommend_rs_parameters(oligo_len, overhead)
    n = rec["recommended"]["n"]
    k = rec["recommended"]["k"]

    # choose chunk_size to match k (bytes per message -> one RS block)
    inputter = FileInputter(EXAMPLE_PATH, chunk_size=k)
    encoder = ReedSolomonEncoder(n=n, k=k)
    mapper = RotatingMapper()

    # compose channel: duplicate copies per strand then apply IDS mutations
    dup = SoupDuplicator(copies=1000)
    ids = IDSChannel(sub_p=0.1, del_p=0.05, seed=2020)
    channel = ChainedChannel(dup, ids)

    aligner = SimpleAligner()
    decoder = ReedSolomonDecoder(n=n, k=k, mapper=mapper)
    outputter = YamlOutputter("output.yaml")

    pipeline = Pipeline(inputter, encoder, mapper, channel, decoder, outputter, aligner=aligner)
    pipeline.run()
    print("Original message written to YAML output.")


if __name__ == "__main__":
    main()
