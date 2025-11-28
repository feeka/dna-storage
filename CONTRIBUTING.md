# Contributing to dna-storage (concise)

Follow these short guidelines so contributions are fast and useful.

1. Scope
   - Small, well-tested modules or bug fixes are easiest to accept.
   - Big design changes: open an issue first to coordinate.

2. Branches & workflow
   - Develop on a branch (feature/ descriptive-name). Rebase/merge to `main` via PR.
   - Use semantic versioning for releases (see `VERSION`) and create tags like `v0.1.0`.

3. Tests
   - Add unit tests for new functionality. We use pytest for quick verification.

4. Style
   - Keep implementations readable and documented. Small, well-scoped files preferred.

5. Releases and versioning
   - The project uses Semantic Versioning (MAJOR.MINOR.PATCH).
   - For breaking changes increment MAJOR; new features increment MINOR; fixes increment PATCH.
   - Add a `CHANGELOG.md` entry under `Unreleased` for any change that should be recorded.

Release checklist
- Update `CHANGELOG.md` (move Unreleased entries to the new version header)
- Bump `VERSION` file to the new version (e.g. 0.1.0 → 0.2.0)
- Run the test suite and ensure CI passes
- Tag the commit in git: `git tag vX.Y.Z` and push the tag

Notes on unstable APIs
- This repository is actively changing — maintainers may make breaking changes in minor versions until we've reached a stable 1.0.0.

6. License & code of conduct
   - Respect the repository license. If you add external code, ensure compatible licensing and attribution.

Quick command examples
```bash
# run the example
python3 -m dna_storage.examples.basic_rs_pipeline

# run tests
python3 -m pytest -q
```

That's it — keep changes small and focused. Thanks! ✨
