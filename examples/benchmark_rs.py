"""Combined benchmark: outer Reed–Solomon (ECC) recovery sweep.

This script runs Grass-style outer-RS experiments (message-level RS across
strands) and sweeps total per-base error = sub + del (S values). Results are
written to bench_rs.csv, one row per (redundancy, error_total) containing
mean/std percent of payload recovered.
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

from dna_storage.components.encoder import ReedSolomonEncoder
from dna_storage.components.decoder import ReedSolomonDecoder
from dna_storage.utils.oligo_utils import recommend_rs_parameters


def run_benchmark(
    trials=100,
    copies=20,
    oligo_len=158,
    adapter_overhead=0,
    text_mode=True,
    redundancies=None,
    payload_min=500,
    payload_max=700,
    s_min=0.02,
    s_max=0.2,
    s_step=0.02,
):
    rec = recommend_rs_parameters(oligo_len, adapter_overhead)
    n_max = rec["n_max"]
    max_overhead = 0.30
    k = max(1, int(n_max / (1 + max_overhead)))

    # Default to a single, practical redundancy level (15%) for canonical runs.
    # This keeps parity meaningful while remaining storage-efficient.
    redundancy_levels = redundancies if redundancies is not None else [0.15]

    # If user explicitly passed redundancies, sanitize: skip any 0.0 entries
    # (RS encoder requires n>k), but preserve other values.
    if redundancies is not None:
        filtered = [float(r) for r in redundancy_levels if float(r) > 0.0]
        if len(filtered) != len(redundancy_levels):
            print("warning: 0.0 redundancy value is not supported and will be skipped")
        redundancy_levels = filtered

    # generate the S sweep values (total error = sub + del)
    S_values = [round(x, 5) for x in frange(s_min, s_max + 1e-9, s_step)]

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

    # Outer loop: RS redundancy levels (unchanged)
    for r in redundancy_levels:
        print(f"Running redundancy {r*100:.0f}% trials={trials} copies={copies} ...")
        # Only keep the realistic, message-level (outer) Reed-Solomon experiment
        stats = {"ecc": {"percent": []}}
        start = time()

        successes = 0
        failures = 0
        for S in S_values:
            # perform 'trials' independent trials for each S
            print(f"  testing total-error S={S:.3f} — {trials} trials")
            stats_S = []
            for t in range(trials):
                # choose payload length per trial uniformly
                L = random.randint(payload_min, payload_max)
                if text_mode:
                    import string

                    chars = string.ascii_letters + string.digits + string.punctuation + " \n\t"
                    text = "".join(random.choices(chars, k=L))
                    data = text.encode("utf-8")
                else:
                    data = os.urandom(L)
                # write payload used for this trial (bench_rs.bin)
                with open(in_file, "wb") as fh:
                    fh.write(data)

                # constrained split (option B): sub in [0.2*S, 0.8*S], del = S - sub
                s_lo = 0.2 * S
                s_hi = 0.8 * S
                sub_p = random.uniform(s_lo, s_hi)
                del_p = max(0.0, S - sub_p)

                dup = SoupDuplicator(copies=copies)
                ids = IDSChannel(sub_p=sub_p, del_p=del_p, seed=None)
                base_channel = type("Chain", (), {"transmit": lambda self, strands: ids.transmit(dup.transmit(strands))})()

                # ECC pipeline (outer RS across message chunks).
                # Use n = ceil(k*(1+r)) but ensure n >= k; n==k gives no parity.
                n = min(n_max, ceil(k * (1 + r)))
                if n < k:
                    n = k
                ecc_enc = ReedSolomonEncoder(n=n, k=k)
                ecc_dec = ReedSolomonDecoder(n=n, k=k, mapper=RotatingMapper())

                # suppress per-trial YAML dumps by sending to OS null
                pipeline_ecc = Pipeline(
                    FileInputter(in_file, chunk_size=k),
                    ecc_enc,
                    RotatingMapper(),
                    base_channel,
                    ecc_dec,
                    YamlOutputter(outpath=os.devnull),
                    aligner=SimpleAligner(),
                    oligo_len=oligo_len,
                    overhead=adapter_overhead,
                )
                cmp_ecc = pipeline_ecc.run()

                # record percent recovered for ECC pipeline
                if cmp_ecc is None:
                    stats_S.append(0.0)
                    stats["ecc"]["percent"].append(0.0)
                    failures += 1
                    print(f"{t+1}/{trials} -> ERROR ({failures} errors so far)", flush=True)
                else:
                    if isinstance(cmp_ecc.get("levenshtein"), int):
                        lv = cmp_ecc.get("levenshtein")
                        orig_len = cmp_ecc.get("orig_len") or len(data)
                        pct = max(0.0, 1.0 - (lv / orig_len)) * 100 if orig_len else 0.0
                        stats_S.append(pct)
                        stats["ecc"]["percent"].append(pct)
                        if lv == 0:
                            successes += 1
                            print(f"{t+1}/{trials} -> OK ({successes} successes so far)", flush=True)
                        else:
                            failures += 1
                            print(f"{t+1}/{trials} -> ERROR (lev={lv} ; {failures} errors so far)", flush=True)
                    else:
                        ok = cmp_ecc.get("equal")
                        stats_S.append(100.0 if ok else 0.0)
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

            # compute mean/std for this redundancy+S and append a row
            mean_s = statistics.mean(stats_S) if stats_S else 0.0
            std_s = statistics.pstdev(stats_S) if stats_S else 0.0
            results.append(
                {
                    "redundancy": r,
                    "error_total": S,
                    "k": k,
                    "copies": copies,
                    "trials": trials,
                    "mean_percent_recovered_ecc": mean_s,
                    "std_percent_recovered_ecc": std_s,
                }
            )

        elapsed = time() - start
        mean_redundancy = statistics.mean(stats["ecc"]["percent"]) if stats["ecc"]["percent"] else 0.0
        print(f"  completed redundancy {r*100:.0f}% (time {elapsed:.1f}s) mean(ecc)={mean_redundancy:.1f}")

    out = "bench_rs.csv"
    fieldnames = [
        "redundancy",
        "error_total",
        "k",
        "copies",
        "trials",
        "mean_percent_recovered_ecc",
        "std_percent_recovered_ecc",
    ]
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)


def frange(a, b, step):
    x = a
    while x <= b:
        yield x
        x += step


if __name__ == "__main__":
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    # optional second arg: comma separated redundancy values (fractions), e.g. '0.15' or '0.05,0.15'
    redundancies = None
    if len(sys.argv) > 2:
        try:
            redundancies = [float(x) for x in sys.argv[2].split(',')]
        except Exception:
            print("Invalid redundancies arg, expected comma-separated floats like '0.15'")
            sys.exit(2)

    # allow optional third CLI argument for copies (number of reads / coverage)
    copies = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    # payload min/max (optional 4th/5th args)
    payload_min = int(sys.argv[4]) if len(sys.argv) > 4 else 500
    payload_max = int(sys.argv[5]) if len(sys.argv) > 5 else 700

    # s range (optional 6th arg in form min:max:step)
    # default to the same values used in run_benchmark's signature
    s_min, s_max, s_step = 0.02, 0.2, 0.02
    if len(sys.argv) > 6:
        try:
            a, b, st = [float(x) for x in sys.argv[6].split(':')]
            s_min, s_max, s_step = a, b, st
        except Exception:
            print("Invalid s-range, expected 'min:max:step' like '0.02:0.2:0.02' — using defaults")
            s_min, s_max, s_step = 0.02, 0.2, 0.02

    run_benchmark(
        trials=trials,
        copies=copies,
        oligo_len=158,
        adapter_overhead=0,
        text_mode=True,
        redundancies=redundancies,
        payload_min=payload_min,
        payload_max=payload_max,
        s_min=s_min,
        s_max=s_max,
        s_step=s_step,
    )
