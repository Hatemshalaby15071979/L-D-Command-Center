# model-layer/tts.py
#
# WHAT: Text-to-speech client for the Piper backend — the supported,
#       offline-first TTS engine (CPU-only, ONNX runtime). Backend-agnostic
#       interface: synthesize(text, voice, language) -> audio bytes.
# WHY:  Provide a local, offline-first TTS capability at the model-layer tier
#       (same as LM Studio client), without depending on cloud services.
# BREAKS IF DELETED: Audio generation across export-engine, audio-engine, and
#       language-lab breaks.
#
# Licensing note (as of 2026-08):
#   - Piper (rhasspy/piper): MIT license for software; voice models are
#     individually licensed (many under Creative Commons or permissive
#     distribution). See https://github.com/rhasspy/piper
#   Piper is CPU-only capable (ONNX runtime).

from __future__ import annotations

import io
import wave
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TtsBackend(str, Enum):
    PIPER = "piper"


DEFAULT_BACKEND = TtsBackend.PIPER
DEFAULT_VOICE = "en_US-lessac-medium"  # Piper's default English voice
DEFAULT_LANGUAGE = "en"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TtsConfig:
    """Configuration for TTS synthesis."""
    backend: TtsBackend = DEFAULT_BACKEND
    voice: str = DEFAULT_VOICE
    language: str = DEFAULT_LANGUAGE
    models_dir: Path = Path(__file__).parent.parent / "models" / "tts"
    speed: float = 1.0  # 0.5 = slow, 1.0 = normal, 2.0 = fast


# ---------------------------------------------------------------------------
# Backend implementations
# ---------------------------------------------------------------------------

def _synthesize_piper(
    text: str,
    voice: str,
    language: str,
    models_dir: Path,
    speed: float,
) -> bytes:
    """
    Synthesize audio using the Piper backend (CPU-only, ONNX runtime).

    Piper loads voice models from a local directory. The voice parameter should
    be in the format 'language_COUNTRY-variant' (e.g., 'en_US-lessac-medium').

    Returns: WAV audio bytes (16-bit, 22050 Hz mono by default for most Piper
    voices; exact sample rate depends on the voice model).
    """
    try:
        from piper import PiperVoice, SynthesisConfig
    except ImportError as e:
        raise RuntimeError(
            "piper-tts package not installed. Run: pip install piper-tts"
        ) from e

    # Resolve model file path
    model_path = models_dir / f"{voice}.onnx"
    config_path = models_dir / f"{voice}.onnx.json"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Piper voice model not found: {model_path}\n"
            f"Download voice models from https://huggingface.co/rhasspy/piper-voices"
        )

    # piper-tts >= 1.3: PiperVoice.synthesize_wav writes a complete WAV;
    # length_scale is the inverse of playback speed.
    piper_voice = PiperVoice.load(model_path, config_path)
    syn_config = SynthesisConfig(length_scale=1.0 / max(speed, 0.01))
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        piper_voice.synthesize_wav(text, wav_file, syn_config)
    return wav_buffer.getvalue()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def synthesize(
    text: str,
    voice: Optional[str] = None,
    language: Optional[str] = None,
    backend: Optional[TtsBackend] = None,
    models_dir: Optional[Path] = None,
    speed: float = 1.0,
) -> bytes:
    """
    Synthesize text to audio bytes using the configured TTS backend.

    Args:
        text: The text to synthesize (must be non-empty).
        voice: Voice identifier (e.g., 'en_US-lessac-medium' for Piper).
               Defaults to DEFAULT_VOICE.
        language: Language code (e.g., 'en', 'es'). Used for validation.
        backend: TtsBackend enum value. Defaults to DEFAULT_BACKEND (Piper).
        models_dir: Directory containing voice model files.
        speed: Speech speed multiplier (0.5 to 2.0).

    Returns:
        WAV audio bytes.

    Raises:
        ValueError: If text is empty or voice/language is invalid.
        FileNotFoundError: If the voice model is not found.
        RuntimeError: If the backend is not available.
    """
    if not text or not text.strip():
        raise ValueError("Text must be non-empty")

    # Apply defaults
    voice = voice or DEFAULT_VOICE
    language = language or DEFAULT_LANGUAGE
    backend = backend or DEFAULT_BACKEND
    models_dir = models_dir or TtsConfig().models_dir

    # Dispatch to backend. Piper is the sole implemented engine.
    if backend == TtsBackend.PIPER:
        return _synthesize_piper(text, voice, language, models_dir, speed)
    raise ValueError(f"Unknown TTS backend: {backend}")


def get_available_voices(backend: Optional[TtsBackend] = None, models_dir: Optional[Path] = None) -> list[str]:
    """
    Return a list of available voice identifiers for the given backend.

    Args:
        backend: TtsBackend to query. Defaults to DEFAULT_BACKEND.
        models_dir: Directory containing voice model files.

    Returns:
        List of voice identifiers (strings) that have model files.
    """
    models_dir = models_dir or TtsConfig().models_dir
    backend = backend or DEFAULT_BACKEND

    if not models_dir.exists():
        return []

    if backend == TtsBackend.PIPER:
        # Piper uses .onnx and .onnx.json pairs
        voices = set()
        for model_file in models_dir.glob("*.onnx"):
            voice_name = model_file.stem  # e.g., "en_US-lessac-medium"
            # Verify config file exists
            config_file = model_file.parent / f"{voice_name}.onnx.json"
            if config_file.exists():
                voices.add(voice_name)
        return sorted(voices)

    return []


def generate_audio(
    text: str,
    output_path: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Convenience function: synthesize text to audio and optionally save to file.

    Args:
        text: Text to synthesize.
        output_path: Optional file path to save WAV audio.
        **kwargs: Passed to synthesize() (voice, language, backend, etc.)

    Returns:
        The output file path if output_path is provided, else "memory".
    """
    audio_bytes = synthesize(text, **kwargs)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(audio_bytes)
        return str(out)

    return "memory"
