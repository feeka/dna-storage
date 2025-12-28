# DNA Storage — Project & Paper Ideas

**Repository quick findings (from sweep):**

- Key components: `IDSChannel` (substitutions + deletions), `SoupDuplicator` (multiple reads), `SimpleAligner`, `RS` encoder/decoder (GF(256) interpolation erasure decoder), `RSInnerChannel`, mappers and oligo utilities.
- Benchmarks present (examples/benchmark_rs.py → `bench_rs.csv`) and plotting utilities.
- Current limitations: decoder is erasure-only (no substitution correction), channel omits insertions in many places, aligner is simple (not weighted/MSA), inner/outer coding modularity present.

---

## Suggested Paper / Project Ideas

### 1) ML-Driven Simulation & Channel Modeling Framework
- Short title: "ML-Driven Simulation Framework for Adaptive Error Modeling in DNA Storage Channels" ✅
- Abstract: Use ML (probabilistic sequence models, e.g., RNNs/transformers, or conditional VAEs) to learn per-base/substitution/insertion/deletion error profiles from real sequencing datasets or synthetic reads, and plug the learned model as a pluggable `Channel` in the repo.
- Hypothesis: Learned channel models produce more realistic recovery curves and enable designing encoders (inner/outer) that are robust to real error distributions.
- Required repo work: Add a trainable Channel API, dataset loader, model scaffolding, evaluation harness, and comparisons against parametric IDSChannel/SoupDuplicator.
- Experiments & metrics: likelihood on held-out reads, recovery (percent recovered) in bench_rs-style experiments, calibration tests, ablations vs hand-tuned channels.

### 2) Adaptive Decoding with ML-assisted Consensus & Soft Inputs
- Short title: "Soft-Input Consensus and ML-assisted Decoders for DNA Storage" ⚡
- Abstract: Replace SimpleAligner with an ML model that produces per-position soft beliefs (class probabilities or symbol logits) and feed soft inputs to an RS or neural decoder (learned or hybrid) that can use soft information to correct substitution/erasure patterns.
- Hypothesis: Soft inputs increase effective code rate and reduce required redundancy under realistic error regimes.
- Repo work: Modify aligner API to output probabilistic consensus; implement soft-input RS (list-decoding or approximations) or a neural decoder; extend pipeline to accept soft channels.
- Experiments: Recovery vs redundancy curves at varying S and coverage, comparing hard consensus + RS vs soft consensus + decoder.

### 3) DSL for DNA Storage Pipelines (Reproducible Experiments & Standards)
- Short title: "A DSL for Reproducible DNA Storage Experiments and Benchmarks" 🧩
- Abstract: Design a small, declarative domain-specific language (YAML/JSON/mini-TOML) to describe full pipelines (input parameters, mapper, inner/outer codes, channel model, aligner, metrics), enabling reproducible, shareable experiments and standardizing reporting.
- Hypothesis: A DSL reduces friction and improves reproducibility and benchmarking across groups.
- Repo work: Implement parser and runner, CLI extension, example spec files, and a VSCode/JSON schema for validation.
- Experiments: Reproduce existing bench runs, cross-validate with external published experiments.

### 4) Design-of-Experiments (DoE) for DNA Storage Parameter Optimization
- Short title: "Systematic DoE for Parameter Optimization in DNA Storage Pipelines" 🧪
- Abstract: Use DoE and Bayesian optimization to explore the high-dimensional parameter space (oligo_len, RS n/k, inner-code rate, coverage, sub/del rates) to find Pareto-optimal trade-offs between redundancy, recovery, and cost.
- Hypothesis: Automated DoE yields better encoder/oligo configurations than manual heuristics.
- Repo work: Add DoE driver, wrappers for bench runs, logging and visualization dashboards.
- Experiments: Multi-objective optimization, hyperparameter landscapes, recommended parameter tables.

### 5) Standards & Benchmarking Suite (Datasets, Formats, Metrics)
- Short title: "Towards Standard Benchmarks for DNA Storage: Datasets, Metrics and Baselines" 📊
- Abstract: Formalize a benchmark suite: curated channel datasets (simulated + public sequencing), canonical pipelines, baseline results and reporting formats (bench_rs.csv as a starting point).
- Hypothesis: A community benchmark accelerates progress and enables fair comparisons.
- Repo work: Add dataset downloaders, canonical configs, CI tests to regenerate key plots, and a compact leaderboard.
- Experiments: Provide baseline results for several pipelines and recommend evaluation metrics (mean recovery, latency, complexity, synthesized oligo length).

### 6) Inner Code Design for Indel Resilience (VT/VT-like codes) and Analysis
- Short title: "Inner Code Design and Empirical Analysis for Indel Resilience in DNA Storage" 🔧
- Abstract: Implement inner synchronization codes (VT codes, marker-based schemes), measure consensus behavior, and quantify benefits when combined with outer RS codes.
- Hypothesis: Adding a lightweight inner code improves recovery at low cost and reduces needed outer redundancy.
- Repo work: Implement VT encoder/decoder, integrate into RSInnerChannel and run benchmarks.
- Experiments: Recovery vs S with/without inner codes across coverage levels and aligners.

### 7) Learned Mappers & Constrained Sequence Design
- Short title: "Learning Sequence Mappers under Biological Constraints" 🧬
- Abstract: Use ML to learn mappers from bytes → oligo subject to GC/ homopolymers / secondary structures constraints, balancing coding rate and sequencing error sensitivity.
- Repo work: Plugin mapper that is learned (neural mapper) vs classic rotating mapper; simulation & evaluation.
- Experiments: Error rates, recovery, biochemical metric distributions (GC/homopolymers) on generated oligos.

### 8) End-to-end Differentiable Pipeline & Neural Decoders
- Short title: "End-to-end Differentiable Emulation of DNA Storage Pipelines for Data-driven Code Design" 🤖
- Abstract: Build a differentiable surrogate for pipeline components (mapper, channel, aligner approximations) and train neural encoders/decoders end-to-end to maximize recoverability under constraints.
- Hypothesis: Data-driven codes adapt to realistic error modes and can improve resilience where classic codes are suboptimal.
- Repo work: Build differentiable approximations and small-scale training harness; begin with toy tasks and measure generalization.
- Experiments: Sim-to-real evaluation; compare to RS baselines.

---

## Prioritization & Quick-win recommendations
1. ML-Driven Channel Modeling (1) + integrate into `examples/benchmark_rs.py` — high impact, incremental on channel API. ✅
2. Soft-consensus + soft-input decoder (2) — moderate complexity, strong expected gains.
3. DSL for experiments (3) — medium effort, big reproducibility payoff.
4. DoE harness (4) — good companion to any experiment-driven project.
5. Standards & Benchmarks (5) — ongoing community project; can start by formalizing `bench_rs.csv` schema.

---

## Minimal Next Steps (implementation tasks)
- Create `docs/project_ideas.md` (this file) and `docs/project_ideas.html` (HTML view).
- Add a training-ready Channel subclass skeleton (e.g. `MLChannel`) with a `fit` method and a `transmit` method.
- Add an `Aligner` interface change to allow probabilistic-consensus outputs.
- Add example configs (YAML) for a DSL prototype and an example experiment spec.

---

## Contact / Follow-up
If you want, I can:
- Generate a PR scaffold implementing `MLChannel` and a small training example.
- Draft an article outline (abstract, intro, methods, experiments, expected figures) for any selected idea.

---

*Generated from an automated sweep of the repository; open an issue for any specific idea you'd like prioritized.*
