# Changelog

All notable changes to this project will be documented in this file.
This project is a work-in-progress — expect breaking API changes in early versions.

## [Unreleased]
- Tests and smaller tweaks

## [0.1.0] - Feature release (WIP)
- Reed–Solomon encoder/decoder implemented (GF(256), interpolation-based erasure recovery)
- Oligo helper utilities added (`recommend_rs_parameters`, `pretty_recommendation`) for computing recommended n/k/chunk_size given oligo length and overhead
- Pipeline checks for encoder sizing and optional oligo warnings
- SimpleAligner + channel simulators (IDSChannel, SoupDuplicator) and many integration tests


## [0.0.1] - Initial prototype
- Initial scaffolding and component examples
