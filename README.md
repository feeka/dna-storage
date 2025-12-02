# rs-dna-pipeline

Modular Reed–Solomon pipeline for DNA data storage experiments
Pure Python 3.9+ framework with pluggable components and realistic error simulation


## Features (v0.2.0 – December 2025)

- Reed–Solomon encoder/decoder over GF(256) – interpolation-based erasure recovery
- Automatic (k,n) recommendation for given oligo length and overhead (`pretty_recommendation`)
- Fully pluggable pipeline: Input → Encoder → Mapper → Channel → Aligner → Decoder → Output
- Simple global aligner + per-oligo consensus
- Channel models: substitution, insertion, deletion, coverage dropout
- Safety checks: warns when RS block size exceeds available oligo payload

## Quick start

git clone https://github.com/feeka/dna-storage.git
cd dna-storage
python3 -m venv venv && source venv/bin/activate
pip install -e .
python3 -m dna_storage.examples.basic_rs_pipeline

## What we did here (short)

We ran a set of Grass-style, message-level Reed–Solomon experiments that
measure average payload recovery across different outer-RS redundancy levels.
The run outputs are collected in `bench_rs.csv` and visualised below.

![Recovery vs redundancy](bench_rs.png)

## Benchmarks

This repository includes example benchmarking scripts and plotting utilities under `examples/` that produce reproducible CSV and PNG artifacts (e.g. `bench_rs.csv`, `bench_rs.png`).

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

- Run an ECC-only benchmark (trials, comma-list of redundancies, copies):

```bash
python3 examples/benchmark_rs.py 100 0.02,0.05,0.07,0.10,0.12 15
```

- Generate a nicer recovery plot from the CSV produced above:

```bash
python3 examples/plot_recovery_pretty.py bench_rs.csv
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