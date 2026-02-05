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

CI and test expectations
------------------------
- This repository runs tests in GitHub Actions (`.github/workflows/ci.yml`). The CI runs GUI tests under Xvfb so pytest-qt tests run in headless CI environments.
- The CI enforces a minimum coverage threshold (default 70%). Make sure your changes are covered by unit tests or GUI tests to avoid CI failures.
- Coverage reports are uploaded to Codecov; a Codecov badge is included in the README.

Codecov token (required for uploads)
-----------------------------------
If this repository is private, or if Codecov requires a token for uploads, create a repository secret named `CODECOV_TOKEN`:

1. In the Codecov project settings copy the upload token.
2. In GitHub: Settings → Secrets and variables → Actions → New repository secret
   - Name: CODECOV_TOKEN
   - Value: (paste the token)

If the token is missing, the CI step that uploads coverage to Codecov will be skipped or report an error; set the secret and re-run the workflow.

Run pytest locally (recommended)
-------------------------------
Install pytest and GUI test deps and run tests with coverage:

```bash
python -m pip install -r requirements-ci.txt
pytest -q -m "not gui" --cov=clipboard_manager --cov-report=term-missing
```

If you want to emulate CI locally (headless), run with Xvfb:

```bash
sudo apt-get install xvfb
xvfb-run -s "-screen 0 1920x1080x24" pytest -q --cov=clipboard_manager --cov-report=xml
```

Pull request checklist
----------------------
- [ ] Code compiles and existing tests pass locally.
- [ ] New behavior is covered by tests where applicable.
- [ ] Add/update documentation (README/DEVELOPMENT.md/PERSISTENCE.md) as needed.
- [ ] Ensure no secrets (API keys, credentials) are committed.

License and contribution rights
-------------------------------
This project is released under the MIT License. By submitting a pull request you agree to license your contribution under the same MIT License and grant the project maintainers the right to incorporate your changes under that license. See the `LICENSE` file in the repository root for the full license text.

Review process
--------------
- PRs are reviewed by maintainers. Expect feedback and iterations.
- Maintain a friendly, constructive tone; explain design choices in the PR description.

Branching
---------
- `main` holds the latest stable code. Create feature branches off `main` and open PRs against `main`.

Contributing
------------
- Create a branch, add tests for behavior changes (HistoryStore unit tests are quick), run the test scripts, and open a PR.
- Helpful areas: persist history, image/rich clipboard support, improve token heuristics, better search (fuzzy matching), keyboard shortcuts.

Contact
-------
If you need help or want to discuss architecture, open an issue or a draft PR and invite reviewers.

Last updated: 2026-02-05
