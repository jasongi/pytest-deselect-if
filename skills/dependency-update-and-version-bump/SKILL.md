---
name: dependency-update-and-version-bump
description: Update supported Python versions, bump GitHub Actions and pre-commit hook pins to their current releases, verify against the latest release of the project's test framework, and cut a patch version bump. Use when asked to update Python support, refresh CI/pre-commit tooling versions, or check compatibility with a new major dependency release.
---

# Dependency update and version bump

Applies to a Python package repo that declares supported Python versions in
`pyproject.toml`, runs a `tox.ini` matrix, tests via GitHub Actions, and lints
via `pre-commit`. Written to be followed by any coding agent with shell and
file-edit access — no tool names below are specific to one harness.

## 1. Inventory what currently pins a version

Search the repo for every place a Python version, GitHub Action, or
pre-commit hook revision is declared, so nothing is updated inconsistently:

- `pyproject.toml`: `requires-python` and the `Programming Language :: Python :: 3.x`
  classifiers.
- `tox.ini`: the `envlist`.
- `.github/workflows/*.yml`: `python-version` fields and any
  `matrix.python-version` list, plus every `uses: owner/repo@ref` line.
- `.pre-commit-config.yaml`: `default_language_version.python` and each
  hook's `rev:`.
- `CHANGELOG.md` and any badge/version string, to confirm nothing else
  hardcodes a version number.

Grep broadly for version-looking strings (`3\.\d+`, `py3\d+`, action/hook
revs) across `*.toml`, `*.ini`, `*.yml`, `*.yaml`, `*.md`, `*.rst` rather than
trusting one file to be authoritative.

## 2. Decide the target Python versions

Check the real end-of-life status of each currently-supported version and the
latest stable release — don't guess from training knowledge, verify live
(e.g. a web search against endoflife.date, or the official CPython downloads
page). As of the check:

- Add the newest stable CPython release if it's missing.
- Drop any version that has reached its EOL date.
- Leave versions that are older but still supported (a version "close to EOL
  but not there yet" stays).

Apply the resulting version set consistently to `requires-python`, the
classifiers, `tox.ini`'s `envlist`, and the GitHub Actions matrix. If
`requires-python` moves up (a floor is dropped), also bump any
`--pyXY-plus`-style flag passed to code-upgrading pre-commit hooks (e.g.
pyupgrade) to match the new floor.

## 3. Bump GitHub Actions pins

For each `uses: owner/repo@ref` line, resolve the action repo's latest
release tag (`curl -s https://api.github.com/repos/<owner>/<repo>/releases/latest`,
or fall back to listing tags if the repo has no GitHub Releases) and update
the pin. Do this for every action used across every workflow file, not just
the ones already spotted — checkout, setup-language, upload-artifact,
download-artifact, and any publish/deploy actions are commonly out of date
together.

## 4. Bump pre-commit hook revisions

For each `repo:`/`rev:` pair in `.pre-commit-config.yaml`, find the latest
tag directly from the hook's git remote rather than trusting a cached
package index page:

```
git ls-remote --tags --refs https://github.com/<owner>/<repo>.git \
  | awk -F/ '{print $NF}' | sed 's/^v//' | sort -V | tail -1
```

Watch for two traps this surfaces:

- **Renamed/transferred repos** (an old `owner/repo` URL 301-redirects to a
  new one). The old URL still works for pinning, but query tags at the new
  location to be sure you're seeing the true latest.
- **Mixed tag prefixes within one repo's history** (some releases tagged
  `v1.2.3`, later ones tagged `1.2.3` with no `v`). Strip the `v` before
  sorting, then check the winning tag's *actual* ref format (with or without
  `v`) before writing it into the pin — don't assume.
- **Untagged releases**: if the package index (PyPI, npm, etc.) has a newer
  version than any git tag, the maintainer stopped tagging — pin to the
  latest version that *does* have a tag, since pre-commit needs a real git
  ref.

Also bump the pinned tool version anywhere it's duplicated, e.g. a
`additional_dependencies: [black==X.Y.Z]` line on a docs-formatting hook that
must match the primary formatter's version.

## 5. Apply and reconcile the tooling bump

Run the full pre-commit hook suite over the whole repo once the revisions are
updated. Newer tool versions commonly auto-rewrite code (a linter's
autofixer applying a new style rule, an upgrader targeting the new Python
floor). Let it run, inspect the resulting diff file-by-file, confirm it's a
legitimate style/upgrade change (not a semantic change), then re-run the
suite to confirm it's now clean.

## 6. Verify against the latest release of the test framework

Look up the latest release of the project's test framework (e.g. pytest) on
its package index. Create an isolated virtual environment, install that
latest version plus the package under test in editable mode, and run:

- the full test suite,
- once more with warnings promoted to errors, to catch silent deprecations,
- the project's coverage command, checked against its existing coverage
  floor.

If everything passes, no code changes are needed for compatibility — record
that verification in the changelog/commit rather than skipping it silently.
Clean up the scratch virtual environment afterward.

## 7. Bump the version and changelog

Bump the package version by whatever scheme the project already uses (a
patch bump for a tooling/support update is typical) in the one place that
defines it — re-check that a version string isn't duplicated somewhere the
initial inventory (step 1) already ruled out. Add a changelog entry dated
with the actual current date, listing each user-visible change (versions
added, versions dropped and why, framework compatibility verified).

## 8. Commit

Stage everything the update touched — config, workflow, changelog, and any
files the tooling bump auto-reformatted — into one commit. Match the
repo's existing commit message style (check `git log` for prior similar
bumps first). Push only after the user confirms; if the environment lacks
push credentials, hand back the exact push command for the user to run
elsewhere rather than silently leaving it uncommitted.
