# Quality guard + humor/tips layer — non-robotic text, tips in every section
import re

BANNED_GENERIC = ["in conclusion", "it is important to note", "furthermore", "delve into", "leverage", "utilize"]
TIPS = {
    "language_lab": "Tip: listen twice — once for meaning, once for tone.",
    "career": "Tip: your resume is a story, not a grocery list.",
    "playground": "Tip: broken audio is just feedback with a loud voice.",
}

def polish(text: str, section: str = "") -> str:
    # Case-insensitive removal of banned corporate filler. The returned string
    # is the cleaned text, not the original — the prior version computed a
    # cleaned copy in a local and returned the untouched input (filler leaked).
    cleaned = text
    for w in BANNED_GENERIC:
        cleaned = re.sub(re.escape(w), "", cleaned, flags=re.IGNORECASE)
    tip = TIPS.get(section, "Tip: humans make mistakes; that’s the point.")
    # keep original if already human; append tip only if not present
    if tip.split(":")[0] not in cleaned:
        cleaned += f"\n\n{tip}"
    return cleaned
