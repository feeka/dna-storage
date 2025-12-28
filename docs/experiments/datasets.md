# Synthetic Datasets — Usage

This document describes the synthetic read generator and how to use generated datasets in experiments.

Generator CLI (simple):

```bash
python tools/gen_synthetic_reads.py --sub_p 0.02 --del_p 0.01 --ins_p 0.0 --copies 30 --n_refs 100 --ref_len 150 --seed 0 --out dna_storage/benchmarks/toy_synthetic/sample.ndjson
```

Output format: newline-delimited JSON (ndjson) with the following fields per record:
- `ref_id`, `ref_seq`, `read_seq`, `mutations`, `copy_id`, `trial_id`, `params`

Quick checks:
- Use the provided JSON schema to validate outputs: `docs/experiments/schema_synthetic_reads.json`.
- The generator supports `--mode` values: `random`, `homopolymer`, `gc_bias` (use `--gc_bias 0.7` for higher GC).

Examples:
- Homopolymer-rich references (for stress testing indels):
  ```bash
  python tools/gen_synthetic_reads.py --mode homopolymer --n_refs 200 --copies 30 --out benchmarks/hp.ndjson
  ```

- Variable coverage using lognormal dist (TODO: CLI option planned).

Notes:
- The generator uses a deterministic RNG seeded by `--seed` for reproducibility.
- For large-scale runs, generate per-trial folders with `trial_id` encoded in filenames.
