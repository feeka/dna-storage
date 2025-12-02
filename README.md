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

git clone https://github.com/feeka/rs-dna-pipeline.git
cd rs-dna-pipeline
python3 -m venv venv && source venv/bin/activate
pip install -e .
python3 -m dna_storage.examples.basic_rs_pipeline

## Benchmark (will be added this week)

| Error model                  | Redundancy | Recovery rate |
|------------------------------|------------|---------------|
| clean channel                | ?? %       | ?? %          |
| 0.5 % sub + 0.5 % indel      | ?? %       | ?? %          |
| 1.0 % sub + 1.0 % indel      | ?? %       | ?? %          |
| 2.0 % indel                  | ?? %       | ?? %          |

Script and plot will be placed in benchmarks/.

## Directory layout

dna_storage/
├── core/         # pipeline runner and abstract interfaces
├── components/   # encoder, mapper, channel, aligner, decoder, …
├── utils/        # GF(4)/GF(256) helpers, oligo utilities
├── examples/     # working end-to-end pipelines
└── benchmarks/   # (future reproducible results)

## Usage

See dna_storage/examples/basic_rs_pipeline.py for a complete working example.

## Citation (after DOI is created)

@software{feeka_rs_dna_pipeline_2025,
  author = {feeka},
  title = {rs-dna-pipeline: Modular Reed--Solomon pipeline for DNA data storage},
  year = {2025},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.XXXXXXX},
  url = {https://github.com/feeka/rs-dna-pipeline}
}

## License

MIT – see LICENSE

Issues and pull requests welcome.