import os
import sys
import unittest
from pathlib import Path

# Add project root and evals to sys.path
root_dir = str(Path(__file__).resolve().parents[3])
evals_dir = str(Path(__file__).resolve().parents[3] / ".agents" / "evals")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if evals_dir not in sys.path:
    sys.path.insert(0, evals_dir)

from consequence_verifier import (
    ConsequencePredicate,
    FalseGreenScanner,
    FlowSpecRunner,
    SpecOutcome,
    SpecMessage,
    PredicateKind,
)


class TestConsequenceVerifier(unittest.TestCase):

    def setUp(self):
        self.sample_trace = {
            "signals": [
                {"name": "cart.item_added", "payload": {"id": "p-101", "qty": 2}},
                {"name": "checkout.initiated", "payload": {"total": 59.99}}
            ],
            "network": [
                {"method": "POST", "url": "/api/v1/cart/items", "status": 200, "consumed": True},
                {"method": "GET", "url": "/api/v1/user/profile", "status": 200, "consumed": False},
                {"method": "POST", "url": "/api/v1/checkout", "status": 201, "consumed": True}
            ],
            "state": {
                "user": {"id": "usr-42", "name": "Antigravity", "authenticated": True},
                "cart": {
                    "items": [{"id": "p-101", "qty": 2}],
                    "total": 59.99,
                    "coupon": None
                }
            },
            "route": {
                "path": "/checkout/confirmation",
                "query": {"orderId": "ord-9988", "step": "done"}
            },
            "dom": {
                "elements": [
                    {"selector": "[data-testid='order-summary']", "ref": "order-summary", "text": "Thank you for your order ord-9988!"},
                    {"selector": "#submit-btn", "ref": "submit-btn", "text": "Pay Now"}
                ]
            }
        }

    def test_signal_predicate_matched(self):
        pred = {"kind": "signal", "name": "cart.item_added", "payloadMatches": {"id": "p-101"}}
        ok, reason = ConsequencePredicate.evaluate(pred, self.sample_trace)
        self.assertTrue(ok)
        self.assertIn("payload matched", reason)

    def test_signal_predicate_unobserved(self):
        pred = {"kind": "signal", "name": "non_existent_signal"}
        ok, reason = ConsequencePredicate.evaluate(pred, self.sample_trace)
        self.assertFalse(ok)
        self.assertIn("not observed", reason)

    def test_network_predicate_success(self):
        pred = {"kind": "net", "method": "POST", "urlContains": "/cart/items", "status": 200}
        ok, reason = ConsequencePredicate.evaluate(pred, self.sample_trace)
        self.assertTrue(ok)
        self.assertIn("verified", reason)

    def test_network_predicate_outcome_unread(self):
        # /api/v1/user/profile was returned 200 but consumed=False
        pred = {"kind": "net", "method": "GET", "urlContains": "/user/profile", "status": 200, "consumed": True}
        ok, reason = ConsequencePredicate.evaluate(pred, self.sample_trace)
        self.assertFalse(ok)
        self.assertIn("outcome_unread", reason)

    def test_state_predicate_nested_and_ops(self):
        pred1 = {"kind": "state", "path": "user.name", "value": "Antigravity", "op": "equals"}
        ok1, _ = ConsequencePredicate.evaluate(pred1, self.sample_trace)
        self.assertTrue(ok1)

        pred2 = {"kind": "state", "path": "cart.items", "op": "not_empty"}
        ok2, _ = ConsequencePredicate.evaluate(pred2, self.sample_trace)
        self.assertTrue(ok2)

        pred3 = {"kind": "state", "path": "cart.coupon", "op": "empty"}
        ok3, _ = ConsequencePredicate.evaluate(pred3, self.sample_trace)
        self.assertTrue(ok3)

    def test_route_predicate(self):
        pred = {"kind": "route", "path": "/checkout/confirmation", "queryContains": {"orderId": "ord-9988"}}
        ok, reason = ConsequencePredicate.evaluate(pred, self.sample_trace)
        self.assertTrue(ok)

        bad_pred = {"kind": "route", "path": "/checkout/confirmation", "queryContains": {"orderId": "wrong-id"}}
        bad_ok, _ = ConsequencePredicate.evaluate(bad_pred, self.sample_trace)
        self.assertFalse(bad_ok)

    def test_dom_predicate_existence_and_absence(self):
        pred_exist = {"kind": "dom", "selector": "[data-testid='order-summary']", "textContains": "ord-9988", "exists": True}
        ok, reason = ConsequencePredicate.evaluate(pred_exist, self.sample_trace)
        self.assertTrue(ok)

        pred_absent = {"kind": "dom", "selector": "#error-banner", "exists": False}
        ok_absent, _ = ConsequencePredicate.evaluate(pred_absent, self.sample_trace)
        self.assertTrue(ok_absent)

    def test_all_of_composition(self):
        pred = {
            "kind": "allOf",
            "predicates": [
                {"kind": "signal", "name": "checkout.initiated"},
                {"kind": "net", "method": "POST", "urlContains": "/checkout", "status": 201},
                {"kind": "dom", "selector": "[data-testid='order-summary']", "textContains": "Thank you"}
            ]
        }
        ok, reason = ConsequencePredicate.evaluate(pred, self.sample_trace)
        self.assertTrue(ok)

    def test_false_green_scanner_shape_1_absence_only(self):
        code = """
        it("should not crash on submit", () => {
            const err = handleSubmission();
            expect(err).toBeNull();
        });
        """
        findings = FalseGreenScanner.audit_content(code, "test_file.ts")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["shape"], "Shape 1: Absence-Only Assertion")

    def test_false_green_scanner_shape_3_action_without_assertion(self):
        code = """
        it("clicks the button", () => {
            userEvent.click(screen.getByRole("button"));
        });
        """
        findings = FalseGreenScanner.audit_content(code, "test_action.ts")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["shape"], "Shape 3: UI Action Without Assertion")

    def test_false_green_scanner_clean_test_no_false_positives(self):
        code = """
        it("updates count on click", () => {
            userEvent.click(screen.getByRole("button"));
            expect(screen.getByText("Count: 1")).toBeInTheDocument();
            expect(counterState.value).toEqual(1);
        });
        """
        findings = FalseGreenScanner.audit_content(code, "clean_test.ts")
        self.assertEqual(len(findings), 0)

    def test_flow_spec_runner_success(self):
        flow_spec = {
            "name": "checkout_flow",
            "steps": [
                {
                    "ref": "#submit-btn",
                    "action": "click",
                    "until": {"kind": "signal", "name": "checkout.initiated"}
                }
            ],
            "success": {
                "kind": "route",
                "path": "/checkout/confirmation"
            }
        }
        result = FlowSpecRunner.run(flow_spec, self.sample_trace)
        self.assertEqual(result["outcome"], SpecOutcome.PASS.value)
        self.assertEqual(result["message"], SpecMessage.ALL_CONDITIONS_MET.value)

    def test_flow_spec_runner_step_drift(self):
        flow_spec = {
            "name": "broken_flow",
            "steps": [
                {
                    "ref": "#ghost-btn",
                    "action": "click",
                    "until": {"kind": "signal", "name": "non_existent"}
                }
            ]
        }
        result = FlowSpecRunner.run(flow_spec, self.sample_trace)
        self.assertEqual(result["outcome"], SpecOutcome.FAIL.value)
        self.assertEqual(result["message"], SpecMessage.STEP_DRIFT.value)


if __name__ == "__main__":
    unittest.main()
