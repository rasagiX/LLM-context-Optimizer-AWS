"""
Token counting helper.

Uses tiktoken when available for a reasonably accurate estimate; falls
back to a ~4-chars-per-token heuristic otherwise. The tiktoken encoding
is loaded lazily (not at import time) and on first use, since it needs
to download its BPE file the first time and some environments (offline,
restricted egress) can't reach that host — in that case we fall back
silently rather than breaking app startup.
"""

_encoding = None
_tiktoken_unavailable = False


def _get_encoding():
    global _encoding, _tiktoken_unavailable
    if _encoding is not None or _tiktoken_unavailable:
        return _encoding
    try:
        import tiktoken

        _encoding = tiktoken.get_encoding("cl100k_base")
    except Exception:
        _tiktoken_unavailable = True
    return _encoding


def count_tokens(text: str) -> int:
    if not text:
        return 0
    enc = _get_encoding()
    if enc is not None:
        return len(enc.encode(text))
    return max(1, len(text) // 4)


def count_context_tokens(question: str, conversation: list[dict], documents: list[dict], tools: list[dict]) -> int:
    total = count_tokens(question)
    total += sum(count_tokens(m.get("content", "")) for m in conversation)
    total += sum(count_tokens(d.get("content", "")) for d in documents)
    total += sum(count_tokens(f"{t.get('name', '')} {t.get('description', '')}") for t in tools)
    return total
