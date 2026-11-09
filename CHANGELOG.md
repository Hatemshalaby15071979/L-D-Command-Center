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
