from typing import Dict, List, Tuple


def _levenshtein(a: bytes, b: bytes) -> int:
    # simple iterative Levenshtein distance implementation for small inputs
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la

    prev = list(range(lb + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i] + [0] * lb
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev = cur
    return prev[-1]


def compare_bytes(orig: bytes, recovered: bytes) -> Dict[str, object]:
    """Compare original and recovered byte sequences.

    Returns a dict containing equality, lengths, Levenshtein distance, Hamming distance if same length,
    and a list of differing indices (first up to 50).
    """
    result: Dict[str, object] = {}
    result["equal"] = orig == recovered
    result["orig_len"] = len(orig)
    result["recovered_len"] = len(recovered)

    result["levenshtein"] = _levenshtein(orig, recovered)

    if len(orig) == len(recovered):
        diffs: List[Tuple[int, int, int]] = []  # index, orig_byte, rec_byte
        for i, (a, b) in enumerate(zip(orig, recovered)):
            if a != b:
                diffs.append((i, a, b))
            if len(diffs) >= 50:
                break
        result["hamming"] = sum(1 for a, b in zip(orig, recovered) if a != b)
        result["diffs_sample"] = diffs
    else:
        result["hamming"] = None
        result["diffs_sample"] = None

    return result


def pretty_report(orig: bytes, recovered: bytes) -> str:
    r = compare_bytes(orig, recovered)
    lines = []
    lines.append(f"equal: {r['equal']}")
    lines.append(f"orig_len: {r['orig_len']} recovered_len: {r['recovered_len']}")
    lines.append(f"levenshtein: {r['levenshtein']}")
    if r["hamming"] is not None:
        lines.append(f"hamming: {r['hamming']}")
        if r["diffs_sample"]:
            lines.append("first diffs (idx, orig_byte, recovered_byte):")
            for idx, a, b in r["diffs_sample"]:
                lines.append(f"  {idx}: {a} -> {b}")
    else:
        lines.append("hamming: (lengths differ)")

    return "\n".join(lines)
