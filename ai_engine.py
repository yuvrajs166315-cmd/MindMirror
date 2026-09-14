import json
import re
from mindmirror_runtime import get_runtime

MODEL_NAME = "qwen3.5:2b"
RUNTIME = get_runtime()

REASONING_SCHEMA = {
    "type": "object",
    "properties": {
        "assumption": {"type": "string"},
        "evidence_used": {"type": "string"},
        "potential_weakness": {"type": "string"},
        "reasoning_pattern": {"type": "string"},
        "reality_check": {"type": "string"},
        "next_time_question": {"type": "string"},
    },
    "required": [
        "assumption", "evidence_used", "potential_weakness",
        "reasoning_pattern", "reality_check", "next_time_question"
    ],
}

HISTORY_SCHEMA = {
    "type": "object",
    "properties": {
        "recurring_pattern": {"type": "string"},
        "strongest_assumption": {"type": "string"},
        "evidence_pattern": {"type": "string"},
        "prediction_pattern": {"type": "string"},
        "reality_pattern": {"type": "string"},
        "next_time_question": {"type": "string"},
    },
    "required": [
        "recurring_pattern", "strongest_assumption", "evidence_pattern",
        "prediction_pattern", "reality_pattern", "next_time_question"
    ],
}

ASSUMPTION_LEDGER_SCHEMA = {
    "type": "object",
    "properties": {
        "entries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "decision_number": {"type": "integer"},
                    "assumption": {"type": "string"},
                    "evidence": {"type": "string"},
                    "evidence_type": {"type": "string"},
                    "prediction": {"type": "string"},
                    "actual_outcome": {"type": "string"},
                    "assessment": {"type": "string"},
                    "lesson": {"type": "string"},
                },
                "required": [
                    "decision_number", "assumption", "evidence", "evidence_type",
                    "prediction", "actual_outcome", "assessment", "lesson"
                ],
            },
        }
    },
    "required": ["entries"],
}

FINGERPRINT_SCHEMA = {
    "type": "object",
    "properties": {
        "prediction_bias": {"type": "string"},
        "confidence_pattern": {"type": "string"},
        "evidence_effectiveness": {"type": "string"},
        "recurring_reasoning_pattern": {"type": "string"},
        "reality_lesson": {"type": "string"},
        "practical_adjustment": {"type": "string"},
        "next_decision_question": {"type": "string"},
    },
    "required": [
        "prediction_bias", "confidence_pattern", "evidence_effectiveness",
        "recurring_reasoning_pattern", "reality_lesson",
        "practical_adjustment", "next_decision_question"
    ],
}


def _clean_json_content(content):
    content = (content or "").strip()
    content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\s*```$", "", content).strip()
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1:
        content = content[start:end + 1]
    return content


def _chat_structured(prompt, schema, num_predict=500):
    response = RUNTIME.chat_structured(
        messages=[{"role": "user", "content": prompt}],
        schema=schema,
        temperature=0,
        num_predict=num_predict,
        think=False,
    )
    return json.loads(_clean_json_content(response["content"]))


def analyze_reasoning(decision, reasoning, prediction, actual_outcome, confidence):
    prompt = f"""
You are the reasoning-analysis engine inside MindMirror.

MindMirror helps a person understand the assumptions and reasoning patterns
behind recorded decisions. Do not tell them whether the decision was good or bad.
Do not diagnose them or make psychological claims.

Analyze only this completed decision:

DECISION: {decision}
USER'S REASONING: {reasoning}
ORIGINAL PREDICTION: {prediction}
ACTUAL OUTCOME: {actual_outcome}
CONFIDENCE: {confidence}%

Use only supplied information.
Every factual claim must be traceable to a supplied field.
Do not invent evidence, actions, motives, adjustments, validation steps, or reasoning.
Never claim the user changed, adjusted, validated, tested, researched, or acted on the decision unless that action is explicitly present in the supplied record.
Do not treat the actual outcome as evidence of what the user believed or did before the outcome.
For evidence_used, summarize only evidence explicitly stated in USER'S REASONING. If none is stated, use exactly: "No explicit evidence was recorded."
For reasoning_pattern, describe only reasoning that is visible in USER'S REASONING.
For reality_check, compare ORIGINAL PREDICTION with ACTUAL OUTCOME without inventing a cause.
For next_time_question, ask about a missing piece of evidence or an assumption; do not imply that validation already happened.
Do not diagnose personality or psychology or reveal chain-of-thought.
Return the requested structured fields. Keep answers concise and practical.
"""
    try:
        result = _chat_structured(prompt, REASONING_SCHEMA, 400)
        for field in REASONING_SCHEMA["required"]:
            result.setdefault(field, "Not available.")

        # Deterministic guardrail: evidence must come from the recorded
        # reasoning, never from the topic of the decision.
        reasoning_lower = str(reasoning).lower()
        explicit_evidence_terms = (
            "data", "survey", "research", "feedback", "interview",
            "analytics", "report", "study", "experiment", "test",
            "historical", "past performance", "customer", "users said",
            "market trend", "trend", "competitor", "observed"
        )
        if not any(term in reasoning_lower for term in explicit_evidence_terms):
            result["evidence_used"] = "No explicit evidence was recorded."

        return result
    except Exception as e:
        return {
            "assumption": "AI analysis unavailable.",
            "evidence_used": "AI analysis unavailable.",
            "potential_weakness": "AI analysis unavailable.",
            "reasoning_pattern": "AI analysis unavailable.",
            "reality_check": "AI analysis unavailable.",
            "next_time_question": "Try the analysis again.",
            "error": str(e),
        }


def test_ai_connection():
    try:
        response = RUNTIME.chat_structured(
            messages=[{
                "role": "user",
                "content": (
                    "Return a JSON object with one key called status. "
                    "Set status to exactly: MindMirror AI connected."
                ),
            }],
            schema={
                "type": "object",
                "properties": {"status": {"type": "string"}},
                "required": ["status"],
            },
            temperature=0,
            num_predict=80,
            think=False,
        )
        data = json.loads(_clean_json_content(response["content"]))
        return data.get("status", "MindMirror AI connected.").strip()
    except Exception as e:
        return f"AI connection failed: {e}"


def get_runtime_status():
    """Return the active AI backend/model for the MindMirror UI."""
    status = RUNTIME.health_check()
    status.update({
        "backend": RUNTIME.backend,
        "model": RUNTIME.model,
    })
    return status


def _format_decisions(decisions):
    return "\n\n".join(
        f"""Decision {i}:
Decision: {d[0]}
Reasoning: {d[1]}
Prediction: {d[2]}
Actual outcome: {d[3]}
Confidence: {d[4]}%"""
        for i, d in enumerate(decisions, 1)
    )


def analyze_decision_history(decisions):
    if not decisions:
        return {"error": "No completed decisions available."}

    prompt = f"""
You are MindMirror, a private decision-learning AI.

Study this small personal dataset and identify signals across decisions:
1. recurring reasoning pattern
2. strongest repeated assumption
3. how evidence is used
4. whether predictions tend to be optimistic or conservative
5. what reality repeatedly taught
6. one useful question before a similar future decision

Treat findings as signals, not statistically conclusive facts.
Do not diagnose, make psychological claims, invent information, or reveal chain-of-thought.
Keep every answer concise and practical.

COMPLETED DECISIONS:
{_format_decisions(decisions)}
"""
    try:
        result = _chat_structured(prompt, HISTORY_SCHEMA, 450)
        for field in HISTORY_SCHEMA["required"]:
            result.setdefault(field, "Not available.")
        return result
    except Exception as e:
        return {"error": str(e)}


def analyze_assumption_ledger(decisions):
    if not decisions:
        return {"entries": []}

    prompt = f"""
You are the Assumption Ledger engine inside MindMirror.

For each completed decision, extract ONE important assumption supported by the
user's recorded reasoning. Connect it to the evidence, classify the evidence,
compare prediction with actual outcome, assess the assumption, and state one
practical lesson.

Rules:
- Use only supplied records.
- Do not invent evidence or facts.
- Do not diagnose or make psychological claims.
- Do not reconstruct hidden chain-of-thought.
- Evidence type must be a short category such as Historical experience,
  Personal intuition, Customer feedback, Observed data, Market signal, or Mixed.
- Assessment must start exactly with Held, Partially held, or Did not hold.
- Lesson must be practical and grounded.
- Keep every text field under 25 words.
- Return exactly one entry per supplied decision, in the same order.

COMPLETED DECISIONS:
{_format_decisions(decisions)}
"""
    try:
        result = _chat_structured(prompt, ASSUMPTION_LEDGER_SCHEMA, 800)
        entries = result.get("entries", [])
        if len(entries) != len(decisions):
            raise ValueError(
                f"Expected {len(decisions)} ledger entries, received {len(entries)}."
            )
        for i, entry in enumerate(entries, 1):
            entry["decision_number"] = i
        return {"entries": entries}
    except Exception as e:
        return {"entries": [], "error": str(e)}


def analyze_decision_fingerprint(decisions):
    """
    Build the AI layer of MindMirror's Decision Fingerprint.

    Input rows:
    (decision, reasoning, prediction, actual_outcome, confidence)

    The model receives both qualitative reasoning and numerical outcome signals.
    Findings are framed as patterns in the recorded dataset, not personality claims.
    """
    if not decisions:
        return {"error": "No completed decisions available."}

    prompt = f"""
You are the Decision Fingerprint engine inside MindMirror.

Study the completed decisions below as one small personal dataset.

Identify:
1. prediction bias: whether expectations tend to be optimistic, conservative, or mixed,
   using the supplied prediction-versus-outcome records.
2. confidence pattern: compare confidence with the supplied prediction gaps. Describe a relationship only if the records support it; otherwise say evidence is insufficient.
3. evidence effectiveness: report ONLY evidence explicitly named in the recorded reasoning.
   - If the reasoning does not explicitly name evidence, write: "No explicit evidence was recorded."
   - Do NOT infer customer research, intuition, historical experience, data, trends, market signals, or any other evidence from the decision topic.
   - Do NOT convert an assumption into evidence.
4. recurring reasoning pattern: identify a repeated wording, justification, or reasoning structure that is actually visible across the recorded reasoning.
   - If no repeated structure is clearly visible, say: "No clear repeated reasoning structure is visible."
5. reality lesson: state the clearest repeated expectation-versus-reality lesson supported directly by the supplied predictions and outcomes.
   - Do NOT invent causes for the outcome.
6. practical adjustment: give one concrete decision-process change grounded in the observed pattern.
   - Prefer assumption checks, explicit evidence requirements, ranges, or validation before commitment.
   - Do NOT prescribe a change to confidence unless the supplied records clearly justify it.
7. next decision question: ask one question that tests the key assumption or missing evidence before a similar future decision.

Important:
- Use ONLY the supplied records.
- Every factual claim must be traceable to a supplied field.
- Never invent facts, evidence, motives, actions, or reasoning.
- Never say an action was taken unless it appears in the recorded reasoning.
- Never use an outcome as proof of what the user believed before the decision.
- Separate numerical findings from interpretation.
- Do not diagnose personality or psychology.
- Do not claim statistical certainty from a small dataset.
- Do not reveal chain-of-thought.
- If evidence is insufficient, explicitly say so.
- Keep every answer under 30 words.

COMPLETED DECISIONS:
{_format_decisions(decisions)}
"""
    try:
        result = _chat_structured(prompt, FINGERPRINT_SCHEMA, 650)
        for field in FINGERPRINT_SCHEMA["required"]:
            result.setdefault(field, "Not available.")

        # Guardrail: if none of the supplied reasoning records contains explicit
        # evidence language, do not let the small model invent an evidence type.
        reasoning_text = " ".join(str(d[1]) for d in decisions).strip()
        explicit_evidence_terms = (
            "data", "survey", "research", "feedback", "interview",
            "analytics", "report", "study", "experiment", "test",
            "historical", "past performance", "customer", "users said",
            "market trend", "trend", "competitor", "observed"
        )
        if reasoning_text and not any(
            term in reasoning_text.lower() for term in explicit_evidence_terms
        ):
            result["evidence_effectiveness"] = "No explicit evidence was recorded."

        return result
    except Exception as e:
        return {"error": str(e)}
