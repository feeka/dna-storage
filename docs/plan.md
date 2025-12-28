# Project Plan — ML-Driven Channel Modeling (Detailed, Stepwise)

**Status:** Expanded into precise step-level tasks for execution (follow each substep exactly).

---

## Plain-English Goal (1 line)
Build and evaluate an ML-based channel (`MLChannel`) that can be trained on synthetic and public reads, integrate it into the repo's bench pipeline, and produce a reproducible set of experiments and figures for a paper.

---

## How to use this plan
- Execute tasks in numeric order (0.x → 1.x → 2.x ...). Each atomic step includes: what file(s) to change, exact code or commands to add, acceptance criteria, and estimated time (hours).
- Stop and report back only if a step's acceptance criteria fail or an external resource (data / compute) is unavailable.

---

# 0. Project bootstrap & environment (0.1–0.6)
0.1 ✅ Create a feature branch: `git checkout -b feat/ml-channel` (0.1h). Acceptance: branch exists and pushes to remote.

0.2 ✅ Update `pyproject.toml` to add optional ML extras (dev extras group `ml`) listing `torch>=1.12,<2.0`, `numpy`, `pandas`, `tqdm`. Commit with message "chore: add ML extras" (0.3h). Acceptance: `poetry install --extras ml` or `pip install -r requirements-dev.txt` works locally.

0.3 Add `tools/` and `docs/experiments/` folders if missing and create a README for experiment reproducibility (0.2h). Acceptance: `tools/README.md` describes script usage.

0.4 Verify local GPU availability (if desired): run `python -c "import torch; print(torch.cuda.is_available())"` and record the result in `docs/experiments/compute.md` (0.2h). Acceptance: file added and output recorded.

0.5 ✅ Add contact / maintainer note to `CONTRIBUTING.md` that ML extras are optional and include instructions to run smoke tests (0.1h).

---

# 1. Data & Synthetic generation (1.1–1.12)
1.1 ✅ Create `tools/gen_synthetic_reads.py` with a CLI: `--sub_p`, `--del_p`, `--ins_p`, `--copies`, `--seed`, `--out` (ndjson) (2h). Acceptance: can run `python tools/gen_synthetic_reads.py --sub_p 0.02 --del_p 0.01 --copies 10 --out sample.ndjson` and create file.

1.2 Define output schema (ndjson): each line JSON with fields: `ref_id`, `ref_seq`, `read_seq`, `mutations` (list of per-read edits), `copy_id`, `trial_id`, `params` (dict). Add schema file `docs/experiments/schema_synthetic_reads.json` (0.5h). Acceptance: schema file present, and generator produces records conforming to it.

1.3 Add helper to `dna_storage/utils` named `sim_utils.py` with deterministic mutation functions used by generator (0.5h). Acceptance: functions `mutate_seq(ref, sub_p, del_p, ins_p, rng)` exist and are unit-tested.

1.4 Build homopolymer-rich generator mode: `--mode homopolymer --gc_bias 0.7` creates references with long runs (0.5h). Acceptance: generated references include runs ≥6 of a base.

1.5 Implement coverage distributions: support `--copies` as int or `--copies-dist lognormal,mu,sigma` (0.5h). Acceptance: generator outputs variable copy counts per reference per trial.

1.6 Add unit tests under `tests/test_gen_synthetic_reads.py` verifying 3 basic settings and deterministic outputs with seed (0.5h). Acceptance: tests pass locally.

1.7 Add a small synthetic dataset artifact under `dna_storage/benchmarks/toy_synthetic/` (100 references × variable reads) to be used by smoke tests (0.2h). Acceptance: small dataset present and checked into the repo (LFS not required for tiny sample).

1.8 Document usage in `docs/experiments/datasets.md` including exact CLI examples and expected output file paths (0.3h).

---

# 2. MLChannel skeleton & API (2.1–2.10)
2.1 Create file `dna_storage/components/channel/ml_channel.py` (0.2h).

2.2 Add class `MLChannel` with methods and docstrings:
- `__init__(self, model=None, tokenizer=None, device='cpu')`
- `fit(self, dataset_path, epochs, batch_size, out_dir, seed=0)`
- `transmit(self, strands)` — matches `IDSChannel.transmit` return type
- `save(self, path)` / `load(self, path)`
(0.5h). Acceptance: class file exists and imports.

2.3 Implement `transmit()` placeholder that for now delegates to `IDSChannel` when `self.model is None` (safe default) (0.5h). Acceptance: unit test uses MLChannel with model=None and reproduces IDSChannel behavior.

2.4 Add `fit()` placeholder that raises NotImplementedError until a training harness is added; add a unit test that asserts NotImplementedError for now (0.2h). Acceptance: test passes.

2.5 Add serialization helpers that save `config.json` and `model.pt` (placeholders) under a directory (0.5h). Acceptance: `save()` writes expected files.

2.6 Add type hints and clear docstrings describing expected dataset format (ndjson from step 1) and example CLI usage (0.3h).

2.7 Add unit tests `tests/test_ml_channel_api.py` with the above checks and a smoke `transmit()` check on toy dataset (0.5h). Acceptance: tests pass.

2.8 Add linting / small coverage tests to ensure basic style (0.2h).

2.9 Open PR with description "feat(ml): add MLChannel skeleton and API + tests" and request review (0.1h). Acceptance: PR created.

---

# 3. Training harness & small RNN baseline (3.1–3.12)
3.1 Create `examples/ml_train.py` with CLI: `--data`, `--model`, `--epochs`, `--batch`, `--out` (0.5h). Acceptance: script supports `--help`.

3.2 Implement a `dna_storage.ml` package submodule with `models.py` containing `RNNChannelModel(torch.nn.Module)` and `SmallTransformerChannelModel` (simple versions, < 100k params) (1.5h).

3.3 Implement dataset loader `dna_storage.ml.data.SyntheticReadDataset` that reads ndjson and yields (ref_seq, read_seq, metadata) tensors (1h). Acceptance: dataset works with torch DataLoader.

3.4 Implement training loop in `examples/ml_train.py` to train negative log-likelihood per base (simple cross-entropy for k-mer prediction or edit labels) and checkpoint model to `--out` (2h). Acceptance: script runs one epoch on toy dataset.

3.5 Add evaluation utilities to compute per-base log-likelihood on held-out set and calibration metrics; save metrics JSON (0.5h). Acceptance: `examples/ml_train.py --eval` produces metrics file.

3.6 Add unit tests `tests/test_ml_train.py` that run 1-epoch training on tiny dataset and verify output checkpoints created (0.5h). Acceptance: tests pass.

3.7 Add reproducible random seeds in training and data loader (0.2h).

3.8 Document hyperparameters and recommended small configs for smoke runs in `docs/experiments/training.md` (0.3h).

3.9 Run a smoke train locally (1 epoch) on toy data to verify end-to-end flow (0.5h). Acceptance: model checkpoints exist and metrics saved.

3.10 Add an example config YAML under `docs/experiments/configs/ml_small.yaml` containing the small experiment settings and exact commands to run (0.2h).

---

# 4. Bench integration & smoke pipeline (4.1–4.8)
4.1 Add `examples/bench_ml_channel.py` that accepts a `--channel` argument: `ids` (default), `ml:/path/to/model` (0.5h). Acceptance: script runs with `--channel ids` and produces `bench_rs.csv`.

4.2 Modify `examples/benchmark_rs.py` to accept a channel factory function (or channel object) so it can use MLChannel; keep backward compatibility (0.5h). Acceptance: running with `ids` behaves the same as before.

4.3 Implement a simple `ml_channel_factory(path)` that loads a saved MLChannel and returns object compatible with bench pipeline (0.5h). Acceptance: bench_ml_channel can call `ml_channel_factory` and get an object.

4.4 Create a smoke bench configuration (one S value, one coverage, 5 trials) and add a command in `docs/experiments/configs/bench_smoke.yaml` (0.2h). Acceptance: smoke bench runs in < 2 minutes.

4.5 Run the smoke bench comparing `ids` vs `ml` on toy model (trained previously) and store CSV outputs `bench_rs_smoke_ids.csv` and `bench_rs_smoke_ml.csv` (1h). Acceptance: both CSVs created and have identical columns.

4.6 Add a plotting script `examples/plot_bench_comparison.py` for quick visual check (0.5h). Acceptance: script produces a small PNG.

4.7 Add unit/integration test that runs bench with smoke config and asserts CSV files exist (0.3h). Acceptance: test passes in CI for smoke runs.

4.8 Update examples README with exact commands to run the smoke bench (0.2h).

---

# 5. Larger experiments & DoE runs (5.1–5.8)
5.1 Create a reproducible experiment runner `tools/run_experiments.py` that takes a YAML config describing grid points and runs benches in parallel (0.5h).

5.2 Encode the DoE grid from the plan into `docs/experiments/configs/bench_doe.yaml` with default trials=50 and seeds (0.3h). Acceptance: file present.

5.3 Implement result aggregation that writes per-grid CSV and a summary JSON (mean/std) under `benchmarks/` (1h). Acceptance: aggregated files produced for a sample run.

5.4 Start with a reduced DoE (one or two axes) for a short run to estimate runtime and resource needs (trials=20) (1h). Acceptance: run completes and provides runtime numbers.

5.5 Based on estimates, schedule full runs (50–200 trials) on available compute (1–2 days depending on resources). Record wall time and costs in `docs/experiments/compute.md` (estimate task 8h–24h depending on compute). Acceptance: full run completes and data stored.

5.6 Create scripts to reproduce main figures from aggregated CSVs (`tools/plot_main_results.py`) (2h). Acceptance: figures are reproduced and saved to `figures/`.

5.7 Add provenance metadata (config, git SHA, timestamp) to each results folder (0.2h). Acceptance: metadata files present.

5.8 Archive final benchmark data and add a small README describing how to load it (0.5h).

---

# 6. Ablations & sensitivity analyses (6.1–6.7)
6.1 Implement conditioning ablation configs (no context vs with context) and add configs under `docs/experiments/configs/ablation/` (0.5h). Acceptance: configs present.

6.2 Implement model-size ablation configs (small vs medium transformer) and add to ablation configs (0.5h).

6.3 Run ablation experiments (reduced trials 30) and collect metrics (1–2 days depending on size). Acceptance: ablation results produced and logged.

6.4 Produce ablation plots (bar charts & heatmaps) using `tools/plot_ablation.py` (2h). Acceptance: PNGs stored.

6.5 Write a short methods appendix describing ablation setup & hyperparameters (0.5h).

6.6 Add unit tests to ensure experiment runner handles ablation configs correctly (0.3h).

6.7 Summarize ablation findings in `docs/experiments/ablation_summary.md` (0.5h).

---

# 7. Analysis, figures, and writing (7.1–7.8)
7.1 Draft the main figures: recovery-vs-error curve, per-base log-likelihood curve, calibration plots and a table of main numbers (4h).

7.2 Write the methods section text with explicit training hyperparameters, dataset generation params and bench configs (3h).

7.3 Prepare results for the paper: export CSVs, tables, and compress figures into `paper_artifacts.zip` (1h).

7.4 Draft the introduction and related work section using references in `concise_guide.md` as starting points (2h).

7.5 Iterate the results/figures based on feedback and further runs (variable, 2–8h).

7.6 Prepare supplementary materials: dataset generation scripts, hyperparameter tables, and ablation details (3h).

7.7 Run a final reproducibility sweep using smoke CI configs to ensure key artifacts are rebuilt quickly (0.5h).

7.8 Prepare a submission checklist and pick venues (conference/journal) (1h).

---

# 8. Reproducibility & CI (8.1–8.6)
8.1 Add unit tests to cover new modules (ml_channel, gen_synthetic_reads, training harness) and mark fast tests (0.5h).

8.2 Add a GitHub Actions workflow `ci/smoke-ml.yml` that runs lint, unit tests, and one tiny train+bench smoke job using toy dataset (1.5h). Acceptance: workflow runs successfully on PRs.

8.3 Provide `requirements-ml.txt` or extras in `pyproject.toml` and document the optional install in `CONTRIBUTING.md` (0.2h).

8.4 Add a reproducible Dockerfile (optional) for full experiments `docker/Dockerfile.ml` that installs extras and runs smoke experiments; include instructions for how to run full DoE on the container (2h). Acceptance: Docker build succeeds.

8.5 Create a `RELEASE.md` entry explaining how to reproduce main figures and where benchmark data is stored (0.5h).

8.6 Tag a release candidate `v0.1-mlchannel` when artifacts + tests + docs are ready (0.1h). Acceptance: tag exists and is documented.

---

# 9. Final paper preparation & submission (9.1–9.5)
9.1 Finalize manuscript draft with figures and methods (2–6h for initial draft).

9.2 Collate supplementary files and ensure all scripts are runnable with examples (2h).

9.3 Run internal review and checklist (1–2 days) and collect co-author feedback (variable).

9.4 Prepare submission materials and cover letter; submit to chosen venue (time depends on venue and co-authors).

9.5 Post-submission: archive dataset & code at DOI (Zenodo/GitHub release) and prepare a short reproducibility README (1h).

---

## Acceptance notes & troubleshooting
- If any unit test fails, stop and report the failing test, exact command, and local environment output.
- If public datasets cannot be downloaded due to access restrictions, report the accession and we will run with synthetic-only and append a note in methods.
- Each subtask above is intentionally small; complete them in order and return status to maintain progress.

---

## Immediate next steps (execute now)
- Step 0.1 (create branch) → then 1.1 (implement generator) → 1.2 (schema) → 1.3 (sim utils) → create PR for skeleton of MLChannel (2.1–2.4) for early review and blocking feedback.


---

*Estimated total effort (prototype to draft): ~120–180 hours depending on compute time and iteration loops.*

