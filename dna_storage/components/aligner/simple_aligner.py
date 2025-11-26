from typing import Iterable, List


def _global_align(a: str, b: str, match=1, mismatch=0, gap=-1):
    # simple Needleman-Wunsch global alignment returning aligned a', b'
    la, lb = len(a), len(b)
    # score matrix
    dp = [[0] * (lb + 1) for _ in range(la + 1)]
    for i in range(1, la + 1):
        dp[i][0] = dp[i - 1][0] + gap
    for j in range(1, lb + 1):
        dp[0][j] = dp[0][j - 1] + gap

    for i in range(1, la + 1):
        for j in range(1, lb + 1):
            score_sub = dp[i - 1][j - 1] + (match if a[i - 1] == b[j - 1] else mismatch)
            score_del = dp[i - 1][j] + gap
            score_ins = dp[i][j - 1] + gap
            dp[i][j] = max(score_sub, score_del, score_ins)

    # traceback
    i, j = la, lb
    a_al = []
    b_al = []
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            sc = dp[i - 1][j - 1] if i - 1 >= 0 and j - 1 >= 0 else None
        else:
            sc = None

        # prefer match/mismatch
        if i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + (match if a[i - 1] == b[j - 1] else mismatch):
            a_al.append(a[i - 1])
            b_al.append(b[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + gap:
            a_al.append(a[i - 1])
            b_al.append("-")
            i -= 1
        else:
            b_al.append(b[j - 1])
            a_al.append("-")
            j -= 1

    return "".join(reversed(a_al)), "".join(reversed(b_al))


class SimpleAligner:
    """Align reads to the longest read then create a simple column-majority consensus.

    Behavior:
    - Choose the longest read as reference
    - Align every read to the reference using a simple global aligner
    - Build consensus by picking the most common non-gap base per column
    - Return a single consensus string (or empty if no reads)
    """

    def __init__(self):
        pass

    def align(self, reads: Iterable[str]) -> Iterable[str]:
        reads = list(reads)
        if not reads:
            return []

        # pick the longest as reference
        ref = max(reads, key=len)

        aligned_columns: List[List[str]] = []

        # Keep track of how many reads have been merged so far so we can
        # pad columns when a new alignment is longer/shorter than earlier ones.
        reads_seen = 0

        # align each read to the ref and merge into columns
        for r in reads:
            a_ref, a_r = _global_align(ref, r)
            L = len(a_ref)

            # If aligned_columns shorter than this alignment, extend and pad
            if len(aligned_columns) < L:
                # extend with empty columns and pad them with '-' for previous reads
                for _ in range(len(aligned_columns), L):
                    aligned_columns.append(["-"] * reads_seen)

            # Now for each existing column index, append the corresponding base or a gap
            for idx in range(len(aligned_columns)):
                if idx < L:
                    aligned_columns[idx].append(a_r[idx])
                else:
                    # This read did not produce this column -> gap
                    aligned_columns[idx].append("-")

            reads_seen += 1

        # build consensus per column
        cons = []
        for col in aligned_columns:
            # count non-gap bases
            counts = {}
            for c in col:
                if c == "-":
                    continue
                counts[c] = counts.get(c, 0) + 1
            if not counts:
                # if all gaps, choose gap
                cons.append("-")
            else:
                # pick most common
                best = max(counts.items(), key=lambda x: x[1])[0]
                cons.append(best)

        # compress gaps out of consensus (simple strategy)
        consensus = "".join([c for c in cons if c != "-"])
        return [consensus]
