"""Synthetic sequencing mutation utilities.

Provides simple, deterministic mutation functions used by the synthetic read
generator. The implementations are intentionally straightforward and easy to
reason about for reproducible experiments.
"""
from __future__ import annotations

import random
from typing import List, Dict, Tuple

BASES = "ACGT"


def mutate_seq(ref: str, sub_p: float, del_p: float, ins_p: float, rng: random.Random) -> Tuple[str, List[Dict]]:
    """Apply substitutions, deletions and insertions to a reference sequence.

    Args:
        ref: Reference DNA sequence (A/C/G/T)
        sub_p: per-base substitution probability
        del_p: per-base deletion probability
        ins_p: per-position insertion probability (inserts a random base)
        rng: instance of random.Random (for deterministic behavior)

    Returns:
        A tuple (read_seq, mutations) where mutations is a list of dicts with
        keys: type in {"sub","del","ins"}, pos (reference position), and
        details: ref/obs for sub, ref for del, obs for ins.
    """
    out = []
    mutations = []
    i = 0
    while i < len(ref):
        base = ref[i]
        # deletion
        if rng.random() < del_p:
            mutations.append({"type": "del", "pos": i, "ref": base})
            # skip adding base to output
            i += 1
            continue
        # substitution
        if rng.random() < sub_p:
            obs = rng.choice([b for b in BASES if b != base])
            out.append(obs)
            mutations.append({"type": "sub", "pos": i, "ref": base, "obs": obs})
        else:
            out.append(base)
        # insertion (between bases)
        if rng.random() < ins_p:
            obs = rng.choice(BASES)
            out.append(obs)
            mutations.append({"type": "ins", "pos": i, "obs": obs})
        i += 1
    read_seq = "".join(out)
    return read_seq, mutations


def random_reference(length: int, rng: random.Random) -> str:
    """Generate a random reference sequence of length `length` using A/C/G/T."""
    return ''.join(rng.choice(BASES) for _ in range(length))
