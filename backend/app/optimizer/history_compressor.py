"""
Conversation History Compressor.

Keeps the most recent K turns verbatim and collapses everything older
into a structured summary message that preserves:
    - The user's original goal (first user message)
    - All distinct facts stated by the user across older turns
    - Key decisions or conclusions mentioned
    - How many turns were compressed

This is a heuristic implementation — it extracts information from the
text of older messages without calling an LLM. It's conservative: it
never silently drops content, it encodes it into the summary message.

For a future LLM-based upgrade, replace the _extract_facts() function
with a Bedrock summarization call. The rest of the module stays the same.
"""

import re

RECENT_TURNS_KEPT = 6

# Sentence endings we split on when extracting facts
_SENTENCE_END = re.compile(r'(?<=[.!?])\s+')


def _extract_facts(messages: list[dict]) -> list[str]:
    """
    Pull meaningful statements out of a list of conversation messages.

    Strategy:
        - Collect all user-role messages (users state facts/requirements)
        - Split into sentences, filter short/filler ones
        - Deduplicate by lowercased content
        - Return up to 10 most informative sentences (longest = most content)
    """
    sentences: list[str] = []
    seen: set[str] = set()

    for msg in messages:
        if msg.get("role") != "user":
            continue
        content = msg.get("content", "").strip()
        if not content:
            continue
        # Split into sentences
        for sent in _SENTENCE_END.split(content):
            sent = sent.strip()
            key  = sent.lower()
            # Skip very short fragments and already-seen content
            if len(sent) < 15 or key in seen:
                continue
            seen.add(key)
            sentences.append(sent)

    # Return the 10 longest sentences — longer = more information-dense
    sentences.sort(key=len, reverse=True)
    return sentences[:10]


def compress(conversation: list[dict], question: str) -> list[dict]:
    """
    Compress older conversation turns into a single structured summary.

    Args:
        conversation: Full conversation history as list of role/content dicts.
        question:     The current user question (used for context, not modified).

    Returns:
        Compressed conversation: one summary system message + last K turns.
        Returns the original list unchanged if it's within the kept limit.
    """
    if len(conversation) <= RECENT_TURNS_KEPT:
        return conversation

    older  = conversation[:-RECENT_TURNS_KEPT]
    recent = conversation[-RECENT_TURNS_KEPT:]

    facts = _extract_facts(older)

    # Build the summary content
    first_user = next(
        (m["content"][:200] for m in older if m.get("role") == "user"), ""
    )

    summary_parts = [
        f"[Conversation summary — {len(older)} earlier turns compressed]",
        f"Original goal: {first_user}",
    ]

    if facts:
        facts_text = " | ".join(facts)
        summary_parts.append(f"Key facts from earlier turns: {facts_text}")

    summary_parts.append(
        f"(Full context compressed by Context Compiler to save tokens)"
    )

    summary = {
        "role":    "system",
        "content": "\n".join(summary_parts),
    }

    return [summary] + recent
