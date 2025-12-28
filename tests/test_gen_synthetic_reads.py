import json
import os
import tempfile

from dna_storage.utils.sim_utils import mutate_seq, random_reference
from tools.gen_synthetic_reads import main as gen_main


def test_mutate_seq_basic():
    import random
    rng = random.Random(42)
    ref = "ACGTACGT"
    read, muts = mutate_seq(ref, sub_p=0.5, del_p=0.1, ins_p=0.1, rng=rng)
    assert isinstance(read, str)
    assert isinstance(muts, list)


def test_generator_creates_ndjson_and_is_deterministic():
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "sample.ndjson")
        # run the module as a script using args; emulate CLI
        import sys
        sys_argv = ["gen_synthetic_reads.py", "--out", out, "--n_refs", "2", "--copies", "2", "--seed", "123"]
        old_argv = sys.argv
        sys.argv = sys_argv
        try:
            gen_main()
        finally:
            sys.argv = old_argv
        assert os.path.exists(out)
        with open(out, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
        assert len(lines) >= 4
        # run again with same seed and confirm first line identical
        out2 = os.path.join(td, "sample2.ndjson")
        sys_argv = ["gen_synthetic_reads.py", "--out", out2, "--n_refs", "2", "--copies", "2", "--seed", "123"]
        sys.argv = sys_argv
        try:
            gen_main()
        finally:
            sys.argv = old_argv
        with open(out2, "r", encoding="utf-8") as fh:
            a = fh.readline()
        with open(out, "r", encoding="utf-8") as fh:
            b = fh.readline()
        assert a == b
