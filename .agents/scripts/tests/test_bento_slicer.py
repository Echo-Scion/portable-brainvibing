import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to sys.path
_scripts_dir = Path(__file__).resolve().parents[1]
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from commands.bento_slicer import (
    extract_fenced_code_blocks,
    parse_action_cards,
    read_live_target_window,
    render_active_bento_markdown,
    sync_orion_infrastructure,
)
from utils.packer import _extract_markdown_sections


class BentoTaskSlicerTests(unittest.TestCase):
    def test_bottom_up_sorting(self):
        markdown_plan = """
### Task 1.1: Top edit
- **Target File**: `src/engine.py`
- **Target Span**: Lines 10-20
- **Root Cause**: Early import

```python
import old_mod
```

```python
import new_mod
```

### Task 1.2: Bottom edit
- **Target File**: `src/engine.py`
- **Target Span**: Lines 100-110
- **Root Cause**: Outdated footer

```python
footer = 1
```

```python
footer = 2
```

### Task 1.3: Middle edit
- **Target File**: `src/engine.py`
- **Target Span**: Lines 50-60
- **Root Cause**: Mid loop

```python
loop = 1
```

```python
loop = 2
```

### Task 2.1: Other file
- **Target File**: `src/other.py`
- **Target Span**: Lines 15-25

```python
x = 1
```

```python
x = 2
```
"""
        cards = parse_action_cards(markdown_plan)
        engine_cards = [c for c in cards if c["target_file"] == "src/engine.py"]
        self.assertEqual(len(engine_cards), 3)

        # Bottom-Up Ordering: line 100 (1.2) -> line 50 (1.3) -> line 10 (1.1)
        self.assertEqual(engine_cards[0]["task_id"], "1.2")
        self.assertEqual(engine_cards[0]["start_line"], 100)
        self.assertEqual(engine_cards[1]["task_id"], "1.3")
        self.assertEqual(engine_cards[1]["start_line"], 50)
        self.assertEqual(engine_cards[2]["task_id"], "1.1")
        self.assertEqual(engine_cards[2]["start_line"], 10)

    def test_nested_code_fence_parsing(self):
        # 4-backtick outer block with inner 3-backtick code block
        nested_markdown = """
### Task 2.1: Nested Fences Handling
- **Target File**: `src/generator.py`
- **Target Span**: Lines 25-35

````markdown
```python
def inner_example():
    return True
```
````

````markdown
```python
def inner_replacement():
    return False
```
````
"""
        cards = parse_action_cards(nested_markdown)
        self.assertEqual(len(cards), 1)
        card = cards[0]
        self.assertIn("inner_example", card["search_code"])
        self.assertIn("inner_replacement", card["replacement_code"])

    def test_live_anchor_recalibration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            src_file = temp_path / "service.py"
            src_file.parent.mkdir(parents=True, exist_ok=True)
            src_file.write_text(
                "line1\nline2\nline3\ndef find_me():\n    return 'found'\nline6\nline7\n",
                encoding="utf-8"
            )

            # Planned lines 1-2, but anchor actually exists at lines 4-5
            search_str = "def find_me():\n    return 'found'"
            numbered, raw, actual_start, actual_end = read_live_target_window(
                temp_path,
                "service.py",
                start_line=1,
                end_line=2,
                search_code=search_str,
            )
            self.assertEqual(actual_start, 4)
            self.assertEqual(actual_end, 5)
            self.assertIn("4 | def find_me():", numbered)
            self.assertEqual(raw, search_str)

    def test_render_active_bento_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            src_file = temp_path / "main.py"
            src_file.write_text("x = 1\ny = 2\nz = 3\n", encoding="utf-8")

            task = {
                "task_id": "T-01",
                "title": "Update main",
                "target_file": "main.py",
                "span_text": "Lines 1-2",
                "root_cause": "Deprecated",
                "start_line": 1,
                "end_line": 2,
                "replacement_lang": "python",
                "search_code": "x = 1\ny = 2",
                "replacement_code": "x = 10\ny = 20",
                "verification_cmd": "python --version",
                "status": "OPEN",
            }

            rendered = render_active_bento_markdown(task, 0, 1, temp_path)
            self.assertIn("ACTIVE ORION BENTO TASK (1 of 1)", rendered)
            self.assertIn("x = 10", rendered)
            self.assertIn("python .agents/scripts/orion.py bento next --verify", rendered)

    def test_extract_markdown_sections_code_comments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_doc = Path(temp_dir) / "doc.md"
            markdown_text = """## Section 1: Implementation

Here is a Python code example:

```python
# This is a comment inside code fence
def hello():
    # Another internal comment
    return "world"
```

## Section 2: Verification

Final notes here.
"""
            temp_doc.write_text(markdown_text, encoding="utf-8")

            # Extracting "Section 1" should include the full code block and not prematurely stop on '# comment'
            sec1 = _extract_markdown_sections(str(temp_doc), ["Section 1"])
            self.assertIn("# This is a comment inside code fence", sec1)
            self.assertIn("def hello():", sec1)
            self.assertNotIn("Final notes here", sec1)

            # Extracting "Section 2" should capture Section 2
            sec2 = _extract_markdown_sections(str(temp_doc), ["Section 2"])
            self.assertIn("Final notes here.", sec2)

    def test_phase_boundary_preservation(self):
        markdown = """
## Phase 1: Core Foundation
### Task 1.1: Edit router in Phase 1
- **Target File**: `src/router.py`
- **Target Span**: Lines 10-20
```python
old_p1 = True
```
```python
new_p1 = True
```

### Task 1.2: Edit contracts in Phase 1
- **Target File**: `src/contracts/user.py`
- **Target Span**: Lines 5-15
```python
old_contract = True
```
```python
new_contract = True
```

## Phase 2: Integration & Wiring
### Task 2.1: Edit router again in Phase 2
- **Target File**: `src/router.py`
- **Target Span**: Lines 50-60
```python
old_p2 = True
```
```python
new_p2 = True
```
"""
        cards = parse_action_cards(markdown)
        self.assertEqual(len(cards), 3)

        # Phase 1 tasks MUST appear before Phase 2 tasks!
        self.assertEqual(cards[0]["phase_id"], "1")
        self.assertEqual(cards[1]["phase_id"], "1")
        self.assertEqual(cards[2]["phase_id"], "2")
        self.assertEqual(cards[2]["task_id"], "2.1")
        self.assertEqual(cards[2]["target_file"], "src/router.py")

    def test_topological_blast_radius_ordering(self):
        markdown = """
## Phase 1: Architectural Fixes
### Task 1.1: UI screen modification
- **Target File**: `lib/presentation/home_screen.dart`
- **Target Span**: Lines 20-30
```dart
old_ui();
```
```dart
new_ui();
```

### Task 1.2: Root contract modification
- **Target File**: `lib/contracts/user_model.dart`
- **Target Span**: Lines 10-20
```dart
old_model();
```
```dart
new_model();
```
"""
        cards = parse_action_cards(markdown)
        self.assertEqual(len(cards), 2)
        # Root contract (gravity 1) MUST be placed before UI screen (gravity 7)!
        self.assertEqual(cards[0]["target_file"], "lib/contracts/user_model.dart")
        self.assertEqual(cards[0]["gravity"], 1)
        self.assertEqual(cards[1]["target_file"], "lib/presentation/home_screen.dart")
        self.assertEqual(cards[1]["gravity"], 7)

    def test_disjoint_parallel_tracks_labeling(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file_a = temp_path / "billing" / "tax.py"
            file_b = temp_path / "ui" / "theme.py"
            file_a.parent.mkdir(parents=True, exist_ok=True)
            file_b.parent.mkdir(parents=True, exist_ok=True)
            file_a.write_text("tax_rate = 0.1\n", encoding="utf-8")
            file_b.write_text("primary_color = '#000'\n", encoding="utf-8")

            markdown = """
## Phase 1: Disjoint Modules
### Task 1.1: Tax logic
- **Target File**: `billing/tax.py`
- **Target Span**: Lines 1-5
```python
tax_rate = 0.1
```
```python
tax_rate = 0.15
```

### Task 1.2: Theme colors
- **Target File**: `ui/theme.py`
- **Target Span**: Lines 1-5
```python
primary_color = '#000'
```
```python
primary_color = '#fff'
```
"""
            cards = parse_action_cards(markdown, workspace_root=temp_path)
            self.assertEqual(len(cards), 2)
            self.assertEqual(cards[0]["execution_topology"], "PARALLEL_DISJOINT")
            self.assertEqual(cards[1]["execution_topology"], "PARALLEL_DISJOINT")
            self.assertNotEqual(cards[0]["track_id"], cards[1]["track_id"])
            tracks = {cards[0]["track_id"], cards[1]["track_id"]}
            self.assertEqual(tracks, {"TRACK-A", "TRACK-B"})

    def test_verify_patch_applied_on_disk_rejection(self):
        from commands.bento_slicer import verify_patch_applied_on_disk
        with tempfile.TemporaryDirectory() as td:
            temp_path = Path(td)
            f = temp_path / "sample.py"
            f.write_text("def old_logic():\n    return 42\n", encoding="utf-8")
            task = {
                "target_file": "sample.py",
                "search_code": "def old_logic():\n    return 42",
                "replacement_code": "def new_logic():\n    return 100",
            }
            ok, err = verify_patch_applied_on_disk(task, temp_path)
            self.assertFalse(ok)
            self.assertIn("still contains the exact unpatched SEARCH block", err)

            f.write_text("def new_logic():\n    return 100\n", encoding="utf-8")
            ok, err = verify_patch_applied_on_disk(task, temp_path)
            self.assertTrue(ok)

    def test_align_replacement_indentation(self):
        from commands.bento_slicer import _align_replacement_indentation
        raw_disk = "        def inner_func():\n            return 1"
        md_search = "    def inner_func():\n        return 1"
        md_repl = "    def inner_func():\n        return 999"
        aligned = _align_replacement_indentation(raw_disk, md_search, md_repl)
        expected = "        def inner_func():\n            return 999"
        self.assertEqual(aligned, expected)

    def test_multi_pair_task_splitting(self):
        markdown = """
### Task 1.1: Multi-span update
- **Target File**: `core/algo.py`
- **Target Span**: Lines 10-20 & Lines 50-60
```python
old_part_1 = True
```
```python
new_part_1 = True
```
```python
old_part_2 = False
```
```python
new_part_2 = False
```
"""
        cards = parse_action_cards(markdown)
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["task_id"], "1.1a")
        self.assertEqual(cards[1]["task_id"], "1.1b")
        self.assertEqual(cards[0]["search_code"], "old_part_1 = True")
        self.assertEqual(cards[1]["search_code"], "old_part_2 = False")

    def test_check_finding_coverage(self):
        from commands.bento_slicer import check_finding_coverage
        content = """
## Threat Table
| ID | Description |
| TTP-B01 | Path bug |
| TTP-R01 | Race condition |
| TTP-S01 | Silent bug |
"""
        tasks = [
            {"task_id": "1.1", "title": "Fix path bug", "root_cause": "Addresses TTP-B01", "span_text": ""},
            {"task_id": "1.2", "title": "Fix race", "root_cause": "Addresses TTP-R01", "span_text": ""},
        ]
        orphaned = check_finding_coverage(content, tasks)
        self.assertEqual(orphaned, ["TTP-S01"])


if __name__ == "__main__":
    unittest.main()
