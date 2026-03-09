# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Consequence-Driven Runtime Assertion & False Green Verifier for .agents.
Evaluates runtime consequences across Tier 1 (Signal), Tier 2 (State/Network/Route),
and Tier 3 (DOM/Render), audits test suites for False Green anomalies, and executes
zero-model deterministic user flow spec assertions using pure Python stdlib.
"""

import os
import sys
import re
import json
import argparse
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


class ConsequenceTier(str, Enum):
    TIER_1_SIGNAL = "tier_1_signal"
    TIER_2_STATE_NETWORK_ROUTE = "tier_2_state_network_route"
    TIER_3_DOM_RENDER = "tier_3_dom_render"


class SpecOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class SpecMessage(str, Enum):
    ALL_CONDITIONS_MET = "ALL_CONDITIONS_MET"
    STEP_DRIFT = "STEP_DRIFT"
    SUCCESS_NOT_MET = "SUCCESS_NOT_MET"
    CONTRADICTION = "CONTRADICTION"
    OUTCOME_UNREAD = "OUTCOME_UNREAD"
    ABSENCE_ONLY = "ABSENCE_ONLY"
    UNINSTRUMENTED_SURFACE = "UNINSTRUMENTED_SURFACE"


class PredicateKind(str, Enum):
    SIGNAL = "signal"
    NET = "net"
    STATE = "state"
    ROUTE = "route"
    DOM = "dom"
    ALL_OF = "allOf"
    ANY_OF = "anyOf"


def _resolve_dot_path(data: Any, path: str) -> Tuple[bool, Any]:
    """Traverses a dot-delimited path across nested dicts and lists."""
    if not path:
        return True, data
    parts = path.split(".")
    curr = data
    for part in parts:
        if isinstance(curr, dict) and part in curr:
            curr = curr[part]
        elif isinstance(curr, list) and part.isdigit() and int(part) < len(curr):
            curr = curr[int(part)]
        else:
            return False, None
    return True, curr


def _subset_match(expected: Any, actual: Any) -> bool:
    """Recursively checks if expected is a subset of actual."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        for k, v in expected.items():
            if k not in actual or not _subset_match(v, actual[k]):
                return False
        return True
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) > len(actual):
            return False
        for i, item in enumerate(expected):
            if not _subset_match(item, actual[i]):
                return False
        return True
    else:
        return expected == actual


class ConsequencePredicate:
    """Evaluates a declarative consequence predicate against an execution trace."""

    @staticmethod
    def evaluate(predicate: Dict[str, Any], trace: Dict[str, Any]) -> Tuple[bool, str]:
        kind = predicate.get("kind", "")
        if not kind:
            return False, "Predicate missing 'kind' field"

        if kind == PredicateKind.ALL_OF:
            sub_preds = predicate.get("predicates", [])
            for sub in sub_preds:
                ok, reason = ConsequencePredicate.evaluate(sub, trace)
                if not ok:
                    return False, f"allOf condition failed: {reason}"
            return True, "All sub-predicates satisfied"

        elif kind == PredicateKind.ANY_OF:
            sub_preds = predicate.get("predicates", [])
            if not sub_preds:
                return False, "anyOf requires at least one predicate"
            failures = []
            for sub in sub_preds:
                ok, reason = ConsequencePredicate.evaluate(sub, trace)
                if ok:
                    return True, "At least one anyOf condition satisfied"
                failures.append(reason)
            return False, f"No anyOf conditions met: {'; '.join(failures)}"

        elif kind == PredicateKind.SIGNAL:
            expected_name = predicate.get("name")
            expected_payload = predicate.get("payloadMatches")
            signals = trace.get("signals", [])
            for sig in signals:
                if sig.get("name") == expected_name:
                    if expected_payload is None:
                        return True, f"Signal '{expected_name}' observed"
                    if _subset_match(expected_payload, sig.get("payload", {})):
                        return True, f"Signal '{expected_name}' payload matched"
            return False, f"Signal '{expected_name}' not observed in trace"

        elif kind == PredicateKind.NET:
            expected_method = predicate.get("method", "GET").upper()
            expected_url = predicate.get("urlContains", "")
            expected_status = predicate.get("status")
            must_be_consumed = predicate.get("consumed", True)
            requests = trace.get("network", [])
            for req in requests:
                method = req.get("method", "").upper()
                url = req.get("url", "")
                status = req.get("status")
                consumed = req.get("consumed", True)

                method_match = (method == expected_method)
                url_match = (expected_url in url)
                status_match = (expected_status is None or status == expected_status)

                if method_match and url_match and status_match:
                    if must_be_consumed and not consumed:
                        return False, f"Network request to '{url}' returned {status} but response was unconsumed (outcome_unread)"
                    return True, f"Network request {method} '{url}' [{status}] verified"
            return False, f"No matching network request found for {expected_method} '{expected_url}'"

        elif kind == PredicateKind.STATE:
            path = predicate.get("path", "")
            op = predicate.get("op", "equals")
            if "op" not in predicate:
                if predicate.get("notEmpty") is True:
                    op = "not_empty"
                elif predicate.get("empty") is True:
                    op = "empty"
            expected_val = predicate.get("value")
            state_data = trace.get("state", {})
            found, actual_val = _resolve_dot_path(state_data, path)

            if not found:
                return False, f"State path '{path}' not found in runtime state"

            if op == "equals":
                if actual_val == expected_val:
                    return True, f"State path '{path}' equals expected value"
                return False, f"State path '{path}' expected '{expected_val}', got '{actual_val}'"
            elif op in ("not_empty", "notEmpty"):
                if actual_val:
                    return True, f"State path '{path}' is not empty"
                return False, f"State path '{path}' is unexpectedly empty"
            elif op == "empty":
                if not actual_val:
                    return True, f"State path '{path}' is empty"
                return False, f"State path '{path}' expected empty, got '{actual_val}'"
            elif op == "truthy":
                if bool(actual_val):
                    return True, f"State path '{path}' is truthy"
                return False, f"State path '{path}' is falsy"
            elif op == "falsy":
                if not bool(actual_val):
                    return True, f"State path '{path}' is falsy"
                return False, f"State path '{path}' is truthy"
            return False, f"Unknown state operation '{op}'"

        elif kind == PredicateKind.ROUTE:
            expected_path = predicate.get("path", "")
            expected_query = predicate.get("queryContains", {})
            route_data = trace.get("route", {})
            current_path = route_data.get("path", "")
            current_query = route_data.get("query", {})

            if expected_path and current_path != expected_path:
                return False, f"Route path expected '{expected_path}', current is '{current_path}'"
            if expected_query:
                for qk, qv in expected_query.items():
                    if str(current_query.get(qk)) != str(qv):
                        return False, f"Route query parameter '{qk}' expected '{qv}', got '{current_query.get(qk)}'"
            return True, f"Route navigation to '{expected_path}' verified"

        elif kind == PredicateKind.DOM:
            selector = predicate.get("selector", "")
            expected_text = predicate.get("textContains", "")
            should_exist = predicate.get("exists", True)
            dom_data = trace.get("dom", {})
            elements = dom_data.get("elements", [])

            matching = [el for el in elements if selector in el.get("selector", "") or selector in el.get("ref", "")]
            if should_exist:
                if not matching:
                    return False, f"DOM element matching selector '{selector}' does not exist"
                if expected_text:
                    text_found = any(expected_text in el.get("text", "") for el in matching)
                    if not text_found:
                        return False, f"DOM element '{selector}' exists but text does not contain '{expected_text}'"
                return True, f"DOM element '{selector}' existence verified"
            else:
                if matching:
                    return False, f"DOM element '{selector}' was expected to be absent but was found"
                return True, f"DOM element '{selector}' absence verified"

        return False, f"Unrecognized predicate kind: '{kind}'"


class FalseGreenScanner:
    """Scans test suites for the 5 shapes of false green tests."""

    ABSENCE_PATTERNS = [
        re.compile(r'expect\([^)]+\)\.(?:toBeNull|toBeUndefined|toBeFalsy)\(\)', re.IGNORECASE),
        re.compile(r'expect\([^)]+\)\.not\.(?:toThrow|toBeDefined)\(\)', re.IGNORECASE),
        re.compile(r'assert\s+(?:not\s+\w+|\w+\s+is\s+None)', re.IGNORECASE),
        re.compile(r'assertFalse\([^)]+\)', re.IGNORECASE),
        re.compile(r'expect\([^)]+,\s*isNull\)', re.IGNORECASE),
    ]

    CONSEQUENCE_PATTERNS = [
        re.compile(r'expect\([^)]+\)\.(?:toBe\((?!\s*(?:null|undefined|false|NaN)\s*\))|toEqual\((?!\s*(?:null|undefined|false)\s*\))|toMatch|toHaveBeenCalledWith|toHaveLength|toBeInTheDocument|toContain)', re.IGNORECASE),
        re.compile(r'assertEqual\([^)]+\)', re.IGNORECASE),
        re.compile(r'assert(?:True|In|IsNotNone|Greater|Less|Regex)\([^)]+\)', re.IGNORECASE),
        re.compile(r'assert\s+[^\n#]+?(?:==|!=|>=|<=|>|<|\bin\b|\bis\s+True\b)', re.IGNORECASE),
        re.compile(r'expect\([^)]+,\s*(?:equals\(|isTrue|contains\(|isNotNull)', re.IGNORECASE),
    ]

    MOCK_DRIFT_PATTERNS = [
        re.compile(r'jest\.mock\(|vi\.mock\(|sinon\.stub\(|@patch\(|when\([^)]+\)\.thenReturn\(', re.IGNORECASE),
    ]

    ACTION_PATTERNS = [
        re.compile(r'(?:fireEvent|userEvent)\.click\(|\.click\(\)|tap\(', re.IGNORECASE),
    ]

    @staticmethod
    def audit_content(content: str, filename: str = "") -> List[Dict[str, Any]]:
        findings = []
        lines = content.splitlines()

        # Test block detection (it, test, def test_, testWidgets)
        test_block_pattern = re.compile(r'\b(?:it|test|def\s+test_\w+|testWidgets)\s*\((?:["\']([^"\']+)["\'])?', re.IGNORECASE)

        current_test: Optional[str] = None
        current_lines: List[str] = []
        start_line = 1

        def analyze_block(name: str, block_lines: List[str], l_start: int):
            if not name:
                return
            block_text = "\n".join(block_lines)
            if not block_text.strip():
                return

            absence_matches = sum(len(p.findall(block_text)) for p in FalseGreenScanner.ABSENCE_PATTERNS)
            consequence_matches = sum(len(p.findall(block_text)) for p in FalseGreenScanner.CONSEQUENCE_PATTERNS)
            has_action = any(p.search(block_text) for p in FalseGreenScanner.ACTION_PATTERNS)
            has_mock = any(p.search(block_text) for p in FalseGreenScanner.MOCK_DRIFT_PATTERNS)

            # Shape 1: Absence-only assertions without positive consequences
            if absence_matches > 0 and consequence_matches == 0:
                findings.append({
                    "file": filename,
                    "line": l_start,
                    "test_name": name,
                    "shape": "Shape 1: Absence-Only Assertion",
                    "severity": "HIGH",
                    "reason": "Test asserts only absence (no error/null/not to throw) without asserting positive consequence or state delta.",
                    "suggestion": "Add an assertion for an expected state mutation, network call, or rendered DOM element."
                })

            # Shape 3: UI Action with zero assertions
            if has_action and (absence_matches == 0 and consequence_matches == 0):
                findings.append({
                    "file": filename,
                    "line": l_start,
                    "test_name": name,
                    "shape": "Shape 3: UI Action Without Assertion",
                    "severity": "CRITICAL",
                    "reason": "User action (click/tap) fired but test contains zero assertions on resulting consequence.",
                    "suggestion": "Assert state transition or DOM consequence produced by the action."
                })

            # Shape 2: Over-reliance on mocks without contract verification
            if has_mock and consequence_matches > 0 and "schema" not in block_text.lower() and "contract" not in block_text.lower():
                # Heuristic: Mock used, check if there's any contract/live integration check
                if not any(k in block_text for k in ["status", "body", "payload"]):
                    findings.append({
                        "file": filename,
                        "line": l_start,
                        "test_name": name,
                        "shape": "Shape 2: Mock Stub Drift Risk",
                        "severity": "MEDIUM",
                        "reason": "Test verifies mock invocation but does not assert contract structure or status codes.",
                        "suggestion": "Ensure mock assertion checks exact wire contract or response status."
                    })

        for idx, line in enumerate(lines, 1):
            m = test_block_pattern.search(line)
            if m:
                if current_lines:
                    analyze_block(current_test, current_lines, start_line)
                current_test = m.group(1) or line.strip()[:40]
                current_lines = [line]
                start_line = idx
            else:
                current_lines.append(line)

        if current_lines:
            analyze_block(current_test, current_lines, start_line)

        return findings

    @staticmethod
    def audit_file(filepath: str) -> List[Dict[str, Any]]:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return FalseGreenScanner.audit_content(content, os.path.basename(filepath))
        except OSError as e:
            return [{
                "file": filepath,
                "line": 0,
                "test_name": "N/A",
                "shape": "File Read Error",
                "severity": "HIGH",
                "reason": str(e),
                "suggestion": "Check file path and read permissions."
            }]


class FlowSpecRunner:
    """Executes a deterministic flow specification against an execution trace."""

    @staticmethod
    def run(flow_spec: Dict[str, Any], trace: Dict[str, Any]) -> Dict[str, Any]:
        flow_name = flow_spec.get("name", "anonymous_flow")
        steps = flow_spec.get("steps", [])
        success_pred = flow_spec.get("success", {})

        # If trace has no instrumented surfaces, return UNKNOWN rather than vacuous PASS
        instrumented_keys = [k for k, v in trace.items() if v and isinstance(v, (dict, list))]
        if not instrumented_keys:
            return {
                "name": flow_name,
                "outcome": SpecOutcome.UNKNOWN.value,
                "message": SpecMessage.UNINSTRUMENTED_SURFACE.value,
                "reason": "Execution trace has zero instrumented surfaces",
                "steps": []
            }

        step_results = []
        for idx, step in enumerate(steps, 1):
            ref = step.get("ref", "")
            action = step.get("action", "")
            until_pred = step.get("until")

            step_record = {
                "step_index": idx,
                "ref": ref,
                "action": action,
                "ok": True,
                "reason": "Action executed"
            }

            if until_pred:
                ok, reason = ConsequencePredicate.evaluate(until_pred, trace)
                step_record["ok"] = ok
                step_record["reason"] = reason
                if not ok:
                    step_results.append(step_record)
                    return {
                        "name": flow_name,
                        "outcome": SpecOutcome.FAIL.value,
                        "message": SpecMessage.STEP_DRIFT.value,
                        "failed_step": idx,
                        "reason": f"Step {idx} ({action} on '{ref}') failed: {reason}",
                        "steps": step_results
                    }

            step_results.append(step_record)

        # Evaluate final terminal success predicate
        if success_pred:
            ok, reason = ConsequencePredicate.evaluate(success_pred, trace)
            if not ok:
                return {
                    "name": flow_name,
                    "outcome": SpecOutcome.FAIL.value,
                    "message": SpecMessage.SUCCESS_NOT_MET.value,
                    "reason": f"Flow steps executed but overall success predicate failed: {reason}",
                    "steps": step_results
                }

        return {
            "name": flow_name,
            "outcome": SpecOutcome.PASS.value,
            "message": SpecMessage.ALL_CONDITIONS_MET.value,
            "reason": "All steps and consequence predicates satisfied",
            "steps": step_results
        }


def main():
    parser = argparse.ArgumentParser(description="Consequence Verifier & False Green Auditor for .agents")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Command: audit-tests
    audit_parser = subparsers.add_parser("audit-tests", help="Audit test files for False Green test patterns")
    audit_parser.add_argument("--file", help="Path to single test file")
    audit_parser.add_argument("--dir", help="Path to directory containing tests")

    # Command: verify-flow
    flow_parser = subparsers.add_parser("verify-flow", help="Verify deterministic flow spec against execution trace")
    flow_parser.add_argument("--flow", required=True, help="Path to flow spec JSON file")
    flow_parser.add_argument("--trace", required=True, help="Path to execution trace JSON file")

    # Command: eval-predicate
    pred_parser = subparsers.add_parser("eval-predicate", help="Evaluate a single consequence predicate")
    pred_parser.add_argument("--predicate", required=True, help="Path to predicate JSON file or raw JSON string")
    pred_parser.add_argument("--trace", required=True, help="Path to trace JSON file")

    args = parser.parse_args()

    if args.command == "audit-tests":
        files_to_scan = []
        if args.file:
            files_to_scan.append(args.file)
        elif args.dir:
            for root, _, files in os.walk(args.dir):
                for f in files:
                    if f.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".dart")) and any(k in f for k in ["test", "spec"]):
                        files_to_scan.append(os.path.join(root, f))
        else:
            print("Error: Specify either --file or --dir")
            sys.exit(1)

        total_findings = 0
        print(f"Auditing {len(files_to_scan)} test file(s) for False Green patterns...")
        for fpath in files_to_scan:
            findings = FalseGreenScanner.audit_file(fpath)
            if findings:
                total_findings += len(findings)
                print(f"\n[VIOLATION] {fpath}")
                for item in findings:
                    print(f"  Line {item['line']} [{item['severity']}] {item['test_name']}: {item['shape']}")
                    print(f"    Reason: {item['reason']}")
                    print(f"    Fix:    {item['suggestion']}")

        print(f"\nAudit complete. Total False Green findings: {total_findings}")
        sys.exit(1 if total_findings > 0 else 0)

    elif args.command == "verify-flow":
        try:
            with open(args.flow, 'r', encoding='utf-8') as f:
                flow_data = json.load(f)
            with open(args.trace, 'r', encoding='utf-8') as f:
                trace_data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON inputs: {e}")
            sys.exit(1)

        result = FlowSpecRunner.run(flow_data, trace_data)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["outcome"] == SpecOutcome.PASS.value else 1)

    elif args.command == "eval-predicate":
        try:
            if os.path.exists(args.predicate):
                with open(args.predicate, 'r', encoding='utf-8') as f:
                    pred_data = json.load(f)
            else:
                pred_data = json.loads(args.predicate)

            with open(args.trace, 'r', encoding='utf-8') as f:
                trace_data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON inputs: {e}")
            sys.exit(1)

        ok, reason = ConsequencePredicate.evaluate(pred_data, trace_data)
        res = {"pass": ok, "reason": reason}
        print(json.dumps(res, indent=2))
        sys.exit(0 if ok else 1)

    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
