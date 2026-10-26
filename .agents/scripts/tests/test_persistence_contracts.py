import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import connect_sqlite
from core.paths import get_persistence_db_path
from commands.brain import MultiLayerMemoryManager
from core.orion_graph import OrionGraphStore
from commands.state_machine import StateGraph
from core.db import SovereignTracer


class PersistenceContractTests(unittest.TestCase):
    def test_shared_persistence_path_is_canonical(self):
        with tempfile.TemporaryDirectory() as tmp:
            expected = Path(tmp) / ".orion" / "orion.db"
            self.assertEqual(get_persistence_db_path(tmp), expected)

    def test_runtime_domains_share_one_database_without_losing_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "orion.db")
            tracer = SovereignTracer(db_path)
            state = StateGraph(db_path=db_path)
            memory = MultiLayerMemoryManager(db_path)
            graph = OrionGraphStore(db_path)

            try:
                trace_id = tracer.start_trace("trace-shared")
                tracer.record_span("span-shared", trace_id, None, "test", 1.0, 1.1)
                state._save_checkpoint("thread-shared", 1, "node", {"value": 1})
                memory.set_fact("session", "phase", "4")
                graph.add_entity("phase-4", "milestone", "Shared persistence")

                conn = sqlite3.connect(db_path)
                try:
                    tables = {
                        row[0]
                        for row in conn.execute(
                            "SELECT name FROM sqlite_master WHERE type = 'table'"
                        )
                    }
                finally:
                    conn.close()

                self.assertTrue({"spans", "fsm_checkpoints", "multi_layer_memory", "entities"} <= tables)
                self.assertEqual(state.load_checkpoint("thread-shared"), {"value": 1})
                self.assertEqual(memory.get_facts("session")["phase"], "4")
                self.assertEqual(graph.conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0], 1)
            finally:
                tracer.conn.close()
                state.conn.close()
                memory.close()
                graph.conn.close()

    def test_shared_connection_uses_busy_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "runtime.db"
            conn = connect_sqlite(db_path)
            self.assertEqual(conn.execute("PRAGMA busy_timeout").fetchone()[0], 5000)
            conn.close()

    def test_read_only_concurrent_connections_on_windows(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "concurrency.db"
            writer = connect_sqlite(db_path)
            writer.execute("CREATE TABLE test_data (id INTEGER PRIMARY KEY, value TEXT)")
            writer.execute("INSERT INTO test_data (value) VALUES ('sovereign')")
            writer.commit()

            # Multiple concurrent read-only connections
            ro1 = connect_sqlite(db_path, read_only=True)
            ro2 = connect_sqlite(db_path, read_only=True)

            self.assertEqual(ro1.execute("PRAGMA query_only").fetchone()[0], 1)
            self.assertEqual(ro2.execute("PRAGMA query_only").fetchone()[0], 1)

            val1 = ro1.execute("SELECT value FROM test_data WHERE id = 1").fetchone()[0]
            val2 = ro2.execute("SELECT value FROM test_data WHERE id = 1").fetchone()[0]
            self.assertEqual(val1, "sovereign")
            self.assertEqual(val2, "sovereign")

            with self.assertRaises(sqlite3.OperationalError):
                ro1.execute("INSERT INTO test_data (value) VALUES ('illegal_write')")

            ro1.close()
            ro2.close()
            writer.close()


if __name__ == "__main__":
    unittest.main()
