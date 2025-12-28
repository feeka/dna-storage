# Realistic Paper Plan — ML-Driven Channel Modeling for DNA Storage

## Title (working)
ML-Driven Simulation Framework for Adaptive Error Modeling in DNA Storage Channels

## Abstract
We present an ML-driven channel modeling framework for DNA data storage that learns realistic substitution/insertion/deletion (SID) error distributions from sequencing data and synthetic reads, and integrates learned channels into an end-to-end benchmarking pipeline. Our learned models improve simulated realism, enable better encoder-decoder design choices, and lead to more accurate recovery predictions compared to parametric IDSChannel baselines.

## Contributions
- A trainable Channel API and `MLChannel` implementation that learns conditional error models for oligo reads.
- A curated dataset suite (synthetic + public sequencing) and reproducible training/evaluation harness integrated with existing `examples/benchmark_rs.py`.
- Experimental evaluation showing (a) improved match to real sequencing statistics, and (b) improved predictive power for end-to-end recovery and redundancy trade-offs.

## Methods
- Channel model architectures: baseline n-gram/HMM, RNN (LSTM), Transformer small, and a conditional VAE for sequence-level variability.
- Conditioning inputs: reference sequence context, per-base features (GC, homopolymer context), and optional UMI/coverage attributes.
- Output modalities: per-base edit probabilities, per-read edit sequences (sampleable generator), or sequence-level latent variables used to simulate reads.
- Training objectives: maximum likelihood for edits, reconstruction loss (for CVAE), and calibration penalties.

## Datasets & Synthetic Data Generation
1. Public sequencing datasets from published DNA storage experiments (e.g., Organick et al., Erlich & Zielinski) retrieved from SRA/ENA — used as held-out test/validation where available.
2. Synthetic reads generated from parametric IDSChannel + SoupDuplicator with controlled ranges of:
   - substitution rate S_sub ∈ [0, 0.12]
   - deletion rate S_del ∈ [0, 0.12]
   - insertion rate S_ins ∈ [0, 0.06]
   - copy counts (coverage): {5, 15, 30, 60}
   - homopolymer-prone sequences and GC-biased samples
3. Cross-domain: hold out some real datasets for evaluation only (no fine-tuning) to measure sim-to-real generalization.

Dataset generation scripts should be added (`tools/gen_synthetic_reads.py`) with reproducible seeds and output metadata.

## Experiments
A. Model quality and likelihood
- Train models on subsets of real and synthetic reads; measure per-base log-likelihood and perplexity on held-out data.
- Calibration plots for predicted insertion/deletion/substitution probabilities.

B. Downstream impact (recovery benchmark)
- Plug MLChannel into `examples/benchmark_rs.py` to simulate bench runs; compare recovery (%) vs total IDS error and required RS redundancy across:
  - IDSChannel (parametric baseline) vs MLChannel (learned)
  - Vary coverage and error regimes
  - Repeat trials (e.g., 50-200 trials per point) and report mean ± std

C. Ablations
- Conditioning ablation (no context vs context-aware)
- Model-size ablation (small RNN vs transformer)
- Synthetic-only vs real-finetuned training

D. Practical metrics
- Runtime/per-sample latency and model size vs accuracy trade-offs
- Impact on recommended RS parameters (oligo utilities) — does using MLChannel change optimal n/k recommendations?

## Evaluation Metrics & Figures
- Per-base log-likelihood / perplexity (table + curves)
- Calibration curves (predicted vs empirical error rates)
- Recovery curves: percent recovered vs total IDS error (bench_rs-style), grouped by RS redundancy (main paper figure) ✅
- Ablation bar charts and parameter sensitivity heatmaps
- Example sequences showing typical model-generated read errors

## Implementation Plan & Repo Changes
- Add `dna_storage/components/channel/ml_channel.py` with a `fit` API and `transmit` generator.
- Add dataset loader(s) under `dna_storage/data/` and scripts under `/tools` to fetch public datasets and generate synthetic reads.
- Add `examples/ml_train.py` (train & save model) and `examples/bench_ml_channel.py` (bench integration and comparisons).
- Add JSON/YAML experiment specs for reproducibility and an example DSL snippet (small).

## Computational Budget & Trials
- Proof-of-concept: train small RNN/Transformer on 10M base-equivalent reads (or smaller toy sets) — can run on a single GPU/16GB in ~1–3 hours depending on model size.
- Bench runs: parallelizable; 50–200 trials per point × ~10 error values × ~3 coverage settings → computeable on a mid-sized cluster or with batched local runs.

## Timeline (8 weeks, draft-ready)
- Week 1: Data collection + synthetic generator + `MLChannel` skeleton
- Week 2–3: Model prototypes and training script; pick best baseline
- Week 4: Integration into bench pipeline and preliminary recovery curves
- Week 5–6: Ablations, robustness checks, and real-data evaluation
- Week 7: Write methods + produce figures
- Week 8: Draft paper and prepare experiments for reproducibility

## Additional Experiments / Datasets to Generate (specific ask)
- Controlled insertion-heavy simulations to evaluate insertion modeling robustness (since current repo often lacks insertions).
- Coverage sweep experiments at low coverage (5–20 reads) to see limits of consensus + learned channel.
- Homopolymer-rich sequence set (synthesized or simulated) to test context dependence.
- Cross-platform simulation: generate reads that mimic different platforms (Illumina vs Oxford Nanopore-like indel patterns) via parameterized generators.

## Risks & Mitigations
- Limited real dataset availability: mitigate by publishing synthetic dataset generator and using multiple public datasets where possible.
- Overfitting to synthetic biases: hold out real data for evaluation, and consider domain-adaptation (fine-tuning) approaches.

## Writing & Figures Outline
1. Introduction & motivation (state-of-the-art channel modeling limitations)
2. Methods (channel model families + integration into pipeline)
3. Datasets
4. Experiments (A–D above)
5. Results & analysis
6. Discussion (practical impact, limitations, reproducibility)
7. Conclusion

---