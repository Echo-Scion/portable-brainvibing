import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from commands.brain import ObsidianVaultExporter


class ObsidianVaultContractTests(unittest.TestCase):
    def test_export_writes_graph_projection_only_to_requested_vault(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "orion.db"
            vault_dir = root / ".orion" / "vault"
            source_note = root / "context" / "03_Tech" / "ARCHITECTURE.md"
            source_note.parent.mkdir(parents=True)
            source_note.write_text("# Authored architecture\n", encoding="utf-8")

            conn = sqlite3.connect(db_path)
            conn.executescript(
                """
                CREATE TABLE nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    name TEXT,
                    source_path TEXT
                );
                CREATE TABLE edges (
                    source_id TEXT,
                    target_id TEXT,
                    relation TEXT,
                    confidence REAL DEFAULT 1.0
                );
                INSERT INTO nodes VALUES ('n1', 'Concept', 'Context Architecture', 'context/03_Tech/ARCHITECTURE.md');
                INSERT INTO nodes VALUES ('n2', 'Concept', 'Brain Graph', '.agents/skills/brain-graph/SKILL.md');
                INSERT INTO edges VALUES ('n1', 'n2', 'REFERENCES', 1.0);
                """
            )
            conn.commit()
            conn.close()

            result = ObsidianVaultExporter(str(db_path)).export_vault(str(vault_dir))

            self.assertEqual(result["status"], "SUCCESS")
            self.assertEqual(result["nodes_exported"], 2)
            self.assertTrue((vault_dir / "index.md").is_file())
            self.assertTrue((vault_dir / "nodes" / "Context_Architecture.md").is_file())
            self.assertEqual(source_note.read_text(encoding="utf-8"), "# Authored architecture\n")
            self.assertFalse((root / "context" / "index.md").exists())


if __name__ == "__main__":
    unittest.main()
