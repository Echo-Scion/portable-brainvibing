import os
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPTS_ROOT not in sys.path:
    sys.path.insert(0, SCRIPTS_ROOT)

import commands.brain as brain
from commands.brain import OrionCompactor
from core.capabilities import _output_feeds_edits


def _build_log(total: int, error_at: int) -> str:
    lines = [f"step {i}: compiling unit {i}" for i in range(total)]
    lines[error_at] = f"step {error_at}: ERROR cannot resolve symbol FooBar"
    return "\n".join(lines)


class StreamElisionContractTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        patches = [
            mock.patch.object(brain, "ORION_DIR", os.path.join(self._tmp.name, ".orion")),
            mock.patch.object(brain, "WORKSPACE_DIR", self._tmp.name),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_small_output_is_untouched(self):
        text = "ok\nall green"
        self.assertEqual(OrionCompactor.elide_output(text), text)

    def test_diagnostic_line_survives_the_cut_middle(self):
        log = _build_log(3000, 1500)
        out = OrionCompactor.elide_output(log)
        self.assertLess(len(out), len(log))
        self.assertIn("ERROR cannot resolve symbol FooBar", out)
        self.assertIn("step 0: compiling unit 0", out)
        self.assertIn("step 2999: compiling unit 2999", out)
        self.assertIn("elided", out)

    def test_spill_holds_full_text_and_marker_names_it(self):
        log = _build_log(3000, 1500)
        out = OrionCompactor.elide_output(log)
        marker_line = next(line for line in out.splitlines() if "Full output:" in line)
        rel = marker_line.split("Full output: ")[1].split(" ")[0]
        spilled = os.path.join(self._tmp.name, rel)
        with open(spilled, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), log)

    def test_spill_directory_is_bounded(self):
        for i in range(brain.STREAM_SPILL_KEEP + 8):
            OrionCompactor.elide_output(_build_log(2000, 900) + f"\nunique tail {i}")
        spill_dir = os.path.join(self._tmp.name, ".orion", "working", "spill")
        self.assertLessEqual(len(os.listdir(spill_dir)), brain.STREAM_SPILL_KEEP)

    def test_spill_can_be_disabled(self):
        out = OrionCompactor.elide_output(_build_log(3000, 10), spill=False)
        self.assertIn("elided", out)
        self.assertNotIn("Full output:", out)
        self.assertFalse(os.path.exists(os.path.join(self._tmp.name, ".orion")))

    def test_single_giant_line_is_cut_by_characters(self):
        giant = "x" * 50000
        out = OrionCompactor.elide_output(giant)
        self.assertLess(len(out), len(giant))
        self.assertIn("chars from the middle", out)

    def test_run_stream_strips_ansi_and_folds_repeats_before_eliding(self):
        noisy = "\x1b[31mred\x1b[0m\n" + "\n".join(["same"] * 5) + "\nend"
        out = OrionCompactor.run_stream(noisy)
        self.assertNotIn("\x1b", out)
        self.assertIn("[repeated 4x]", out)

    def test_compress_stream_level_reports_stages(self):
        res = OrionCompactor.compress(_build_log(3000, 1500), level="stream")
        self.assertEqual(res["status"], "COMPRESSED")
        self.assertIn("stream_elide", res["stages"])
        self.assertIn("ERROR cannot resolve symbol FooBar", res["output"])

    def test_lite_default_keeps_legacy_cut_and_flag_disables_it(self):
        log = "\n".join(f"line {i}" for i in range(300))
        self.assertIn("omitted by Stream Filter", OrionCompactor.run_lite(log))
        self.assertNotIn("omitted by Stream Filter", OrionCompactor.run_lite(log, elide=False))

    def test_commands_that_feed_edits_are_recognised(self):
        self.assertTrue(_output_feeds_edits(["cat", "a.py"]))
        self.assertTrue(_output_feeds_edits(["Get-Content", "a.py"]))
        self.assertTrue(_output_feeds_edits(["C:/tools/bat.exe", "a.py"]))
        self.assertFalse(_output_feeds_edits(["git", "log"]))
        self.assertFalse(_output_feeds_edits([]))


if __name__ == "__main__":
    unittest.main()
