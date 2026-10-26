# Releasing watergate-local-api

This is a public library on PyPI ([`watergate-local-api`](https://pypi.org/project/watergate-local-api/)). A release is **a pushed version tag**; everything after that is automatic and uses no private repository, GitHub App or long-lived token.

```
git tag + push  ->  test (py3.13, 3.14)  ->  build (isolated, twine check)  ->  [approval: environment "pypi"]  ->  PyPI (Trusted Publishing)  ->  GitHub Release
```

- **Version** = the tag, via `setuptools-scm` (no version file). CalVer `YYYY.N.P`: `N` counts releases of the year, `P` hotfixes. Existing tags are unprefixed (`2026.2.2`); a `v` prefix also works (`v2026.3.0` builds `2026.3.0`) but stay unprefixed for consistency.
- **Trigger** = a tag push, not "publish a Release". One deliberate action, protected by tag rules; the GitHub Release is *created by* the pipeline from the exact artifacts that were uploaded, so a Release can never exist without a published package.
- **Pre-release tags** (`2026.3.0rc1`, `a`, `b`, `.dev`) go to **TestPyPI only** and never to PyPI. They dry-run the whole pipeline.
- Workflows: `.github/workflows/release.yml` (pipeline), `test.yml` (tests, shared with PR CI).

## ONE-TIME SETUP (repository admin)

Do these in order before the first release with this flow. Nothing here needs a secret.

- [ ] **PyPI -> project `watergate-local-api` -> Manage -> Publishing**: add (or edit the existing one from #5) a *GitHub* trusted publisher: owner `watergate-ai`, repository `watergate-local-api-python`, workflow file `release.yml`, environment `pypi`.
- [ ] **TestPyPI** (<https://test.pypi.org>, separate account/project; create the project `watergate-local-api` there or add a *pending* publisher): same publisher with workflow `release.yml`, environment `testpypi`. Only needed for the rc dry-run.
- [ ] **GitHub -> Settings -> Environments -> New environment `pypi`**: enable **Required reviewers** (add yourself and one more maintainer), enable *Prevent self-review* if there are 2+ reviewers, restrict **Deployment branches and tags** to the tag patterns `[0-9]*.[0-9]*.[0-9]*` and `v[0-9]*.[0-9]*.[0-9]*`. Add no secrets.
- [ ] **GitHub -> Settings -> Environments -> New environment `testpypi`**: no reviewers needed; same tag restriction. Add no secrets.
- [ ] **GitHub -> Settings -> Rules -> Rulesets -> New tag ruleset**: target tags `*.*.*` (and `v*.*.*`); rules *Restrict creations*, *Restrict updates*, *Restrict deletions*; bypass only the maintainers who may release.
- [ ] **GitHub -> Settings -> Actions -> General**: *Workflow permissions* = read-only (the workflows declare their own), allow GitHub-authored and `pypa/*` actions (they are pinned by SHA).
- [ ] Merge the release-flow PR. Close PR #7 and remove any variables/secrets/App installations that were added for it.

## Pre-flight (every release)

1. `main` is green (PR CI: tests + OSV scan) and contains everything you want to ship.
2. Decide the version: next number after the latest tag of the year (`git fetch --tags && git tag --sort=-v:refname | head -3`). `2026.3.0` for a new release, `2026.3.1` for a hotfix of it.
3. Optional local check: `python -m venv .venv && . .venv/bin/activate && pip install build twine && python -m build && twine check --strict dist/*`.

## Cut a release

```sh
git switch main && git pull --ff-only
git tag -a 2026.3.0 -m "2026.3.0"
git push origin 2026.3.0
```

Then open **Actions -> Release**: after `test` and `build` pass, the `publish-pypi` job waits for approval on the `pypi` environment - a required reviewer clicks **Review deployments -> Approve**. The workflow refuses a tag that is not on `main`, and fails if the built version differs from the tag.

First time under this flow, do the dry run first: push `2026.3.0rc1` (publishes to TestPyPI, creates a GitHub *pre-release*), check it, then tag the real release. Tags cannot be reused: the real release is a new tag on the same or a later commit.

## Verify

- PyPI shows the new version: <https://pypi.org/project/watergate-local-api/#history> (and "Provenance"/attestations on the file page).
- `python -m venv /tmp/v && /tmp/v/bin/pip install watergate-local-api==2026.3.0 && /tmp/v/bin/python -c "import importlib.metadata as m; print(m.version('watergate-local-api'))"` (PyPI can take a minute to serve it).
- The GitHub Release exists with the sdist and wheel attached and generated notes.

## Hotfix

Fix on `main` via a normal PR, then tag the next patch (`2026.3.1`) exactly as above. (Releases are cut from `main` only; if you ever need to patch an older line without the newer commits, that needs a separate maintenance branch and a change to the "tag is on main" guard in `release.yml`.)

## Rollback

**Never delete a tag, a Release or a PyPI file** - consumers and PyPI's immutability depend on them. Instead: on PyPI -> project -> Manage -> the bad release -> **Yank** (installers skip it unless pinned exactly), then release a fixed version. Mark the GitHub Release text as broken if useful.

## When something fails

| Symptom | Fix |
|---|---|
| `Tag ... is not on main` | Tag the commit on `main`; delete the *unpublished* wrong tag (`git push --delete origin <tag>`), re-tag. |
| `tag X != built Y` | The checkout lacked history/tags or the tag is malformed; use `YYYY.N.P[rcN]`. |
| `publish-*` fails with *invalid-publisher* / 403 | The trusted publisher on (Test)PyPI does not match owner/repo/`release.yml`/environment exactly. Fix it there and re-run the job. |
| `publish-pypi` never starts | Waiting for environment approval, or the tag doesn't match the environment's allowed tag patterns. |
| *File already exists* on PyPI | That version was already uploaded: never re-upload; release the next patch. |
| `github-release` fails after PyPI succeeded | Re-run just that job (the package is already published). |
