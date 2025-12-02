"""Combined benchmark: outer Reed–Solomon (ECC) vs NoECC (no error correction).

This script runs a Grass-style outer-RS experiment (message-level RS across
strands) and, in the same trials, measures the recovered payload percent when no
error correction is used (NoECC). Results are written to bench_rs.csv.
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import random
import csv
from math import ceil
from time import time
import statistics

from dna_storage.core.pipeline import Pipeline
from dna_storage.components.inputter.file_inputter import FileInputter
from dna_storage.components.mapper.rotating import RotatingMapper
from dna_storage.components.channel.soup_duplicator import SoupDuplicator
from dna_storage.components.channel.ids_channel import IDSChannel
from dna_storage.components.aligner.simple_aligner import SimpleAligner
from dna_storage.components.outputter.yaml_outputter import YamlOutputter

from dna_storage.components.encoder import ReedSolomonEncoder, NoECCEncoder
from dna_storage.components.decoder import ReedSolomonDecoder, NoECCDecoder
from dna_storage.utils.oligo_utils import recommend_rs_parameters


def run_benchmark(trials=50, copies=4, oligo_len=158, adapter_overhead=0, text_mode=True, redundancies=None):
    rec = recommend_rs_parameters(oligo_len, adapter_overhead)
    n_max = rec["n_max"]
    max_overhead = 0.30
    k = max(1, int(n_max / (1 + max_overhead)))

    redundancy_levels = redundancies if redundancies is not None else [0.0, 0.05, 0.10, 0.20, 0.30]

    if text_mode:
        import string
        chars = string.ascii_letters + string.digits + string.punctuation + " \n\t"
        text = "".join(random.choices(chars, k=1024))
        data = text.encode("utf-8")
    else:
        data = os.urandom(1024)

    in_file = "bench_rs.bin"
    with open(in_file, "wb") as fh:
        fh.write(data)

    results = []

    for r in redundancy_levels:
        print(f"Running redundancy {r*100:.0f}% trials={trials} copies={copies} ...")
        # Only keep the realistic, message-level (outer) Reed-Solomon experiment
        stats = {"ecc": {"percent": []}}
        start = time()

        successes = 0
        failures = 0
        for t in range(trials):
            sub_p = random.uniform(0.01, 0.04)
            del_p = random.uniform(0.005, 0.03)

            dup = SoupDuplicator(copies=copies)
            ids = IDSChannel(sub_p=sub_p, del_p=del_p, seed=None)
            base_channel = type("Chain", (), {"transmit": lambda self, strands: ids.transmit(dup.transmit(strands))})()

            # ECC pipeline (outer RS across message chunks) — for r==0, acts like NoECC
            if r == 0.0:
                ecc_enc = NoECCEncoder()
                ecc_dec = NoECCDecoder(RotatingMapper())
            else:
                n = min(n_max, ceil(k * (1 + r)))
                ecc_enc = ReedSolomonEncoder(n=n, k=k)
                ecc_dec = ReedSolomonDecoder(n=n, k=k, mapper=RotatingMapper())

            # suppress per-trial YAML dumps by sending to OS null
            pipeline_ecc = Pipeline(FileInputter(in_file, chunk_size=k), ecc_enc, RotatingMapper(), base_channel, ecc_dec, YamlOutputter(outpath=os.devnull), aligner=SimpleAligner(), oligo_len=oligo_len, overhead=adapter_overhead)
            cmp_ecc = pipeline_ecc.run()

            # record percent recovered for ECC pipeline
            if cmp_ecc is None:
                stats["ecc"]["percent"].append(0.0)
                failures += 1
                print(f"{t+1}/{trials} -> ERROR ({failures} errors so far)", flush=True)
            else:
                if isinstance(cmp_ecc.get("levenshtein"), int):
                    lv = cmp_ecc.get("levenshtein")
                    orig_len = cmp_ecc.get("orig_len") or len(data)
                    pct = max(0.0, 1.0 - (lv / orig_len)) * 100 if orig_len else 0.0
                    stats["ecc"]["percent"].append(pct)
                    if lv == 0:
                        successes += 1
                        print(f"{t+1}/{trials} -> OK ({successes} successes so far)", flush=True)
                    else:
                        failures += 1
                        print(f"{t+1}/{trials} -> ERROR (lev={lv} ; {failures} errors so far)", flush=True)
                else:
                    ok = cmp_ecc.get("equal")
                    stats["ecc"]["percent"].append(100.0 if ok else 0.0)
                    if ok:
                        successes += 1
                        print(f"{t+1}/{trials} -> OK ({successes} successes so far)", flush=True)
                    else:
                        failures += 1
                        print(f"{t+1}/{trials} -> ERROR ({failures} errors so far)", flush=True)

            # (retained) periodic progress summary every ~10% completes
            interval = max(1, trials // 10)
            if (t + 1) % interval == 0 or (t + 1) == trials:
                print(f"  redundancy {r:.2f}: {t+1}/{trials} trials done — successes: {successes}, errors: {failures}", flush=True)

        elapsed = time() - start

        # compute mean/std
        ecc_percents = stats["ecc"]["percent"]
        row = {
            "redundancy": r,
            "k": k,
            "copies": copies,
            "trials": trials,
            "mean_percent_recovered_ecc": statistics.mean(ecc_percents) if ecc_percents else 0.0,
            "std_percent_recovered_ecc": statistics.pstdev(ecc_percents) if ecc_percents else 0.0,
        }
        results.append(row)
        print(f"  completed redundancy {r*100:.0f}% (time {elapsed:.1f}s) mean(ecc)={row['mean_percent_recovered_ecc']:.1f}")

    out = "bench_rs.csv"
    fieldnames = ["redundancy", "k", "copies", "trials", "mean_percent_recovered_ecc", "std_percent_recovered_ecc"]
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)


if __name__ == "__main__":
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    # optional second arg: comma separated redundancy values (fractions), e.g. '0.15' or '0.05,0.15'
    redundancies = None
    if len(sys.argv) > 2:
        try:
            redundancies = [float(x) for x in sys.argv[2].split(',')]
        except Exception:
            print("Invalid redundancies arg, expected comma-separated floats like '0.15'")
            sys.exit(2)

    # allow optional third CLI argument for copies (number of reads / coverage)
    copies = int(sys.argv[3]) if len(sys.argv) > 3 else 4

    run_benchmark(trials=trials, copies=copies, oligo_len=158, adapter_overhead=0, text_mode=True, redundancies=redundancies)
