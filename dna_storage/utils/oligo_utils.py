from typing import Dict, Optional, Tuple


def recommend_rs_parameters(
    oligo_len: int,
    overhead: int,
    min_k: int = 1,
    desired_k: Optional[int] = None,
    desired_n: Optional[int] = None,
) -> Dict[str, object]:
    """Recommend RS parameters (n, k) and chunk sizes for a given oligo length.

    Assumptions:
    - mapper packs 1 byte -> 4 DNA bases (GF(256) byte -> 4 GF(4) symbols -> 4 bases)
    - usable_bases = oligo_len - overhead
    - maximum codeword length (n) in bytes is floor(usable_bases / 4)

    Returns a dict with keys: usable_bases, n_max, recommended (n,k,chunk_size) and warnings.

    Use desired_k or desired_n to ask for specific sizes; otherwise the helper suggests a
    conservative default (k ~= 0.85 * n to leave parity space).
    """
    if oligo_len <= 0 or overhead < 0:
        raise ValueError("oligo_len must be > 0 and overhead must be >= 0")

    usable = oligo_len - overhead
    if usable <= 0:
        return {
            "usable_bases": usable,
            "n_max": 0,
            "recommended": None,
            "warnings": ["No usable bases left after overhead; decrease overhead or increase oligo_len."],
        }

    # 1 byte -> 4 bases
    n_max = usable // 4

    warnings = []
    if n_max == 0:
        warnings.append("No bytes fit in the usable bases; reduce overhead or increase oligo length.")

    # choose defaults
    if desired_n is not None:
        if desired_n > n_max:
            warnings.append("desired_n is larger than the maximum possible; clipping to n_max")
        n = min(desired_n or n_max, n_max)
    else:
        # pick the largest reasonable n by default
        n = n_max

    # default k: leave ~15% for parity if not specified
    if desired_k is not None:
        k = min(desired_k, n)
    else:
        k = max(min(int(n * 0.85), n), min_k)

    if k > n:
        warnings.append("k cannot be larger than n; clipped to n")
        k = n

    chunk_size = k

    return {
        "usable_bases": usable,
        "n_max": n_max,
        "recommended": {"n": n, "k": k, "chunk_size": chunk_size},
        "warnings": warnings,
    }


def pretty_recommendation(oligo_len: int, overhead: int, **kwargs) -> str:
    r = recommend_rs_parameters(oligo_len, overhead, **kwargs)
    rec = r.get("recommended")
    lines = [f"oligo_len={oligo_len} overhead={overhead}", f"usable_bases={r['usable_bases']} max_bytes(n_max)={r['n_max']}"]
    if not rec:
        lines.append("no recommendation available")
    else:
        lines.append(f"recommended n={rec['n']}, k={rec['k']}, chunk_size={rec['chunk_size']}")
    if r["warnings"]:
        lines.append("warnings:")
        for w in r["warnings"]:
            lines.append(f"  - {w}")
    return "\n".join(lines)
