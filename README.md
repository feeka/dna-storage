# rs-dna-pipeline ✨

Compact, modular Reed–Solomon pipelines and reproducible benchmarks for DNA data storage experiments.
Pure Python 3.9+ — quick to run, easy to extend.


## Features (v0.2.0 – December 2025)

- Reed–Solomon encoder/decoder over GF(256) – interpolation-based erasure recovery
- Automatic (k,n) recommendation for given oligo length and overhead (`pretty_recommendation`)
- Fully pluggable pipeline: Input → Encoder → Mapper → Channel → Aligner → Decoder → Output
- Simple global aligner + per-oligo consensus
- Channel models: substitution, insertion, deletion, coverage dropout
- Safety checks: warns when RS block size exceeds available oligo payload

## Quick start

Clone, create a virtualenv, install, and run the example (copy/paste):

```bash
git clone https://github.com/feeka/dna-storage.git
cd dna-storage
# create & activate a venv called .venv (recommended)
python3 -m venv .venv
source .venv/bin/activate
python3 -m dna_storage.examples.basic_rs_pipeline
```

## What we did here (short)

We ran a set of [Prof. Robert Grass-style](https://doi.org/10.1002/anie.201411378), message-level Reed–Solomon experiments that
measure average payload recovery across different outer-RS redundancy levels.
Outputs are collected in `bench_rs.csv`. Representative visualizations below.

<div align="center">
	<img src="bench_rs.png" alt="Recovery vs error" width="460" />
</div>

Very short — likely causes for low recovery

- aligner is too simple (indels break consensus)
- deletions shift symbol packing → erasures
- RS decoder is erasure-only (no substitution correction)
- low coverage or too-small parity makes recovery fragile

## Benchmarks

This repository includes example benchmarking scripts and plotting utilities under `examples/` that produce reproducible CSV and PNG artifacts (e.g. `bench_rs.csv`, `bench_rs.png`).

Experiment: controlled IDS-error sweep (staple behaviour)
-----------------------------------------------------

We include a reproducible experiment that sweeps the total per-base error (substitutions + deletions)
across a fixed set of levels and measures average payload recovery using only message-level (outer) Reed–Solomon.

Key parameters used by the canonical sweep (configurable in `examples/benchmark_rs.py`):

- Error total S values: 0.02 → 0.20 in steps of 0.02 (i.e. 0.02, 0.04, …, 0.20)
	- NOTE: S is the per-base IDS error fraction (S = sub_p + del_p); plots show S on the x-axis as a percentage (S * 100). IDSChannel simulates substitutions + deletions (no insertions), so S only includes those two error types.
- Trials per S: 100
- Payload length per trial L: uniformly sampled from [500, 700] bytes
- Error split rule (Option B — constrained, recommended): sub_p ∈ [0.2*S, 0.8*S] chosen uniformly; del_p = S - sub_p
- Coverage (copies): 20 (per trial)
- Default RS redundancy used by the canonical sweep: 0.15 (15%)
- Pipeline behaviour: exactly the `basic_rs_pipeline` flow (Reed–Solomon encoder/decoder, rotating mapper, SoupDuplicator, IDSChannel, SimpleAligner)

Notes:
- The script uses the constrained split so each trial preserves the requested total error S but varies the ratio of deletion vs substitution.
- We also convert alignment failures into explicit erasures so the message-level RS decoder can repair missing symbols.
- Results are written to `bench_rs.csv` and plotted with the existing plotting scripts.

To run the canonical sweep (defaults):

```bash
python3 examples/benchmark_rs.py    # runs the S sweep with defaults (100 trials × 10 S values)
```

You can override parameters on the CLI — see header of `examples/benchmark_rs.py` for syntax.

## Directory layout

High-level structure (top-level package + helpers and example pipelines):

- dna_storage/ (main package)
	- core/ — pipeline runner and abstract interfaces
	- components/ — encoders, mappers, channels, aligners, decoders, etc.
	- utils/ — GF(4)/GF(256) helpers and oligo utilities
	- examples/ — working end-to-end pipelines, benchmark drivers, plot helpers
	- benchmarks/ — reproducible benchmark outputs and analysis artifacts

For a quick visual, here's the same tree in monospace:

```text
dna_storage/
├── core/         # pipeline runner and abstract interfaces
├── components/   # encoder, mapper, channel, aligner, decoder, …
├── utils/        # GF(4)/GF(256) helpers, oligo utilities
├── examples/     # working end-to-end pipelines and bench scripts
└── benchmarks/   # reproducible benchmark outputs & analysis
```

## Usage

See `dna_storage/examples/basic_rs_pipeline.py` for a complete working example.

Mini usage (benchmarks & plotting)

Quick test & canonical run

- Smoke test (fast, sanity-check; outputs bench_rs.csv):

```bash
# 3 trials per S, single redundancy=15%, copies=20, payload fixed at 500, S=0.02,0.04,0.06
python3 examples/benchmark_rs.py 3 0.15 20 500 500 0.02:0.06:0.02
```

- Full canonical sweep (default):

```bash
# runs trials=100, redundancy=0.15, copies=20, payloads=500..700, S=0.02..0.20
python3 examples/benchmark_rs.py
```

- Generate the pretty recovery plot (redundancy on x-axis):

```bash
python3 examples/plot_recovery_pretty.py bench_rs.csv
```

- Generate recovery vs total-IDS-error plot (S on x-axis):

```bash
python3 examples/plot_recovery_vs_error.py bench_rs.csv
```

-- Parse the run log (or per-redundancy CSV) and produce the successes bar chart:

```bash
python3 examples/plot_successes.py successes
```

Output files you should see in the repo root after running the bench above:

- `bench_rs.csv` — mean/std mean percent recovered per redundancy
- `bench_rs.png` — the recovery plot (illustrated above)


## Citation

If you use this code in published work, please cite the repository URL and add an entry appropriate to your citation style.

## License

MIT – see LICENSE

Issues and pull requests welcome.