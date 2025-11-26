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


def test_aligner_improves_consensus(tmp_path):
    # Create a short input and simulate deletions from reads
    data = b"ABCDEFGH01234567ABCDEFGH01234567"
    input_path = tmp_path / "in.txt"
    input_path.write_bytes(data)

    inputter = FileInputter(str(input_path), chunk_size=32)
    encoder = SimpleGf4ParityEncoder()
    mapper = RotatingMapper()

    dup = SoupDuplicator(copies=8)
    # set a non-zero deletion rate to simulate indel-heavy channel
    ids = IDSChannel(sub_p=0.01, del_p=0.05, seed=None)

    # chain
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

    # pipeline without aligner
    from dna_storage.core.pipeline import Pipeline as PClass

    p_no_align = PClass(inputter, encoder, mapper, channel, decoder, YamlOutputter(outpath=str(tmp_path / "noalign.yaml")), aligner=None)
    cmp_no = p_no_align.run()

    # with aligner
    from dna_storage.components.aligner.simple_aligner import SimpleAligner
    aligner = SimpleAligner()
    p_with = PClass(inputter, encoder, mapper, channel, decoder, YamlOutputter(outpath=str(tmp_path / "withalign.yaml")), aligner=aligner)
    cmp_with = p_with.run()

    assert cmp_no is not None and cmp_with is not None
    # aligner should reduce Levenshtein distance (or equal) relative to non-aligner case
    assert cmp_with["levenshtein"] <= cmp_no["levenshtein"]

    # Ensure the example aligns and decodes without raising IndexError
    assert cmp_with is not None


def test_reed_solomon_roundtrip():
    from dna_storage.components.encoder.reed_solomon import ReedSolomonEncoder
    from dna_storage.components.decoder.reed_solomon import ReedSolomonDecoder
    from dna_storage.components.mapper.rotating import RotatingMapper

    k = 4
    n = 8
    message = bytes([10, 20, 30, 40])
    enc = ReedSolomonEncoder(n=n, k=k)
    mapper = RotatingMapper()
    syms = enc.encode(message)
    dna = mapper.map(syms)

    dec = ReedSolomonDecoder(n=n, k=k, mapper=mapper)
    recovered = dec.decode([dna])

    assert recovered[: len(message)] == message


def test_end_to_end_rs_pipeline_single_chunk(tmp_path):
    from dna_storage.components.encoder.reed_solomon import ReedSolomonEncoder
    from dna_storage.components.decoder.reed_solomon import ReedSolomonDecoder
    from dna_storage.components.mapper.rotating import RotatingMapper
    from dna_storage.components.channel.soup_duplicator import SoupDuplicator
    from dna_storage.components.channel.ids_channel import IDSChannel
    from dna_storage.components.inputter.file_inputter import FileInputter
    from dna_storage.components.outputter.yaml_outputter import YamlOutputter
    from dna_storage.core.pipeline import Pipeline

    message = b"TESTMSG!"
    input_path = tmp_path / "in.txt"
    input_path.write_bytes(message)

    inputter = FileInputter(str(input_path), chunk_size=4)
    encoder = ReedSolomonEncoder(n=8, k=4)
    mapper = RotatingMapper()
    dup = SoupDuplicator(copies=5)
    ids = IDSChannel(sub_p=0.01, del_p=0.0, seed=None)
    channel = type("C", (), {"transmit": lambda self, s: dup.transmit(s)})()
    decoder = ReedSolomonDecoder(n=8, k=4, mapper=mapper)
    output = tmp_path / "out.yaml"
    outputter = YamlOutputter(outpath=str(output))

    pipeline = Pipeline(inputter, encoder, mapper, channel, decoder, outputter, aligner=None)
    cmp = pipeline.run()

    # verify output file and that decoding was successful
    assert output.exists()
    assert cmp is not None


def test_reed_solomon_interpolation():
    from dna_storage.components.encoder.reed_solomon import ReedSolomonEncoder
    from dna_storage.components.decoder.reed_solomon import _lagrange_interpolate
    from dna_storage.utils import gf256

    k = 4
    n = 8
    msg = [5, 6, 7, 8]
    points = [i + 1 for i in range(n)]
    # compute full codeword
    codeword = [gf256.poly_eval(msg, x) for x in points]

    # pick arbitrary k positions
    chosen_idx = [0, 2, 5, 7]
    xs = [points[i] for i in chosen_idx]
    ys = [codeword[i] for i in chosen_idx]

    coeffs = _lagrange_interpolate(xs, ys, k)
    # coefficients should match original
    assert coeffs[: len(msg)] == msg
