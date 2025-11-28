import io
import sys

from dna_storage.core.pipeline import Pipeline


class DummyInput:
    def read(self):
        return [b"a"]


class DummyEncoder:
    def __init__(self):
        # create artificially large codeword size
        self.n = 100

    def encode(self, m: bytes):
        return [0]


class DummyMapper:
    def map(self, cw):
        return "A"


class DummyChannel:
    def transmit(self, strands):
        return [s for s in strands]


class DummyDecoder:
    def decode(self, reads):
        return b""


class DummyOutput:
    def write(self, message: bytes):
        pass


def test_pipeline_warns_on_large_encoder_n(capsys=None):
    # force small oligo_len to trigger warning
    buf = io.StringIO()
    old = sys.stdout
    try:
        sys.stdout = buf
        p = Pipeline(
        DummyInput(),
        DummyEncoder(),
        DummyMapper(),
        DummyChannel(),
        DummyDecoder(),
        DummyOutput(),
        oligo_len=20,
        overhead=0,
        )
    finally:
        sys.stdout = old

    out = buf.getvalue()
    assert "may be too large for oligo_len" in out
    # sanity: pipeline object exists
    assert hasattr(p, "encoder")
