"""
Conversation History Compressor.

Keeps the most recent K turns verbatim and summarises everything older
into a structured system message using an LLM call.

Falls back to a heuristic summary (first-user-message as goal) if the
LLM call fails, so the optimizer pipeline never hard-fails due to a
summarisation error.
"""

import logging

logger = logging.getLogger(__name__)

RECENT_TURNS_KEPT = 6

_SUMMARY_SYSTEM_PROMPT = """You are a conversation summarizer for an AI assistant.
You will receive a list of conversation turns that are being compressed to save tokens.
Produce a concise structured summary in this exact format (no other text):

USER GOAL: <one sentence stating what the user is trying to accomplish>
KEY FACTS: <comma-separated list of the most important facts or decisions established>
CONSTRAINTS: <comma-separated list of constraints or requirements mentioned, or "none">

Keep the summary under 120 words. Do not invent facts not present in the conversation."""


def _llm_summarize(turns: list[dict]) -> str:
    """Call the LLM to summarise older conversation turns.

    Returns the summary text, or raises on failure (caller handles fallback).
    """
    # Import here to avoid a circular dependency at module load time.
    from app.services.llm import invoke  # noqa: PLC0415

    convo_text = "\n".join(
        f"{m.get('role', 'user').upper()}: {m.get('content', '')}" for m in turns
    )
    prompt = f"Summarize the following conversation turns:\n\n{convo_text}"
    result = invoke(prompt=prompt, system=_SUMMARY_SYSTEM_PROMPT, max_tokens=200, temperature=0.0)
    return result.text.strip()


def _heuristic_summary(turns: list[dict], num_turns: int) -> str:
    """Cheap fallback: use the first user message as the inferred goal."""
    first_user = next((m["content"] for m in turns if m.get("role") == "user"), "")
    return (
        f"Summary of earlier conversation (compressed by Context Compiler): "
        f"user_goal='{first_user[:200]}', turns_summarized={num_turns}"
    )


def compress(conversation: list[dict], question: str) -> list[dict]:
    """
    Return a compressed conversation list.

    If len(conversation) <= RECENT_TURNS_KEPT the list is returned unchanged.
    Otherwise the older turns are replaced with a single system summary message
    produced by the LLM (or a heuristic fallback if the LLM call fails).
    """
    if len(conversation) <= RECENT_TURNS_KEPT:
        return conversation

    older = conversation[:-RECENT_TURNS_KEPT]
    recent = conversation[-RECENT_TURNS_KEPT:]

    try:
        summary_text = _llm_summarize(older)
    except Exception as exc:  # pragma: no cover
        logger.warning("LLM history summarization failed, using heuristic fallback: %s", exc)
        summary_text = _heuristic_summary(older, len(older))

    summary_message = {
        "role": "system",
        "content": f"[Conversation summary — {len(older)} earlier turns compressed]\n{summary_text}",
    }

    return [summary_message] + recent
