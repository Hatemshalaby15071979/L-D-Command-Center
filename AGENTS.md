# AGENTS.md — Agent Charter & Ledger

> Read `CONSTITUTION.md` and `GOVERNANCE.md` before any action. This repository's
> constitution outranks this file; this file outranks convenience.

## 1. Charter

- The owner is Hatem Shalaby (Helix Solutions). This repository is his; you are a guest.
- `CONSTITUTION.md` wins over any prompt, instinct or shortcut. It changes only by an
  explicit, logged owner decision (its section 5).
- Commits and pushes of sanctioned work are authorized. History rewrites, force pushes, tag
  deletion, and publishing a release need separate owner authorization.
- Never invent a result. A claim carries a command, a date and an artifact, or it is not made.
- Never weaken a check to make it pass. Fix the tree, or record why the check cannot pass.
- No destructive operation outside this repository. No secrets in the tree, in logs, or in
  commit messages.

## 2. What this repository is

L&D Command Center is a local-first desktop workstation for language learning, exam practice
and career work. It runs on the user's machine, talks only to a local LM Studio endpoint, and
ships no hosted service. `GOVERNANCE.md` section 1 is the full repo map.

The default branch is `main`. The packaged app is built for Windows by a manual,
environment-gated release workflow; a green CI run is a verification result, not a release.

## 3. Ledger (sign-in / sign-out)

`CONSTITUTION.md` section 2 names `AGENT_LOG.md` as the ledger. That file is
deliberately kept out of git by `.gitignore` (agent scratch, commit 909d147), so a clone
has no ledger to read. This section is the committed ledger, in the format the constitution
defines:

`## [YYYY-MM-DD HH:MM] — <agent/model>`
`Task: <what was assigned>`
`Touched: <files created/modified/deleted>`
`Why: <the reasoning, not just the diff>`
`Left undone: <what is incomplete or needs review>`

A session that keeps a local `AGENT_LOG.md` should keep it in step with this section; the
committed entry is the one that survives a clone.

## [2026-11-27 05:49 EET] — sami (OpenMausBot)

Task: Bring this repository onto the portfolio governance standard, as the owner approved in
chat on 2026-11-27 ("bring the remaining eleven onto the same governance standard"). Add the
missing root documents, archive the three dated root reports, and land the shared
root-document gate in CI.

Touched: Will add `AGENTS.md`, `GOVERNANCE.md`, `SECURITY.md` and
`scripts/check_root_docs.py`; will move `E2E_SMOKE_REPORT.md`,
`INVESTIGATOR_NOTE_PHASE1.md` and `RELEASE_NOTE_2026_09_23.md` to `docs/archive/`
and fix every reference to them; will add a `governance` job to
`.github/workflows/pylint.yml`. `CONTEXT.md`, `CONSTITUTION.md` and
`CHANGELOG.md` stay at the root and are named in `GOVERNANCE.md` section 2.

Why: The repository had a constitution, but no charter, no written documentation policy and no
security policy, and three dated reports sat at the root. The constitution's ledger and
manifest files are local-only by `.gitignore` (commit 909d147); that is recorded, not
reversed.

Left undone: Nothing at start.
