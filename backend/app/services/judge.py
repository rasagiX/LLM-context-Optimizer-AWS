"""
Quality Judge.

Scores an answer against a task-specific rubric using the LLM itself
as an evaluator. Kept separate from llm.py so the judging prompt/
parsing logic lives in one place.
"""

import json

from app.schemas.responses import QualityScore
from app.services import llm

JUDGE_SYSTEM_PROMPT = """You are a strict evaluation judge for LLM answers.
You will be given a question, an answer, and a rubric (a list of criteria).
For each rubric item, decide if the answer satisfies it.
Respond ONLY with JSON, no preamble, no markdown fences, in this exact shape:

{
  "score": <float 0-10>,
  "rationale": "<one or two sentence explanation>",
  "rubric_hits": ["<criteria the answer satisfied>"],
  "rubric_misses": ["<criteria the answer failed>"]
}
"""


def evaluate(question: str, answer: str, rubric: list[str]) -> QualityScore:
    rubric_text = "\n".join(f"- {item}" for item in rubric) if rubric else "(no rubric provided)"

    prompt = (
        f"Question:\n{question}\n\n"
        f"Answer to evaluate:\n{answer}\n\n"
        f"Rubric:\n{rubric_text}"
    )

    result = llm.invoke(prompt=prompt, system=JUDGE_SYSTEM_PROMPT, max_tokens=500)

    cleaned = (
        result.text.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )

    try:
        parsed = json.loads(cleaned)
        return QualityScore(
            score=float(parsed.get("score", 0)),
            rationale=parsed.get("rationale"),
            rubric_hits=parsed.get("rubric_hits", []),
            rubric_misses=parsed.get("rubric_misses", []),
        )
    except (json.JSONDecodeError, TypeError, ValueError):
        # Judge failed to return valid JSON — surface a zero score rather
        # than silently fabricating one, and keep the raw text for debugging.
        return QualityScore(
            score=0.0,
            rationale=f"Judge parse failure. Raw output: {cleaned[:300]}",
        )
