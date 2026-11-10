# Changelog

All notable changes to L&D Command Center are documented here. The project
follows a simple chronological format (newest first).

## Unreleased

### Removed
- **Kokoro TTS backend removed.** The `KOKORO` value of `TtsBackend`, the
  `KOKORO_IMPLEMENTED` flag, the `_synthesize_kokoro()` stub, the
  `KOKORO_LANGUAGE_VOICES` catalog, and all Kokoro-routing branches in
  `narration.py` / `voice_catalog.py` have been deleted.

  **Why:** Kokoro-82M was never implemented — every code path raised
  `NotImplementedError` and was gated behind `KOKORO_IMPLEMENTED = False`.
  Shipping a stub that always fails is a defect, not a feature. Per the
  owner's decision, the unimplemented backend is removed rather than kept
  as documentation.

  **Intended future enhancement:** Kokoro remains a *possible* future
  backend. If/when a real tokenizer + phoneme encoder is integrated, it can
  be re-added behind a genuine implementation — Piper stays the supported,
  default, offline-first engine in the meantime.

### Changed
- `narration.py` and `voice_catalog.py` now resolve voices **Piper-only**.
  `narrator_voice()` and `has_language()` no longer take a `backend`
  argument.
- `TtsBackend` is now a single-value enum (`PIPER`). `synthesize()` and
  `get_available_voices()` accept only `PIPER`; any other value raises
  `ValueError`.
- `requirements.txt`: dropped the `kokoro==not-implemented` placeholder
  comment; Piper is the sole TTS dependency.

## [1.0.0] - 2026-11-10

First tagged release anchor. Establishes the version single-source-of-truth
(`desktop_shell/__init__.py::__version__ = "1.0.0"`) so the git tag `v1.0.0`,
this entry, and the code constant agree.

### Packaging & release
- Windows desktop build via PyInstaller 6.22.2 (Python 3.10 baseline),
  Authenticode signing (optional; unsigned builds are allowed and flagged),
  SHA-256 build manifest, and a human-approved (`environment: release`)
  GitHub Release workflow.
- CI: `windows-build.yml` validates the build on every `main` push touching
  `desktop_shell/**`; `release.yml` is manually dispatched and gated.

### Quality
- Offline suite (live tests deselected): 1051 passed at the time of tagging.
- 90% coverage floor enforced locally via `run_checks.sh` (added to CI in the
  shipment-readiness pass).

### Security hygiene
- `secrets/`, `models/`, `.env`, `*.secrets` are git-ignored and excluded from
  the bundle by `desktop_shell/check_deployment_policy.py`.
- Gitleaks config (`.gitleaks.toml`) and Dependabot/CodeQL added post-tag in the
  shipment-readiness pass.
