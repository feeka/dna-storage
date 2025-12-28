#!/usr/bin/env python3
"""Generate synthetic sequencing reads with controlled substitution/deletion/insertion rates.

Writes newline-delimited JSON (ndjson) with one record per read.
"""
from __future__ import annotations

import argparse
import json
import os
import random
from typing import List, Dict
from dna_storage.utils.sim_utils import mutate_seq, random_reference


def generate_for_ref(ref_id: str, ref_seq: str, sub_p: float, del_p: float, ins_p: float, copies: int, seed: int, trial_id: int) -> List[Dict]:
    rng = random.Random(seed)
    records = []
    for copy_id in range(copies):
        read_seq, mutations = mutate_seq(ref_seq, sub_p=sub_p, del_p=del_p, ins_p=ins_p, rng=rng)
        rec = {
            "ref_id": ref_id,
            "ref_seq": ref_seq,
            "read_seq": read_seq,
            "mutations": mutations,
            "copy_id": copy_id,
            "trial_id": trial_id,
            "params": {"sub_p": sub_p, "del_p": del_p, "ins_p": ins_p, "seed": seed},
        }
        records.append(rec)
    return records


def build_refs(n_refs: int, ref_len: int, mode: str, gc_bias: float, seed: int):
    rng = random.Random(seed)
    refs = []
    for i in range(n_refs):
        if mode == "random":
            seq = random_reference(ref_len, rng)
        elif mode == "homopolymer":
            # create a sequence with occasional long runs
            seq = []
            while len(seq) < ref_len:
                base = rng.choice("ACGT")
                run = rng.randint(1, 8) if rng.random() < 0.1 else rng.randint(1, 3)
                seq.extend([base] * run)
            seq = ''.join(seq[:ref_len])
        elif mode == "gc_bias":
            # generate sequence with elevated GC content
            seq = ''.join(rng.choices(['G', 'C', 'A', 'T'], weights=[gc_bias, gc_bias, 1 - gc_bias, 1 - gc_bias], k=ref_len))
        else:
            raise ValueError("unknown mode")
        refs.append((f"ref_{i}", seq))
    return refs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sub_p", type=float, default=0.02)
    p.add_argument("--del_p", type=float, default=0.01)
    p.add_argument("--ins_p", type=float, default=0.0)
    p.add_argument("--copies", type=int, default=30)
    p.add_argument("--n_refs", type=int, default=100)
    p.add_argument("--ref_len", type=int, default=150)
    p.add_argument("--mode", choices=["random", "homopolymer", "gc_bias"], default="random")
    p.add_argument("--gc_bias", type=float, default=0.6)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--trial_id", type=int, default=0)
    p.add_argument("--out", type=str, required=True)
    args = p.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    refs = build_refs(args.n_refs, args.ref_len, args.mode, args.gc_bias, args.seed)

    with open(args.out, "w", encoding="utf-8") as fh:
        for ref_id, ref_seq in refs:
            records = generate_for_ref(ref_id, ref_seq, args.sub_p, args.del_p, args.ins_p, args.copies, args.seed, args.trial_id)
            for r in records:
                fh.write(json.dumps(r) + "\n")

    print(f"Wrote synthetic reads to {args.out}")


if __name__ == "__main__":
    main()
