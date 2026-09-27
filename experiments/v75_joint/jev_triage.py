"""Offline replay triage with Jev. Never import this from a Kaggle agent."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-1.13.0"
CASE_FILE = Path(__file__).with_name("jev_case_studies.json")

QUESTIONS = {
    "primary_bottleneck": {
        "type": "choice",
        "instructions": (
            "Given only the replay observations in `state`, which one plausible lost-revenue "
            "mechanism should be investigated first? Select uncertainty if the evidence "
            "cannot distinguish these mechanisms. This is a hypothesis, not a causal finding."
        ),
        "criteria": {
            "cash_runway": "Capital was committed before the existing farm could fund workers, feed and seeds.",
            "worker_service": "Available workers or their travel could not service productive assets on time.",
            "crop_conversion": "A planted crop missed its harvest or sale window despite available demand.",
            "animal_service": "Feed, care, placement or harvest capacity prevented livestock yield.",
            "market_demand": "Saleable inventory existed but a buyer or quote limited accepted sales.",
            "uncertain": "The stated observations do not discriminate among these mechanisms."
        },
    },
    "service_stress": {
        "type": "score",
        "instructions": (
            "How strongly do the observed actions and capacity indicate that time-critical "
            "care, harvest, planting or watering tasks were not completed? Do not calculate from raw numbers."
        ),
        "criteria": [
            "No documented missed or delayed service task.",
            "Some service load is visible, but no missed task is documented.",
            "Several missed or delayed tasks are documented in one short window.",
            "A sustained gap in essential tasks or crop survival is documented."
        ],
    },
    "liquidity_stress": {
        "type": "score",
        "instructions": (
            "How strongly do the supplied observations indicate a short-term cash shortage "
            "that might block already-needed inputs or workers? Treat this as qualitative evidence, "
            "not a calculation of exact affordability."
        ),
        "criteria": [
            "No low-cash period or unmet need is documented.",
            "Cash fell, but the observations do not show an unmet need.",
            "Very low cash coincided with reduced staffing or production work.",
            "Very low cash persisted alongside documented missed sales or essential work."
        ],
    },
}


class JevError(RuntimeError):
    """Safe, deliberately non-diagnostic public error message."""


def load_cases(path: Path = CASE_FILE) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = data.get("cases")
    if data.get("schema_version") != 1 or not isinstance(cases, list):
        raise JevError("Unsupported case-study file")
    if any(not isinstance(c, dict) or not isinstance(c.get("id"), str) or
           not isinstance(c.get("state"), dict) for c in cases):
        raise JevError("Invalid case-study file")
    if len({c["id"] for c in cases}) != len(cases):
        raise JevError("Duplicate case identifiers")
    return cases


def build_request(case: dict) -> dict:
    return {"model": MODEL, "state": case["state"], "questions": QUESTIONS}


def _unit_interval(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1


def _safe_response(raw: object) -> dict:
    if not isinstance(raw, dict) or raw.get("model") != MODEL:
        raise JevError("Unexpected Jev response")
    answers = raw.get("answers")
    if not isinstance(answers, dict):
        raise JevError("Unexpected Jev response")
    selected = {}
    for name, question in QUESTIONS.items():
        answer = answers.get(name)
        if not isinstance(answer, dict) or answer.get("type") != question["type"]:
            raise JevError("Unexpected Jev response")
        confidence = answer.get("confidence")
        if not _unit_interval(confidence):
            raise JevError("Unexpected Jev response")
        probs = answer.get("probabilities")
        if not isinstance(probs, dict) or not all(_unit_interval(v) for v in probs.values()):
            raise JevError("Unexpected Jev response")
        if question["type"] == "choice":
            keys = set(question["criteria"])
            if answer.get("choice") not in keys or set(probs) != keys:
                raise JevError("Unexpected Jev response")
            selected[name] = {"choice": answer["choice"], "confidence": confidence,
                              "probabilities": {key: probs[key] for key in question["criteria"]}}
        else:
            keys = {str(i) for i in range(len(question["criteria"]))}
            score = answer.get("score")
            if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= len(keys) - 1 or set(probs) != keys:
                raise JevError("Unexpected Jev response")
            selected[name] = {"score": score, "confidence": confidence,
                              "probabilities": {key: probs[key] for key in sorted(keys)}}
    usage = raw.get("usage", {})
    if not isinstance(usage, dict):
        raise JevError("Unexpected Jev response")
    safe_usage = {key: usage[key] for key in ("input_tokens", "output_tokens")
                  if type(usage.get(key)) is int and usage[key] >= 0}
    return {"model": MODEL, "answers": selected, "usage": safe_usage}


def call_jev(case: dict) -> dict:
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key or not key.strip():
        raise JevError("TYPESAFE_API_KEY is unavailable in this process")
    body = json.dumps(build_request(case), separators=(",", ":")).encode("utf-8")
    request = Request(API_URL, data=body, method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                return _safe_response(json.load(response))
        except HTTPError as error:
            # Bound retries; neither server bodies nor echoed headers reach output.
            if error.code in (408, 429, 500, 502, 503, 504, 529) and attempt < 2:
                hint = error.headers.get("Retry-After") if error.headers else None
                try:
                    delay = min(4.0, max(0.0, float(hint))) if hint is not None else 0.5 * (2 ** attempt)
                except ValueError:
                    delay = 0.5 * (2 ** attempt)
                time.sleep(delay)
                continue
            raise JevError(f"Jev HTTP status {error.code}") from None
        except (URLError, TimeoutError, OSError, ValueError):
            raise JevError("Jev request or response failed") from None
    raise JevError("Jev request failed")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", dest="selected", help="Case ID; repeat to select several")
    parser.add_argument("--dry-run", action="store_true", help="Print key-free request bodies without calling Jev")
    args = parser.parse_args(argv)
    try:
        cases = load_cases()
        if args.selected:
            selected = set(args.selected)
            if selected - {case["id"] for case in cases}:
                raise JevError("Unknown case identifier")
            cases = [case for case in cases if case["id"] in selected]
        for case in cases:
            output = build_request(case) if args.dry_run else call_jev(case)
            print(json.dumps({"case_id": case["id"], **output}, sort_keys=True))
    except JevError as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
