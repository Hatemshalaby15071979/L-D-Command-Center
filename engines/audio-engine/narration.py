# engines/audio-engine/narration.py
#
# WHAT: Text-to-speech narration function that synthesizes text into audio
#       files (WAV + MP3) using the model-layer TTS client.
# WHY:  Provides a simple, unified interface for audio generation across
#       engines — takes any text (Journey cards, Resume summaries, or
#       arbitrary text) and produces audiobook-quality audio.
# BREAKS IF DELETED: Audio generation capability is lost; export-engine and
#       language-lab can't produce audio output.
#
# Backend: Piper is the sole implemented TTS engine. narration auto-selects
#   Piper for every language; an explicit backend override (Piper) is honored
#   as-is — the caller owns it.
#
# Audio output:
#   - WAV is written first (lossless, preserves all TTS output)
#   - MP3 is generated from WAV using ffmpeg (available in environment)
#   - Both formats are returned as bytes; optional file paths can be provided

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from engines.audio_engine import assembly, voice_catalog
from model_layer.tts import TtsBackend


# ---------------------------------------------------------------------------
# Constants — voice tables live in the Voice Catalog (P2.3); these aliases
# keep the historical module names importable for callers and tests.
# ---------------------------------------------------------------------------

DEFAULT_PIPER_VOICE = voice_catalog.PIPER_LANGUAGE_VOICES["en"]
DEFAULT_SAMPLE_RATE = assembly.DEFAULT_SAMPLE_RATE

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class NarrationResult:
    """Result of narration synthesis."""
    wav_bytes: bytes
    mp3_bytes: bytes
    sample_rate: int
    backend_used: TtsBackend
    voice_used: str


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _detect_language(text: str) -> str:
    """
    Detect the language of the input text.

    This is a simple heuristic based on character patterns. For production
    use, consider using a language detection library like langdetect.

    Returns:
        Language code (e.g., 'en', 'es', 'fr') or 'en' as fallback.
    """
    # Simple heuristic: check for common patterns
    # This is a placeholder — real implementation would use a library

    # Count character ranges
    latin_extended = sum(1 for c in text if 'Ā' <= c <= 'ſ')
    cyrillic = sum(1 for c in text if 'Ѐ' <= c <= 'ӿ')
    cjk = sum(1 for c in text if '一' <= c <= '鿿')
    arabic = sum(1 for c in text if '؀' <= c <= 'ۿ')
    hindi = sum(1 for c in text if 'ऀ' <= c <= 'ॿ')

    total = len(text.replace(' ', ''))
    if total == 0:
        return "en"

    ratios = {
        "cjk": cjk / total,
        "arabic": arabic / total,
        "hindi": hindi / total,
        "cyrillic": cyrillic / total,
        "latin_extended": latin_extended / total,
    }

    # Simple detection rules
    if ratios["cjk"] > 0.1:
        return "zh"
    elif ratios["arabic"] > 0.1:
        return "ar"
    elif ratios["hindi"] > 0.1:
        return "hi"
    elif ratios["cyrillic"] > 0.1:
        return "ru"
    elif ratios["latin_extended"] > 0.3:
        return "en"  # Default to English for mixed text
    else:
        return "en"  # Default to English


def _select_backend(text: str, backend: Optional[TtsBackend] = None) -> tuple[TtsBackend, str]:
    """
    Select the TTS backend and voice. Piper is the sole implemented engine,
    so every path resolves to Piper; an explicit override is still honored.

    Args:
        text: Input text to narrate.
        backend: Optional explicit backend override (must be Piper).

    Returns:
        Tuple of (backend, voice) to use.
    """
    # Piper is the only implemented backend; honor a Piper override, otherwise
    # fall back to the Piper default voice. Any non-Piper value is ignored.
    if backend is not None and backend != TtsBackend.PIPER:
        logger.warning("narration: only the Piper backend is implemented; ignoring %r", backend)
    return TtsBackend.PIPER, DEFAULT_PIPER_VOICE


def _wav_to_mp3(wav_bytes: bytes) -> bytes:
    """Delegate to the assembly seam owner (kept for direct unit tests)."""
    return assembly.wav_to_mp3(wav_bytes)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def narrate(
    text: str,
    *,
    backend: Optional[TtsBackend] = None,
    voice: Optional[str] = None,
    output_path: Optional[str] = None,
    include_mp3: bool = True,
    speed: float = 1.0,
) -> NarrationResult:
    """
    Synthesize text to audiobook audio (WAV + optional MP3).

    This is the main entry point for audio generation. It automatically
    selects the best backend based on the text's language.

    Args:
        text: The text to synthesize (can be a Journey card, Resume summary,
              or any arbitrary text).
        backend: Optional explicit backend override (TtsBackend.PIPER).
                 If None, narration uses Piper.
        voice: Optional explicit voice override. If None, uses the default
               voice for the selected backend and language.
        output_path: Optional directory path to save audio files. If provided,
                     WAV and MP3 files are written to this directory.
        include_mp3: Whether to generate MP3 in addition to WAV (default True).
        speed: Speech speed multiplier (0.5 to 2.0, default 1.0).

    Returns:
        NarrationResult containing WAV and MP3 bytes, sample rate, and
        the backend/voice actually used.

    Raises:
        ValueError: If text is empty.
        RuntimeError: If TTS synthesis or conversion fails.
    """
    if not text or not text.strip():
        raise ValueError("Text must be non-empty")

    # Select backend and voice
    selected_backend, selected_voice = _select_backend(text, backend)

    # Override voice if explicitly provided
    if voice:
        selected_voice = voice

    audio = assembly.render_segments(
        [(text, selected_voice, speed, selected_backend)],
        include_mp3=include_mp3,
        output_path=output_path,
        basename="narration",
    )

    return NarrationResult(
        wav_bytes=audio.wav_bytes,
        mp3_bytes=audio.mp3_bytes,
        sample_rate=audio.sample_rate,
        backend_used=selected_backend,
        voice_used=selected_voice,
    )


def narrate_journey_card(
    card: dict,
    *,
    include_mp3: bool = True,
    output_path: Optional[str] = None,
) -> NarrationResult:
    """
    Convenience function to narrate a Journey card.

    Args:
        card: Journey card dict with 'title' and 'content' fields.
        include_mp3: Whether to generate MP3 (default True).
        output_path: Optional directory to save audio files.

    Returns:
        NarrationResult with the synthesized audio.
    """
    # Combine title and content for narration
    text = f"{card.get('title', '')}. {card.get('content', '')}"
    return narrate(text, include_mp3=include_mp3, output_path=output_path)


def narrate_resume_summary(
    resume: dict,
    *,
    include_mp3: bool = True,
    output_path: Optional[str] = None,
) -> NarrationResult:
    """
    Convenience function to narrate a Resume's summary section.

    Args:
        resume: Resume dict with 'contact' and 'summary' fields.
        include_mp3: Whether to generate MP3 (default True).
        output_path: Optional directory to save audio files.

    Returns:
        NarrationResult with the synthesized audio.
    """
    name = resume.get("contact", {}).get("name", "Candidate")
    summary = resume.get("summary", "")
    text = f"Resume for {name}. {summary}"
    return narrate(text, include_mp3=include_mp3, output_path=output_path)
