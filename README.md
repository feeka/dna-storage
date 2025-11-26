# dna_storage — modular DNA-as-storage library

This repository contains a small, modular framework for simulating DNA-based data storage systems. The architecture keeps each stage pluggable so researchers and developers can implement different algorithms and experiments easily.

Structure

- core/: abstract interfaces and pipeline orchestrator
- components/: inputters, encoders, mappers, channel simulators and decoders
- utils/: helpers and field arithmetic
- examples/: runnable pipelines

Quick start

1. Run the example pipeline (Python 3.8+):

```bash
python -m dna_storage.examples.basic_rs_pipeline
```

Feel free to add more encoders, mappers, or channel simulators as separate modules.
