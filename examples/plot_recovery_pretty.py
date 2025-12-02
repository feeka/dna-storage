"""Create a modern, clearer plot from bench_rs.csv

This script reads bench_rs.csv (columns: redundancy,k,copies,trials,mean_percent_recovered_ecc,std_percent_recovered_ecc)
and creates an annotated, publication-friendly figure with:
- mean percent recovered (line + markers)
- shaded std band
- sample size / copies annotated

Usage:
  python3 examples/plot_recovery_pretty.py bench_rs.csv

Saves bench_rs.recovery.pretty.png next to the CSV.
"""
import sys
from pathlib import Path
import csv
import matplotlib.pyplot as plt


def read_bench(path):
    redundancies = []
    means = []
    stds = []
    copies = None
    trials = None
    with open(path, newline='') as fh:
        r = csv.DictReader(fh)
        for row in r:
            redundancies.append(float(row['redundancy']))
            means.append(float(row['mean_percent_recovered_ecc']))
            stds.append(float(row['std_percent_recovered_ecc']))
            if copies is None:
                copies = int(row.get('copies', 0))
            if trials is None:
                trials = int(row.get('trials', 0))
    return redundancies, means, stds, copies, trials


def pretty_plot(path, out, show_ci=True):
    rs, means, stds, copies, trials = read_bench(path)
    xs = [r * 100 for r in rs]

    # pretty defaults
    try:
        import seaborn as sns
        sns.set_theme(style='whitegrid')
    except Exception:
        plt.style.use('seaborn-v0_8')

    fig, ax = plt.subplots(figsize=(10, 6))

    line_color = '#264653'
    shade_color = '#2a9d8f'
    marker_color = '#e9c46a'

    ax.plot(xs, means, color=line_color, marker='o', linewidth=2.5, markersize=10, label='mean percent recovered')

    if show_ci:
        lower = [m - s for m, s in zip(means, stds)]
        upper = [m + s for m, s in zip(means, stds)]
        ax.fill_between(xs, lower, upper, color=shade_color, alpha=0.18, label='±1 stddev')

    # annotate the mean value above each point
    for x, m in zip(xs, means):
        ax.text(x, m + 2.0, f"{m:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')

    # horizontal baseline guide
    ax.axhline(50, color='gray', linestyle='--', linewidth=1, alpha=0.6)
    ax.text(xs[0], 50 + 1.5, '50% baseline', color='gray', fontsize=9, alpha=0.8)

    ax.set_xlabel('Redundancy (%)', fontsize=12)
    ax.set_ylabel('Average percent payload recovered (%)', fontsize=12)
    ax.set_title('Outer RS (message-level) — recovery vs redundancy', fontsize=14, fontweight='bold')

    # add some explanatory subtitle with sample size / copies
    ax.text(0.99, 0.02, f"trials={trials} per point · copies={copies}", transform=ax.transAxes, ha='right', fontsize=9, color='dimgray')

    ax.set_ylim(-5, 105)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{int(x)}%" for x in xs])
    ax.grid(alpha=0.2)
    ax.legend(loc='lower left')

    fig.tight_layout()
    fig.savefig(out, dpi=200)
    print(f"Saved {out}")


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'bench_rs.csv'
    p = Path(path)
    if not p.exists():
        print('CSV not found:', path)
        raise SystemExit(2)
    out = str(p.with_suffix('.recovery.pretty.png'))
    pretty_plot(path, out)
