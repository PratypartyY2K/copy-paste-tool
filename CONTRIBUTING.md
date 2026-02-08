# Contributing

Thank you for considering contributing to App-Aware Clipboard Manager. This project follows a simple workflow designed to keep changes safe and reviewed.

Getting started
1. Fork the repository and create a branch for your change (feature/bugfix/test). Example:

```bash
git checkout -b feature/my-feature
```

2. Run the test suite locally and add tests for new behavior (especially for HistoryStore or watcher logic):

```bash
python -m pytest -q
```

3. Keep changes small and focused. Add tests for any behavior changes.

Pull request checklist
- [ ] My code follows the project's coding style and conventions.
- [ ] I have added required tests and they pass locally.
- [ ] I have updated README/DEVELOPMENT.md if the change affects usage or developer setup.
- [ ] I have run the test suite locally and fixed any failures.

Security & Privacy
- Default settings place the project in a privacy-conscious mode (Secret-safe ON and persistence OFF). If your change touches persistence, secret-detection heuristics, or anything that affects what gets stored, please call this out explicitly in your PR so reviewers can evaluate privacy implications.

Contributor responsibilities
- Be responsive to review comments and willing to iterate.
- Add tests for bug fixes and new features.

Migration note
- If your change touches the persistence schema (for example, the `board` column was removed), include migration scripts and add a dry-run mode so operators can inspect the effects before applying.

Packaging and releases
- Packaging and publishing (for example, signed macOS `.app`/`.dmg`) is deferred; maintainers will coordinate a release when ready. Contributors who want to help prepare a release can open an issue or PR with a proposed release checklist.

License
- This repository is licensed under the MIT License (see `LICENSE`). By contributing you agree to license your contributions under MIT as well.

Thank you!

Last updated: 2026-02-07
