"""Plot mean percent recovered vs total error (sub+del) grouped by redundancy.

Usage:
  python3 examples/plot_recovery_vs_error.py bench_rs.csv

Saves bench_rs.by_error.png next to the CSV.
"""
import sys
import csv
from pathlib import Path
import matplotlib.pyplot as plt
from collections import defaultdict
import math


def read(path):
    groups = defaultdict(list)
    with open(path, newline='') as fh:
        r = csv.DictReader(fh)
        for row in r:
            redundancy = float(row['redundancy'])
            S = float(row['error_total'])
            mean = float(row['mean_percent_recovered_ecc'])
            std = float(row['std_percent_recovered_ecc'])
            groups[redundancy].append((S, mean, std))
    return groups


def plot(groups, out):
    # pretty defaults (match the style used in plot_recovery_pretty)
    try:
        import seaborn as sns

        sns.set_theme(style="whitegrid")
    except Exception:
        plt.style.use("seaborn-v0_8")

    fig, ax = plt.subplots(figsize=(11, 6))

    colors = ["#264653", "#2a9d8f", "#e76f51", "#f4a261", "#e9c46a", "#8ab17d"]
    markers = ["o", "s", "^", "D", "v", "P"]

    for i, (r, rows) in enumerate(sorted(groups.items())):
        rows_sorted = sorted(rows, key=lambda x: x[0])
        xs = [s * 100 for s, _, _ in rows_sorted]
        ys = [m for _, m, _ in rows_sorted]
        yerr = [st for _, _, st in rows_sorted]

        c = colors[i % len(colors)]
        mkr = markers[i % len(markers)]
        ax.plot(xs, ys, color=c, marker=mkr, linewidth=2.5, markersize=8, label=f"r={r*100:.0f}%")

        # draw shaded stddev band if available
        lower = [max(-5.0, y - e) for y, e in zip(ys, yerr)]
        upper = [min(105.0, y + e) for y, e in zip(ys, yerr)]
        if any(not math.isclose(u, l) for u, l in zip(upper, lower)):
            ax.fill_between(xs, lower, upper, color=c, alpha=0.12)

        # annotate points if there are not too many
        if len(xs) <= 12:
            for x, y in zip(xs, ys):
                ax.text(x, y + 2.0, f"{y:.0f}%", ha="center", va="bottom", fontsize=9, color=c)

    ax.set_xlabel("Total IDS error S = sub+del (%)")
    ax.set_ylabel("Mean percent payload recovered (%)")
    ax.set_title("Recovery vs total per-base IDS error — grouped by RS redundancy", fontsize=14, fontweight="bold")
    ax.set_ylim(-5, 105)
    # Auto-scale X axis to the data range (S percent). Keep lower bound at 0
    # and allow some padding on the right so labels/markers aren't cramped.
    all_x = []
    for rows in groups.values():
        all_x.extend([s * 100 for s, _, _ in rows])
    if all_x:
        min_x = min(all_x)
        max_x = max(all_x)
        # If min==max (single value) or very narrow range, add a small padding
        if math.isclose(min_x, max_x):
            pad = max(0.5, max_x * 0.01)
            left = max(0.0, min_x - pad)
            right = min(100.0, max_x + pad)
        else:
            left = max(0.0, min_x)
            right = min(100.0, max_x)
        ax.set_xlim(left, right)
    else:
        ax.set_xlim(0.0, 100.0)
    ax.grid(alpha=0.2)
    ax.legend(title="redundancy", loc="lower left")

    fig.tight_layout()
    fig.savefig(out, dpi=200)
    print(f"Saved {out}")


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'bench_rs.csv'
    p = Path(path)
    if not p.exists():
        print('CSV not found:', path)
        raise SystemExit(2)
    groups = read(path)
    out = str(p.with_suffix('.by_error.png'))
    plot(groups, out)
