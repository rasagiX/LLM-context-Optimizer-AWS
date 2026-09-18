"""
Prompt Compressor.

Baseline implementation: strips redundant whitespace and filler phrases.
This is intentionally conservative — it must never change meaning.

TODO: proper prompt compression (e.g. LLMLingua-style token pruning or
an LLM rewrite pass) belongs here once the baseline shows this step is
worth the extra latency/cost it would add.
"""

import re

FILLER_PATTERNS = [
    r"\bplease note that\b",
    r"\bit is important to (note|mention) that\b",
    r"\bas (mentioned|stated) (above|earlier|before)\b",
]


def compress(text: str) -> str:
    if not text:
        return text

    compressed = text
    for pattern in FILLER_PATTERNS:
        compressed = re.sub(pattern, "", compressed, flags=re.IGNORECASE)

    # Collapse repeated whitespace/newlines.
    compressed = re.sub(r"[ \t]+", " ", compressed)
    compressed = re.sub(r"\n{3,}", "\n\n", compressed)

    return compressed.strip()
