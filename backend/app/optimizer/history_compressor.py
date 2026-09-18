"""
Conversation History Compressor.

Baseline implementation: keep the most recent K turns verbatim and
collapse everything older into a lightweight structured summary
(user goal, known facts, constraints) as described in the project spec.

TODO: the summary is currently a placeholder heuristic (first user
message = goal, no fact/constraint extraction). Swap in an LLM
summarization call once the baseline pipeline is wired up end to end —
keeping it non-LLM for now avoids extra Bedrock calls while iterating.
"""

RECENT_TURNS_KEPT = 6


def compress(conversation: list[dict], question: str) -> list[dict]:
    if len(conversation) <= RECENT_TURNS_KEPT:
        return conversation

    older = conversation[:-RECENT_TURNS_KEPT]
    recent = conversation[-RECENT_TURNS_KEPT:]

    first_user_msg = next((m["content"] for m in older if m.get("role") == "user"), "")

    summary = {
        "role": "system",
        "content": (
            "Summary of earlier conversation (compressed by Context Compiler): "
            f"user_goal='{first_user_msg[:200]}', "
            f"turns_summarized={len(older)}"
        ),
    }

    return [summary] + recent
