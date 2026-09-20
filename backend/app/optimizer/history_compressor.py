"""
Conversation History Compressor.

Keeps the most recent K turns verbatim and summarizes older turns into a
structured system message using LLM or fact-extraction heuristics.

Falls back to a heuristic summary if the LLM call fails, so the optimizer
pipeline never hard-fails due to a summarization error.
"""

import logging
import re

logger = logging.getLogger(__name__)

RECENT_TURNS_KEPT = 6
_SENTENCE_END = re.compile(r'(?<=[.!?])\s+')

_SUMMARY_SYSTEM_PROMPT = """You are a conversation summarizer for an AI assistant.
Produce a concise structured summary in this exact format (no other text):

USER GOAL: <one sentence stating what the user is trying to accomplish>
KEY FACTS: <comma-separated list of the most important facts or decisions established>
CONSTRAINTS: <comma-separated list of constraints or requirements mentioned, or "none">

Keep the summary under 120 words. Do not invent facts not present in the conversation."""


def _extract_facts(messages: list[dict]) -> list[str]:
    sentences: list[str] = []
    seen: set[str] = set()

    for msg in messages:
        if msg.get("role") != "user":
            continue
        content = msg.get("content", "").strip()
        if not content:
            continue
        for sent in _SENTENCE_END.split(content):
            sent = sent.strip()
            key = sent.lower()
            if len(sent) < 15 or key in seen:
                continue
            seen.add(key)
            sentences.append(sent)

    sentences.sort(key=len, reverse=True)
    return sentences[:10]


def _llm_summarize(turns: list[dict]) -> str:
    """Call the LLM to summarize older conversation turns."""
    from app.services.llm import invoke  # noqa: PLC0415

    convo_text = "\n".join(
        f"{m.get('role', 'user').upper()}: {m.get('content', '')}" for m in turns
    )
    prompt = f"Summarize the following conversation turns:\n\n{convo_text}"
    result = invoke(prompt=prompt, system=_SUMMARY_SYSTEM_PROMPT, max_tokens=200, temperature=0.0)
    return result.text.strip()


def _heuristic_summary(turns: list[dict], num_turns: int) -> str:
    facts = _extract_facts(turns)
    first_user = next((m["content"][:200] for m in turns if m.get("role") == "user"), "")
    summary_parts = [
        f"Original goal: {first_user}",
    ]
    if facts:
        summary_parts.append(f"Key facts: {' | '.join(facts)}")
    return "\n".join(summary_parts)


def compress(conversation: list[dict], question: str) -> list[dict]:
    """
    Return a compressed conversation list.
    """
    if len(conversation) <= RECENT_TURNS_KEPT:
        return conversation

    older = conversation[:-RECENT_TURNS_KEPT]
    recent = conversation[-RECENT_TURNS_KEPT:]

    try:
        summary_text = _llm_summarize(older)
    except Exception as exc:
        logger.debug("[history_compressor] LLM summarization unavailable (%s) — using fact heuristic", exc)
        summary_text = _heuristic_summary(older, len(older))

    summary_message = {
        "role": "system",
        "content": f"[Conversation summary — {len(older)} earlier turns compressed]\n{summary_text}",
    }

    return [summary_message] + recent
