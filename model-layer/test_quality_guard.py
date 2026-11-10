"""Tests for model_layer.quality_guard (B6: was at 0% coverage)."""

from model_layer.quality_guard import BANNED_GENERIC, TIPS, polish


def test_polish_removes_banned_phrase_and_appends_tip():
    out = polish("We will delve into the topic.", "career")
    assert "delve into" not in out
    # a career tip is appended when not already present
    assert "Tip:" in out
    assert "story, not a grocery list" in out


def test_polish_does_not_double_append_existing_tip():
    original = "Some career advice.\n\nTip: your resume is a story, not a grocery list."
    out = polish(original, "career")
    assert out == original
    assert out.count("Tip:") == 1


def test_polish_default_tip_for_unknown_section():
    out = polish("Plain text.", "no_such_section")
    assert "Tip:" in out
    assert out.startswith("Plain text.")


def test_polish_case_insensitive_ban():
    out = polish("Please UTILIZE the lever.", "language_lab")
    assert "utilize" not in out.lower()
    assert "Tip:" in out


def test_banned_generic_and_tips_contracts_present():
    assert "delve into" in BANNED_GENERIC
    assert "career" in TIPS
    assert "language_lab" in TIPS
