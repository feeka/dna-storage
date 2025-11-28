## DNA Storage — modular DNA-as-storage prototype - in progress...


### Short, to-the-point status
- Purpose: a lightweight, modular framework for experimenting with DNA-based storage pipelines (input → encode → map → channel → align → decode → output).
- Status: Work in progress — prototype components included for GF(4) and GF(256)/Reed–Solomon experiments, a simple aligner and channel simulators. Not production-ready.
- Versioning: semantic versioning (see `VERSION` + `CHANGELOG.md`). This repository is now at v0.1.0 as a first feature release (see CHANGELOG).

### Quick run (Python 3.8+)

``` python3 -m dna_storage.examples.basic_rs_pipeline ```

#### If you plan to use this for research or experiments note:
- Tools are small prototypes, not production ECC/mapping/synthesis models.
- Expect API changes as encoders/decoders and alignment strategies evolve.

#### New features since 0.0.1
- Reed–Solomon encoder/decoder (GF(256)) — encoder evaluates message polynomial at n points; decoder can reconstruct from k correct evaluations (interpolation-based erasure recovery).
- Oligo helper utilities — `recommend_rs_parameters` and `pretty_recommendation` to compute safe RS/oligo sizes for a target oligo length and overhead (useful to select `chunk_size`, `n`, `k`).
- Simple aligner & improved pipeline — pipeline accepts an optional `aligner` and groups reads for per-oligo consensus to improve indel recovery.
- Pipeline-size check — Pipeline will warn (by default) when an encoder’s `n` is too large for the configured oligo length/overhead.

Quick example showing oligo helper (python):

```py
from dna_storage.utils.oligo_utils import pretty_recommendation
print(pretty_recommendation(150, 40))
```

Using the pipeline with oligo checks and RS
- Examples now compute recommended n/k and set `FileInputter(chunk_size=k)` to ensure we map RS blocks into practical oligo sizes. See `dna_storage/examples/basic_rs_pipeline.py`.
- dna_storage/core: abstract interfaces + pipeline runner
- dna_storage/components: pluggable modules (inputter, encoder, mapper, channel, aligner, decoder, outputter)
- dna_storage/utils: GF(4) / GF(256) helpers and small utilities
- examples/: minimal runnable examples + demo input

Why this is useful
- Educational, experimental scaffold to plug in different encoders, mappers and channel models.
- Small, readable implementations so it’s easy to extend or swap components during R&D.

If you plan to use this for research or experiments note:
- Tools are small prototypes, not production ECC/mapping/synthesis models.
- Expect API changes as encoders/decoders and alignment strategies evolve.

Where to look next
- `dna_storage/examples/basic_rs_pipeline.py` — complete end-to-end toy pipeline.
- `dna_storage/components/encoder` and `decoder` — toy GF(4) and GF(256)/RS examples.

Contact & license
- This repo is MIT/exp permissive — contact via GitHub issues for questions.

Thanks — PRs, issues and contributions welcome. See `CONTRIBUTING.md` for workflow and versioning policy.
