import tempfile
import os

from dna_storage.utils.gf4 import to_gf4_symbols, from_gf4_symbols

from dna_storage.core.pipeline import Pipeline
from dna_storage.components.inputter.file_inputter import FileInputter
from dna_storage.components.encoder.dna_rs_gf4 import SimpleGf4ParityEncoder
from dna_storage.components.mapper.rotating import RotatingMapper
from dna_storage.components.channel.soup_duplicator import SoupDuplicator
from dna_storage.components.channel.ids_channel import IDSChannel
from dna_storage.components.decoder.dna_rs_gf4_decoder import SimpleGf4ParityDecoder
from dna_storage.components.outputter.yaml_outputter import YamlOutputter


def test_gf4_roundtrip():
    b = b"abcd1234"
    syms = to_gf4_symbols(b)
    out = from_gf4_symbols(syms)
    assert out == b


def test_basic_pipeline_roundtrip(tmp_path):
    # create input file
    data = b"small message for pipeline test"
    input_path = tmp_path / "in.txt"
    input_path.write_bytes(data)

    out_path = tmp_path / "out.yaml"

    inputter = FileInputter(str(input_path), chunk_size=32)
    encoder = SimpleGf4ParityEncoder()
    mapper = RotatingMapper()
    dup = SoupDuplicator(copies=5)
    ids = IDSChannel(sub_p=0.01, del_p=0.0, seed=42)
    # a small chain
    class Chain:
        def __init__(self, layers):
            self.layers = layers

        def transmit(self, strands):
            out = strands
            for l in self.layers:
                out = l.transmit(out)
            return out

    channel = Chain([dup, ids])
    decoder = SimpleGf4ParityDecoder(mapper)
    outputter = YamlOutputter(outpath=str(out_path))

    pipeline = Pipeline(inputter, encoder, mapper, channel, decoder, outputter)
    cmp = pipeline.run()

    assert out_path.exists()
    txt = out_path.read_text(encoding="utf-8")
    assert "small message for pipeline test" in txt

    # run-time comparison returned useful information
    assert isinstance(cmp, dict)
    assert cmp["orig_len"] == len(data)
    assert "levenshtein" in cmp


def test_compare_utils():
    from dna_storage.utils.compare import compare_bytes

    a = b"hello"
    b2 = b"hello"
    c = b"hell0"

    r1 = compare_bytes(a, b2)
    assert r1["equal"] is True
    assert r1["levenshtein"] == 0

    r2 = compare_bytes(a, c)
    assert r2["equal"] is False
    assert r2["levenshtein"] >= 1
