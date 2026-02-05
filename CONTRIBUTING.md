CONTRIBUTING
============

Thanks for considering contributing! This file documents the preferred workflow for contributing changes, running tests, and opening a pull request.

Getting started
---------------
1. Fork the repository and create a new branch for your work. Use descriptive branch names like `feat/persistence-json` or `fix/clipboard-dedupe`.

2. Implement your changes and add tests when appropriate. Small focused PRs are preferred.

3. Run the project's test scripts locally before pushing:

```bash
source .venv/bin/activate
python tests/test_utils.py
python tests/test_secret_safe.py
python tests/test_pins.py
python tests/smoke_pause_test.py
python tests/gui_startup.py
```

Coding guidelines
-----------------
- Keep public APIs of modules stable where possible. Backwards-compatible changes are preferred.
- Add tests for bug fixes and new features. Keep tests fast and deterministic.
- Use small, focused commits with clear messages.

Pull request checklist
----------------------
- [ ] Code compiles and existing tests pass locally.
- [ ] New behavior is covered by tests where applicable.
- [ ] Add/update documentation (README/DEVELOPMENT.md/PERSISTENCE.md) as needed.
- [ ] Ensure no secrets (API keys, credentials) are committed.

Review process
--------------
- PRs are reviewed by maintainers. Expect feedback and iterations.
- Maintain a friendly, constructive tone; explain design choices in the PR description.

Branching
---------
- `main` holds the latest stable code. Create feature branches off `main` and open PRs against `main`.

License and contribution rights
-------------------------------
By opening a pull request you agree to license your contribution under the repository's license. If you want a different arrangement, state it clearly when opening the PR.

Contact
-------
If you need help or want to discuss architecture, open an issue or a draft PR and invite reviewers.

Last updated: 2026-02-04
