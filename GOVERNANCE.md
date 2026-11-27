# GOVERNANCE.md — Operating Policy & Repo Map for L&D Command Center

> Companion to `CONSTITUTION.md` (this project's own engineering constitution) and
> `AGENTS.md` (the agent charter). Read all three before acting. This file may be updated
> by any agent **as a logged governance change**; the CONSTITUTION is owner-only.

## 1. Repository map

| Path | Purpose (one line) |
|---|---|
| `engines/` | The product engines, one directory each: `journey-core`, `career-engine`, `audio-engine`, `export-engine`, `language-lab`, `playground-bridge`. |
| `model-layer/` | The local-model client. It talks to LM Studio on `localhost`; nothing leaves the machine. |
| `storage/` | Local persistence for journeys, cards and user content. |
| `desktop_shell/` | The Tk desktop application and its controller. |
| `assets/` | Bundled images, audio and lesson-pack assets. |
| `docs/` | Plans, runbooks, research and the archive. |
| `docs/archive/` | Historical reports and release notes (section 4). |
| `tests` / `test_app_load.py` / `gui_smoke.py` / `smoke_headless.py` | The suite, the app-load test and the two smoke harnesses. |
| `run_checks.sh` / `run_checks.bat` / `RUN_APP.bat` / `RUN_LDCC.bat` | Local verification and launch scripts. |
| `requirements.txt` / `pytest.ini` | The pinned toolchain and the pytest configuration (`testpaths`, `not live` by default). |
| `.github/workflows/` | `pylint.yml` (quality + the root-document gate), `python-app.yml`, `windows-build.yml`, `release.yml` (manual, environment-gated), `codeql.yml`, `gitleaks.yml`, `docs-sync.yml`. |

The packaged app targets Windows; the code and the suite run on Linux and macOS too. There is
no hosted service, no account and no telemetry.

## 2. Documentation policy (what belongs where)

**Root holds only the requested set** — nothing else:

| File | State | Purpose |
|---|---|---|
| `README.md` | required | The single source of truth for a reader: what this is, how to run it, what it needs. Carries the Helix Solutions logo. |
| `AGENTS.md` | required | Agent charter and the rules a session must follow. |
| `CONSTITUTION.md` | required | This project's own engineering constitution, written before the portfolio text existed. It outranks the portfolio constitution here; it is owner-only and amended only by a logged owner decision (its section 5). |
| `GOVERNANCE.md` | required | This file: repo map, documentation policy, status-truth policy, archiving rules. |
| `CONTEXT.md` | required | The living domain glossary. Code comments and engine READMEs cite it by name, so it stays at the root. |
| `CHANGELOG.md` | standard | Dated, user-visible changes. |
| `LICENSE` / `LICENSE.md` | standard | MIT. |
| `SECURITY.md` | standard | Security policy and private reporting route. |

**Everything else lives in `docs/`** — plans, reports, research, ADRs, runbooks, anything
dated or one-off. No stray `.md`/`.txt` at the root. If a document at the root is not in
the table above, move it to `docs/` (or `docs/archive/` if it is historical) and record
the move in `AGENTS.md` section 3.

`requirements.txt` is a package manifest, not a document: pip resolves it relative to the
working directory, so `docs/` is not an option.

**Local-only files, deliberately untracked.** `.gitignore` keeps `AGENT_LOG.md`,
`FILE_MANIFEST.md`, `TASKS.md`, `MASTER_STORY.md` and `BOOT_ROOT.md` out of the
public tree as agent scratch (commit 909d147, "docs: stop tracking generated agent scratch
logs"). They exist on a working machine and not in a clone. The committed ledger is
`AGENTS.md` section 3, which names this arrangement so a fresh clone is not missing a
document it was never meant to hold. A landing that would satisfy the constitution's
`FILE_MANIFEST.md` requirement records that the file is local-only rather than claiming it
is current.

## 3. Status truth policy

`README.md` is the canonical account of what the app is and what it needs. The status block
(version, release date, tests, CI) is refreshed by the shared `docs-sync` action on a
published release; it opens a pull request and never commits to the branch.

A green CI run proves the checks passed on that commit. It is not a release decision: the
release workflow is manual, runs on Windows, and is gated by the `release` environment,
which must have a reviewer configured.

## 4. Archiving rule

- Archive (move to `docs/archive/`), never delete: historical reports, superseded plans,
  dated audits, release notes and one-off execution logs.
- Delete outright only regenerable artifacts: caches, build output, coverage files.
- Fix the links inside a moved document and the links pointing at it in the same landing.
- Record every move in `AGENTS.md` section 3 with date and time.

## 5. Engineering philosophy (operational summary)

The full text is `CONSTITUTION.md`. The reminders, enforced here:

- **Fail closed.** Missing input, an unloaded model or an unclear authority is a refusal,
  never a default.
- **Evidence before claims.** Every published number carries a command, a date and an artifact.
- **No duplicates, no temp files, one file one job, every file explains itself.**
- **Secrets never enter the tree.** The signing material lives in repository secrets, never here.
- **Simple English** in code, docs and UI.
- **One brand mark:** the Helix Solutions logo, everywhere.

## 6. Definition of done

It works; it has a test or a documented manual check; `AGENTS.md` section 3 has an entry; the docs
reflect the new reality; no temporary file was left behind; and every published number can be
re-run to reproduce itself. Where the constitution's `FILE_MANIFEST.md` requirement cannot
be met, the entry says so explicitly.
