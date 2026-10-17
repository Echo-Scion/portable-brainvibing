import os
import sys
import re
import json
import argparse
import math
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

scripts_dir = str(Path(__file__).resolve().parents[1] / "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

try:
    from core.db import log_telemetry as _log_telemetry
except ImportError:
    def _log_telemetry(err: Exception, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG"):
            msg = f": {err}" if err else ""
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")

from core.capabilities import get_embedding as _core_get_embedding, resolve_ollama_base_url, probe_capabilities
from core.db import cosine_similarity as _cosine_similarity
from core.security import CanaryDefense


def _get_ollama_embedding(text: str) -> Optional[List[float]]:
    """Fetches text embedding via core.capabilities.get_embedding with Fast-Fail Capability Latch."""
    try:
        if not probe_capabilities().get("ollama", {}).get("available"):
            return None
        host = resolve_ollama_base_url()
        return _core_get_embedding(text, host=host)
    except Exception as _e:
        _log_telemetry(_e, "assertion_engine:get_embedding")
        return None


def _jaccard_similarity(s1: str, s2: str) -> float:
    """Offline heuristic fallback for semantic similarity when Ollama is offline."""
    tokens1 = set(re.findall(r'\b\w+\b', s1.lower()))
    tokens2 = set(re.findall(r'\b\w+\b', s2.lower()))
    if not tokens1 or not tokens2:
        return 1.0 if s1 == s2 else 0.0
    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    return intersection / union if union > 0 else 0.0


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes Wagner-Fischer Levenshtein distance between two strings in O(min(m, n)) space."""
    if s1 == s2:
        return 0
    if not s1:
        return len(s2)
    if not s2:
        return len(s1)

    if len(s1) < len(s2):
        s1, s2 = s2, s1

    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1] * (len(s2) + 1)
        for j, c2 in enumerate(s2):
            cost = 0 if c1 == c2 else 1
            curr[j + 1] = min(
                curr[j] + 1,       # insertion
                prev[j + 1] + 1,   # deletion
                prev[j] + cost     # substitution
            )
        prev = curr
    return prev[len(s2)]


def validate_json_schema_subset(data: Any, schema: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates data against a lightweight JSON-schema subset in pure Python stdlib.
    Supports: type, required, properties, minimum, maximum, items, enum, minItems, maxItems.
    """
    expected_type = schema.get("type")
    if expected_type:
        type_map = {
            "object": dict,
            "array": list,
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "null": type(None)
        }
        target_py_type = type_map.get(expected_type)
        if target_py_type:
            if expected_type == "integer" and (isinstance(data, bool) or not isinstance(data, int)):
                return False, f"Expected integer, got {type(data).__name__}"
            elif expected_type == "number" and (isinstance(data, bool) or not isinstance(data, (int, float))):
                return False, f"Expected number, got {type(data).__name__}"
            elif expected_type != "integer" and expected_type != "number" and not isinstance(data, target_py_type):
                return False, f"Expected type {expected_type}, got {type(data).__name__}"

    if "enum" in schema:
        if data not in schema["enum"]:
            return False, f"Value '{data}' is not in allowed enum {schema['enum']}"

    if "minimum" in schema and isinstance(data, (int, float)) and not isinstance(data, bool):
        if data < schema["minimum"]:
            return False, f"Value {data} is less than minimum {schema['minimum']}"

    if "maximum" in schema and isinstance(data, (int, float)) and not isinstance(data, bool):
        if data > schema["maximum"]:
            return False, f"Value {data} is greater than maximum {schema['maximum']}"

    if isinstance(data, dict):
        required_keys = schema.get("required", [])
        for k in required_keys:
            if k not in data:
                return False, f"Missing required property: '{k}'"

        props = schema.get("properties", {})
        for prop_name, prop_schema in props.items():
            if prop_name in data:
                ok, err = validate_json_schema_subset(data[prop_name], prop_schema)
                if not ok:
                    return False, f"Property '{prop_name}': {err}"

    elif isinstance(data, list):
        if "minItems" in schema and len(data) < schema["minItems"]:
            return False, f"Array length {len(data)} is less than minItems {schema['minItems']}"
        if "maxItems" in schema and len(data) > schema["maxItems"]:
            return False, f"Array length {len(data)} is greater than maxItems {schema['maxItems']}"

        items_schema = schema.get("items")
        if items_schema:
            for idx, item in enumerate(data):
                ok, err = validate_json_schema_subset(item, items_schema)
                if not ok:
                    return False, f"Array index {idx}: {err}"

    return True, ""


class AssertionEvaluator:
    """
    Pure-Python declarative assertion engine.
    Evaluates assertion rules on text and structured LLM outputs.
    """
    @staticmethod
    def evaluate(output: str, assertion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a single assertion against output.
        Supported assertion types:
          - equals, not-equals
          - contains, not-contains, icontains
          - regex, not-regex
          - starts-with, ends-with
          - is-json, contains-json, json-schema
          - similar (cosine threshold)
        """
        a_type = assertion.get("type", "contains").lower()
        target = assertion.get("value")
        threshold = assertion.get("threshold", 0.8)
        negate = assertion.get("negate", False)

        passed = False
        message = ""

        # Normalize not- prefix
        if a_type.startswith("not-"):
            a_type = a_type[4:]
            negate = True

        if a_type == "equals":
            passed = (output.strip() == str(target).strip())
            message = f"Expected equals '{target}'"

        elif a_type == "contains":
            passed = str(target) in output
            message = f"Expected substring '{target}'"

        elif a_type == "icontains":
            passed = str(target).lower() in output.lower()
            message = f"Expected case-insensitive substring '{target}'"

        elif a_type == "starts-with":
            passed = output.strip().startswith(str(target))
            message = f"Expected output to start with '{target}'"

        elif a_type == "ends-with":
            passed = output.strip().endswith(str(target))
            message = f"Expected output to end with '{target}'"

        elif a_type == "regex":
            try:
                matched = bool(re.search(str(target), output))
                passed = matched
                message = f"Expected regex match '{target}'"
            except re.error as e:
                passed = False
                message = f"Invalid regex pattern: {e}"

        elif a_type == "is-json":
            try:
                json.loads(output.strip())
                passed = True
                message = "Output is valid JSON"
            except json.JSONDecodeError as e:
                passed = False
                message = f"Invalid JSON output: {e}"

        elif a_type == "contains-json":
            # Extract first JSON block enclosed in { ... } or [ ... ]
            m = re.search(r'(\{.*?\}|\[.*?\])', output, re.DOTALL)
            if m:
                try:
                    json.loads(m.group(1))
                    passed = True
                    message = "Found valid embedded JSON block"
                except Exception as e:
                    passed = False
                    message = f"Malformed embedded JSON block: {e}"
            else:
                passed = False
                message = "No JSON object/array block detected in output"

        elif a_type == "json-schema":
            try:
                parsed = json.loads(output.strip())
                schema = target if isinstance(target, dict) else json.loads(str(target))
                ok, schema_err = validate_json_schema_subset(parsed, schema)
                passed = ok
                message = "JSON schema valid" if ok else schema_err
            except Exception as e:
                passed = False
                message = f"Schema validation error: {e}"

        elif a_type == "contains-all":
            expected_list = target if isinstance(target, (list, tuple)) else [target]
            missing = [item for item in expected_list if str(item) not in output]
            passed = len(missing) == 0
            message = "All expected substrings found" if passed else f"Missing substrings: {missing}"

        elif a_type == "contains-any":
            expected_list = target if isinstance(target, (list, tuple)) else [target]
            found = [item for item in expected_list if str(item) in output]
            passed = len(found) > 0
            message = f"Found matching substring(s): {found}" if passed else f"None of {expected_list} found in output"

        elif a_type in {"levenshtein", "distance"}:
            dist = levenshtein_distance(output.strip(), str(target).strip())
            thresh = float(threshold) if threshold is not None else 3.0
            if thresh >= 1.0:
                passed = dist <= int(thresh)
                message = f"Levenshtein distance: {dist} (max allowed: {int(thresh)})"
            else:
                max_len = max(len(output.strip()), len(str(target).strip()), 1)
                sim = 1.0 - (dist / max_len)
                passed = sim >= thresh
                message = f"Levenshtein similarity ratio: {sim:.4f} (threshold: {thresh})"

        elif a_type in {"canary", "no-canary-leak"}:
            if target:
                tokens = target if isinstance(target, (list, tuple)) else [str(target)]
                found_canaries = CanaryDefense.detect_leaks(output, tokens)
                if not found_canaries and any(re.findall(t, output) for t in tokens if '(' in t or '[' in t):
                    found_canaries = [t for t in tokens if re.search(t, output)]
            else:
                tokens = re.findall(r'CANARY_[a-f0-9]{16}', output)
                found_canaries = CanaryDefense.detect_leaks(output, tokens)
            passed = (len(found_canaries) == 0)
            message = "Zero canary token leaks detected" if passed else f"Canary leak detected: {found_canaries}"

        elif a_type == "assert-set":
            child_assertions = assertion.get("assertions", [])
            operator = assertion.get("operator", "and").lower()
            results = [AssertionEvaluator.evaluate(output, child) for child in child_assertions]
            if operator == "or":
                passed = any(r["passed"] for r in results)
            else:
                passed = all(r["passed"] for r in results)
            message = f"assert-set ({operator}): {sum(1 for r in results if r['passed'])}/{len(results)} passed"

        elif a_type in {"similar", "similarity"}:
            emb_out = _get_ollama_embedding(output)
            emb_tgt = _get_ollama_embedding(str(target))
            if emb_out and emb_tgt:
                sim = _cosine_similarity(emb_out, emb_tgt)
                passed = sim >= float(threshold)
                message = f"Cosine similarity: {sim:.4f} (threshold: {threshold})"
            else:
                jacc = _jaccard_similarity(output, str(target))
                passed = jacc >= (float(threshold) * 0.7)
                message = f"Offline Jaccard similarity: {jacc:.4f} (degraded fallback)"

        else:
            passed = False
            message = f"Unsupported assertion type: '{a_type}'"



        if negate:
            passed = not passed
            message = f"Negation: {message}"

        return {
            "type": assertion.get("type"),
            "passed": passed,
            "message": message,
            "weight": assertion.get("weight", 1.0)
        }

    @classmethod
    def evaluate_suite(cls, output: str, assertions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluates a batch of assertions and computes pass ratio."""
        results = []
        passed_count = 0
        total_weight = 0.0
        earned_weight = 0.0

        for a in assertions:
            res = cls.evaluate(output, a)
            results.append(res)
            w = res["weight"]
            total_weight += w
            if res["passed"]:
                passed_count += 1
                earned_weight += w

        all_passed = (passed_count == len(assertions))
        score = (earned_weight / total_weight * 100.0) if total_weight > 0 else 100.0

        return {
            "all_passed": all_passed,
            "passed_count": passed_count,
            "total_count": len(assertions),
            "score": round(score, 2),
            "results": results
        }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Declarative Multi-Type Assertion Engine")
    parser.add_argument("--output", help="Raw string output to evaluate")
    parser.add_argument("--file", help="File containing output to evaluate")
    parser.add_argument("--assertions", help="JSON array of assertion objects")
    parser.add_argument("--assertions-file", help="File containing JSON array of assertion objects")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    output_text = args.output
    if not output_text and args.file:
        if os.path.exists(args.file):
            with open(args.file, "r", encoding="utf-8") as f:
                output_text = f.read()

    assertions_list = None
    if args.assertions:
        try:
            assertions_list = json.loads(args.assertions)
        except Exception as e:
            sys.stderr.write(f"Error parsing --assertions JSON: {e}\n")
            sys.exit(1)
    elif args.assertions_file:
        if os.path.exists(args.assertions_file):
            with open(args.assertions_file, "r", encoding="utf-8") as f:
                assertions_list = json.load(f)

    if output_text is None or assertions_list is None:
        # Self-test demonstration mode
        sample_text = '{"status": "success", "count": 42, "items": ["a", "b"]}'
        assertions = [
            {"type": "is-json"},
            {"type": "contains", "value": "success"},
            {"type": "regex", "value": r'"count":\s*\d+'},
            {"type": "json-schema", "value": {
                "type": "object",
                "required": ["status", "count", "items"],
                "properties": {
                    "status": {"type": "string"},
                    "count": {"type": "integer"},
                    "items": {"type": "array"}
                }
            }}
        ]
        report = AssertionEvaluator.evaluate_suite(sample_text, assertions)
        print(f"[EVAL] Assertion Suite Score: {report['score']}% ({report['passed_count']}/{report['total_count']} passed)")
        for r in report["results"]:
            mark = "✓" if r["passed"] else "✗"
            print(f" [{mark}] {r['type']}: {r['message']}")
        sys.exit(0 if report["all_passed"] else 1)

    report = AssertionEvaluator.evaluate_suite(output_text, assertions_list)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"[EVAL] Assertion Suite Score: {report['score']}% ({report['passed_count']}/{report['total_count']} passed)")
        for r in report["results"]:
            mark = "✓" if r["passed"] else "✗"
            print(f" [{mark}] {r['type']}: {r['message']}")
    sys.exit(0 if report["all_passed"] else 1)


# ==============================================================================
# RESPONSE VALIDATOR (Absorbed from response_validator.py)
# ==============================================================================

INDONESIAN_MARKERS = {
    "apa", "atau", "bahwa", "dengan", "dan", "dari", "ini", "karena",
    "kenapa", "untuk", "yang", "sudah", "harus", "tidak", "bukan",
}
REQUIRED_FOOTER_LABELS = ("CHECKPOINT", "EVIDENCE", "NEXT TASK")
LESSWORD_FILLER_PATTERNS = (
    r"\bhere(?:'s| is) what you need to know\b",
    r"\blet(?:'s| us) dive in\b",
    r"\bi(?:'d| would) be happy to help\b",
    r"\bhope this helps\b",
)


@dataclass
class Finding:
    rule: str
    message: str
    severity: str = "error"


def _prose_only(response: str) -> str:
    prose = re.sub(r"```.*?```", " ", response, flags=re.DOTALL)
    prose = re.sub(r"`[^`\n]*`", " ", prose)
    prose = re.sub(r"https?://\S+", " ", prose)
    return prose


def validate_response(
    response: str,
    *,
    require_footer: bool = True,
    strict_lessword: bool = False,
    allow_qa: bool = True,
) -> List[Finding]:
    findings: List[Finding] = []
    prose = _prose_only(response)
    words = set(re.findall(r"\b[a-zA-ZÀ-ÿ]+\b", prose.lower()))

    if re.search(r"[\u0400-\u04ff\u0600-\u06ff\u3040-\u30ff\u3400-\u9fff]", prose):
        findings.append(Finding("english", "Non-Latin script detected in response prose."))
    marker_hits = sorted(words & INDONESIAN_MARKERS)
    if len(marker_hits) >= 2:
        findings.append(
            Finding("english", f"Likely non-English prose markers detected: {', '.join(marker_hits)}.")
        )

    if require_footer:
        is_qa_turn = allow_qa and ("CHECKPOINT" in response and "NEXT TASK" in response and "EVIDENCE" not in response)
        if is_qa_turn:
            pass
        else:
            missing = [label for label in REQUIRED_FOOTER_LABELS if label not in response]
            if missing:
                findings.append(Finding("footer", f"Missing required footer labels: {', '.join(missing)}."))

    if "EVIDENCE" in response and "Exit Code 0" in response:
        failures_log = Path(".orion/working/failures.log")
        if failures_log.exists():
            import time
            try:
                if (time.time() - failures_log.stat().st_mtime) < 60:
                    findings.append(Finding(
                        "evidence",
                        "Response claims 'Exit Code 0' in EVIDENCE, but a command failure was logged within the last 60s in failures.log."
                    ))
            except OSError:
                pass

    if strict_lessword:
        for pattern in LESSWORD_FILLER_PATTERNS:
            if re.search(pattern, prose, re.IGNORECASE):
                findings.append(Finding("lessword", f"Lessword filler detected: {pattern}."))

    return findings


def main_response_validator(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="assertion_engine.py validate-response", description="Validate agent response contract.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--file", type=Path, help="Read response from a UTF-8 file.")
    source.add_argument("--text", help="Validate literal response text.")
    parser.add_argument("--no-footer", action="store_true", help="Skip footer validation.")
    parser.add_argument("--strict-lessword", action="store_true", help="Reject known filler phrases.")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit machine-readable results.")
    args = parser.parse_args(argv if argv is not None else sys.argv[2:])

    if args.file:
        response = args.file.read_text(encoding="utf-8")
    elif args.text is not None:
        response = args.text
    else:
        response = sys.stdin.read()

    findings = validate_response(
        response,
        require_footer=not args.no_footer,
        strict_lessword=args.strict_lessword,
    )
    result = {
        "valid": not findings,
        "finding_count": len(findings),
        "findings": [asdict(finding) for finding in findings],
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=True))
    else:
        print("VALID" if result["valid"] else "INVALID")
        for finding in findings:
            print(f"[{finding.severity.upper()}] {finding.rule}: {finding.message}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("validate-response", "response-validator", "response_validator"):
        sys.exit(main_response_validator(sys.argv[2:]))
    else:
        main()

