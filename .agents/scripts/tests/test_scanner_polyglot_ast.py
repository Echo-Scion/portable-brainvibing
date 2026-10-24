import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.scanner import _count_effective_delimiters_stateful, _count_effective_braces, skeletonize_code


class PolyglotASTHardeningTests(unittest.TestCase):
    def test_raw_strings_windows_paths_and_escapes(self):
        # Windows raw path with trailing backslash must not escape closing quote
        line1 = 'final path = r"C:\\Windows\\System32\\";'
        nb, np, bc, ms = _count_effective_delimiters_stateful(line1)
        self.assertEqual(nb, 0)
        self.assertEqual(np, 0)
        self.assertIsNone(ms)

        line2 = "final path = r'C:\\Windows\\System32\\';"
        nb, np, bc, ms = _count_effective_delimiters_stateful(line2)
        self.assertEqual(nb, 0)
        self.assertEqual(np, 0)
        self.assertIsNone(ms)

    def test_template_literal_and_nested_strings(self):
        # Nested template literal in JS/TS
        line = "const s = `outer ${ `inner` }`;"
        nb, np, bc, ms = _count_effective_delimiters_stateful(line)
        self.assertEqual(nb, 0)
        self.assertEqual(np, 0)
        self.assertIsNone(ms)

        # Multiline template literal with function closure
        lines = [
            "const t = `hello ${() => {",
            "  return 1;",
            "}}`;"
        ]
        total_nb = 0
        in_bc = False
        in_ms = None
        for l in lines:
            nb, np, in_bc, in_ms = _count_effective_delimiters_stateful(l, in_bc, in_ms)
            total_nb += nb
        self.assertEqual(total_nb, 0)
        self.assertIsNone(in_ms)

    def test_dart_string_interpolations_and_literal_braces(self):
        # Literal braces inside string without $ must not count as code braces
        line_literal = 'final s = "value: { not an interpolation }";'
        self.assertEqual(_count_effective_braces(line_literal), 0)

        # Dart string interpolation
        line_interp = 'final s = "Hello ${user.name}";'
        self.assertEqual(_count_effective_braces(line_interp), 0)

        # Dart string interpolation with nested quotes
        line_nested_quotes = 'final s = "${user.get(\\"name\\")}";'
        self.assertEqual(_count_effective_braces(line_nested_quotes), 0)

    def test_dart_3_switch_expression_skeletonizer(self):
        dart_code = """
class MyWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) => switch (state) {
    StateLoading() => const CircularProgressIndicator(),
    StateSuccess() => const Text('Success'),
    _ => const SizedBox(),
  };
}
""".strip()
        skeleton = skeletonize_code(dart_code, "dart")
        self.assertIn("Widget build(BuildContext context) => switch (state) {", skeleton)
        self.assertIn("[Implementation omitted for audit]", skeleton)
        self.assertNotIn("CircularProgressIndicator", skeleton)

    def test_dart_3_records_and_pattern_assignment(self):
        dart_code = """
class Service {
  (int, String) fetchPair() {
    final a = 1;
    final b = 'two';
    return (a, b);
  }

  void process() {
    final (x, y) = fetchPair();
    print('$x: $y');
  }
}
""".strip()
        skeleton = skeletonize_code(dart_code, "dart")
        self.assertIn("fetchPair()", skeleton)
        self.assertIn("void process()", skeleton)
        self.assertIn("[Implementation omitted for audit]", skeleton)


if __name__ == "__main__":
    unittest.main()
