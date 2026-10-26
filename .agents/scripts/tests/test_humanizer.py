import unittest
import os
import sys

# Add scripts directory to sys.path
SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from commands.compact import HumanizerEngine, SyntaxAnchorGuard, OrionCompactor


class TestHumanizerEngine(unittest.TestCase):
    def test_syntax_anchor_guard_preserves_code_and_paths(self):
        text = "Check `my_fn(x)` in .agents/scripts/orion.py:42 and visit https://example.com. Serves as a gateway."
        guard = SyntaxAnchorGuard()
        locked = guard.lock(text)
        self.assertNotIn("`my_fn(x)`", locked)
        self.assertNotIn(".agents/scripts/orion.py:42", locked)
        self.assertNotIn("https://example.com", locked)

        # Apply deterministic sanitize
        cleaned = HumanizerEngine.sanitize_deterministic(locked)
        restored = guard.unlock(cleaned)

        self.assertIn("`my_fn(x)`", restored)
        self.assertIn(".agents/scripts/orion.py:42", restored)
        self.assertIn("https://example.com", restored)
        self.assertIn("is a gateway", restored)
        self.assertNotIn("serves as a", restored)

    def test_ai_tells_detection(self):
        text = "It is not just a tool, it's a platform. Marking a pivotal moment. Let that sink in."
        guard = SyntaxAnchorGuard()
        locked = guard.lock(text)
        report = HumanizerEngine.audit_text(locked)

        self.assertGreaterEqual(report["total_tells"], 2)
        self.assertGreaterEqual(report["strong_tells"], 1)
        rules_triggered = [f["rule"] for f in report["findings"]]
        self.assertTrue(any("Not-X-but-Y" in r for r in rules_triggered))
        self.assertTrue(any("Overused AI Vocabulary" in r or "Inflated Significance" in r for r in rules_triggered))

    def test_deterministic_sanitization(self):
        text = "Great question! Let's dive in: this could potentially possibly work. Serves as a foundation. Certainly!"
        cleaned = HumanizerEngine.sanitize_deterministic(text)
        self.assertNotIn("Great question!", cleaned)
        self.assertNotIn("Let's dive in", cleaned)
        self.assertNotIn("could potentially possibly", cleaned)
        self.assertIn("could work", cleaned)
        self.assertIn("is a foundation", cleaned)
        self.assertNotIn("Certainly!", cleaned)

    def test_curly_quotes_normalization(self):
        text = '“Smart quotes” and ‘single quotes’'
        cleaned = HumanizerEngine.sanitize_deterministic(text)
        self.assertEqual(cleaned, '"Smart quotes" and \'single quotes\'')


if __name__ == "__main__":
    unittest.main()
