"""Plot results from bench_rs.csv

Usage:
  python3 examples/plot_rs.py bench_rs.csv

Saves bench_rs.png next to the CSV.
"""
import sys
import csv
import matplotlib.pyplot as plt
from pathlib import Path


def plot_csv(path):
    redundancies = []
    ecc_means = []
    ecc_stds = []

    with open(path, newline="") as fh:
        r = csv.DictReader(fh)
        for row in r:
            redundancies.append(float(row["redundancy"]))
            ecc_means.append(float(row["mean_percent_recovered_ecc"]))
            ecc_stds.append(float(row["std_percent_recovered_ecc"]))

    xs = [r*100 for r in redundancies]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.errorbar(xs, ecc_means, yerr=ecc_stds, marker='o', capsize=4, label='Outer RS (ECC)')
    ax.set_xlabel("Redundancy (%)")
    ax.set_ylabel("Average percent of payload recovered (%)")
    ax.set_title("Outer RS (message-level) — average percent payload recovered")
    ax.set_ylim(-5, 105)
    ax.legend()
    ax.grid(alpha=0.25)

    out = str(Path(path).with_suffix('.png'))
    fig.tight_layout()
    fig.savefig(out)
    print(f"Saved {out}")


if __name__ == '__main__':
    csvpath = sys.argv[1] if len(sys.argv) > 1 else 'bench_rs.csv'
    plot_csv(csvpath)
