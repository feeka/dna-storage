## DNA Storage — modular DNA-as-storage prototype - in progress...

Short, to-the-point status
- Purpose: a lightweight, modular framework for experimenting with DNA-based storage pipelines (input → encode → map → channel → align → decode → output).
- Status: Work in progress — prototype components included for GF(4) and GF(256)/Reed–Solomon experiments, a simple aligner and channel simulators. Not production-ready.
- Versioning: semantic versioning (see `VERSION` + `CHANGELOG.md`). Expect regular breaking changes while the API stabilizes.

Quick run (Python 3.8+)

```bash
python3 -m dna_storage.examples.basic_rs_pipeline
```

Project layout (short)
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
