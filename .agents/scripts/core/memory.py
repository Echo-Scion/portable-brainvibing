"""Kernel memory primitives for the .agents ecosystem.

Hosts the 3-tier memory stack (Core, Recall, Archival), graph community
clustering, the Obsidian vault exporter and the Second Brain briefing builder.
`commands/brain.py` is the CLI gateway that imports these primitives.
"""

import hashlib
import json
import math
import os
import re
import sqlite3
import struct
import sys
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.orion_graph import OrionGraphStore
from core.paths import get_persistence_db_path
from core.db import build_fts_query_or, atomic_write_text

try:
    from core import connect_sqlite, log_telemetry as _kernel_log_telemetry

    def _log_telemetry(err: Optional[Exception] = None, context: str = "") -> None:
        _kernel_log_telemetry(err, context)
except ImportError:
    def _log_telemetry(err: Optional[Exception] = None, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG"):
            msg = f": {err}" if err else ""
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")

    def connect_sqlite(db_path, wal=True, timeout_sec=5.0):
        conn = sqlite3.connect(db_path, timeout=timeout_sec)
        conn.execute(f"PRAGMA busy_timeout={int(timeout_sec * 1000)};")
        return conn

# Base path anchors (core/ -> scripts/ -> .agents/ -> workspace)
_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(os.path.dirname(_CORE_DIR))
WORKSPACE_DIR = os.path.dirname(_BASE_DIR)
ORION_DIR = os.path.join(WORKSPACE_DIR, '.orion')
DB_PATH = str(get_persistence_db_path(WORKSPACE_DIR))
CORE_MEM_PATH = os.path.join(ORION_DIR, 'working', 'core_memory.json')


def louvain_clustering(
    nodes: List[str],
    edges: List[Tuple[str, str, float]],
    store: Optional[OrionGraphStore] = None
) -> Tuple[Dict[str, int], float]:
    """
    Louvain modularity clustering delegating to canonical OrionGraphStore or in-memory execution.
    Returns (node_to_community_map, modularity_q).
    """
    if not nodes:
        return {}, 0.0

    if store is not None:
        partition = store.compute_louvain_communities()
        cur = store.conn.cursor()
        cur.execute("SELECT modularity_q FROM communities ORDER BY level DESC LIMIT 1")
        row = cur.fetchone()
        q = float(row[0]) if row and row[0] is not None else 0.0
        return partition, round(q, 4)

    node_to_idx = {n: i for i, n in enumerate(nodes)}
    idx_to_node = {i: n for i, n in enumerate(nodes)}
    adj: Dict[int, Dict[int, float]] = {i: defaultdict(float) for i in range(len(nodes))}
    m = 0.0
    for u, v, w in edges:
        if u in node_to_idx and v in node_to_idx:
            iu, iv = node_to_idx[u], node_to_idx[v]
            adj[iu][iv] += float(w)
            adj[iv][iu] += float(w)
            m += float(w)

    if m <= 0.0:
        return {n: 0 for n in nodes}, 0.0

    current_adj = adj
    current_node_count = len(nodes)
    node_community_mapping = {i: i for i in range(len(nodes))}
    best_modularity = 0.0
    level = 0
    max_levels = 15

    while level < max_levels:
        partition, mod_q = OrionGraphStore._louvain_phase_one(current_adj, current_node_count, m)
        node_community_mapping = {i: partition[node_community_mapping[i]] for i in range(len(nodes))}
        unique_communities = sorted(list(set(partition.values())))
        best_modularity = max(best_modularity, mod_q)

        if len(unique_communities) >= current_node_count or len(unique_communities) == 1:
            break

        current_adj, current_node_count = OrionGraphStore._louvain_phase_two(current_adj, partition, unique_communities)
        level += 1

    final_mapping = {idx_to_node[i]: node_community_mapping[i] for i in range(len(nodes))}
    return final_mapping, round(best_modularity, 4)



# === TIME-DECAYED MEMORY RETRIEVAL (Half-Life Access Decay) ===

HALF_LIFE_DAYS = 14.0
LAMBDA_DECAY = math.log(2) / (HALF_LIFE_DAYS * 86400.0)

def calculate_retrieval_score(base_relevance: float, created_timestamp: float) -> float:
    """Computes time-decayed retrieval score S = S_base * e^(-lambda * dt)."""
    age_seconds = max(0.0, time.time() - created_timestamp)
    decay_factor = math.exp(-LAMBDA_DECAY * age_seconds)
    return base_relevance * decay_factor


# === FLOAT32 VECTOR BLOB SERIALIZATION & COSINE SIMILARITY (Tier 2 Archival Memory) ===

from core.db import pack_vector, unpack_vector, cosine_similarity


# === MULTI-LAYER MEMORY & AUDIT LEDGER (Multi-Layer Context Ledger) ===

class MultiLayerMemoryManager:
    """
    Multi-layer long-term memory engine with history audit (Scoped Memory Manager).
    Partitions memory into 'user', 'session', and 'persona' layers.
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._closed = False
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
            self._conn = connect_sqlite(self.db_path)
        else:
            self._conn = sqlite3.connect(":memory:")
        return self._conn

    def _init_db(self) -> None:
        conn = self._get_connection()
        with conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS multi_layer_memory (
                id TEXT PRIMARY KEY,
                layer TEXT CHECK(layer IN ('user', 'session', 'persona')),
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                version INTEGER DEFAULT 1,
                updated_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS memory_mutation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT NOT NULL,
                action TEXT CHECK(action IN ('CREATE', 'UPDATE', 'DELETE', 'RESOLVE_CONFLICT')),
                old_value TEXT,
                new_value TEXT,
                timestamp REAL NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_mem_layer ON multi_layer_memory(layer, key);
            CREATE INDEX IF NOT EXISTS idx_mem_hist ON memory_mutation_history(memory_id);
            """)

    def set_fact(self, layer: str, key: str, value: str, confidence: float = 1.0) -> None:
        mem_id = f"{layer}:{key}"
        now = time.time()
        conn = self._get_connection()
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT value, version FROM multi_layer_memory WHERE id = ?", (mem_id,))
            row = cur.fetchone()
            if row:
                old_val, ver = row[0], row[1]
                cur.execute("""
                UPDATE multi_layer_memory 
                SET value = ?, confidence = ?, version = ?, updated_at = ?
                WHERE id = ?
                """, (value, confidence, ver + 1, now, mem_id))
                cur.execute("""
                INSERT INTO memory_mutation_history (memory_id, action, old_value, new_value, timestamp)
                VALUES (?, 'UPDATE', ?, ?, ?)
                """, (mem_id, old_val, value, now))
            else:
                cur.execute("""
                INSERT INTO multi_layer_memory (id, layer, key, value, confidence, version, updated_at)
                VALUES (?, ?, ?, ?, ?, 1, ?)
                """, (mem_id, layer, key, value, confidence, now))
                cur.execute("""
                INSERT INTO memory_mutation_history (memory_id, action, old_value, new_value, timestamp)
                VALUES (?, 'CREATE', NULL, ?, ?)
                """, (mem_id, value, now))

    def get_facts(self, layer: Optional[str] = None) -> Dict[str, str]:
        conn = self._get_connection()
        cur = conn.cursor()
        if layer:
            cur.execute("SELECT key, value FROM multi_layer_memory WHERE layer = ?", (layer,))
        else:
            cur.execute("SELECT key, value FROM multi_layer_memory")
        facts = {r[0]: r[1] for r in cur.fetchall()}
        return facts

    def get_history(self, memory_id: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        if ":" in memory_id:
            cur.execute("""
            SELECT action, old_value, new_value, timestamp 
            FROM memory_mutation_history 
            WHERE memory_id = ? 
            ORDER BY id ASC
            """, (memory_id,))
        else:
            cur.execute("""
            SELECT action, old_value, new_value, timestamp 
            FROM memory_mutation_history 
            WHERE memory_id = ? OR memory_id LIKE ?
            ORDER BY id ASC
            """, (memory_id, f"%:{memory_id}"))
        rows = [
            {"action": r[0], "old_value": r[1], "new_value": r[2], "timestamp": r[3]}
            for r in cur.fetchall()
        ]
        return rows

    def close(self) -> None:
        if self._closed:
            return
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception as _e:
                _log_telemetry(_e, "MultiLayerMemoryManager:close")
            finally:
                self._conn = None
                self._closed = True



class CoreMemoryManager:

    """
    Virtual Core Memory (VirtualMemoryHierarchy pattern).
    Holds persistent human profile and agent persona invariants in active context.
    """
    def __init__(self, path: str = CORE_MEM_PATH):
        self.path = path
        self.data: Dict[str, str] = {
            "human": "Developer: Staff/Principal level. Standards: Lessword terse, zero-pip, Exit Code 0 with evidence mandate.",
            "persona": "Antigravity Assistant. Protocol: Strict TDD, ast-grep polyglot analysis, self-evolving memory consolidation."
        }
        self.load()

    def load(self) -> Dict[str, str]:
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8', errors='ignore') as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        self.data.update(loaded)
            except Exception as e:
                _log_telemetry(e, 'memory.py:CoreMemoryManager.load')
        return self.data

    def save(self) -> None:
        try:
            from core.db import atomic_write_text
            atomic_write_text(self.path, json.dumps(self.data, indent=2))
        except Exception as e:
            _log_telemetry(e, 'memory.py:CoreMemoryManager.save')

    def get_all(self) -> Dict[str, str]:
        return self.data

    def append(self, section: str, content: str) -> Dict[str, str]:
        section = section.lower()
        if section not in self.data:
            self.data[section] = ""
        existing = self.data[section].strip()
        new_text = content.strip()
        if existing:
            self.data[section] = f"{existing} | {new_text}"
        else:
            self.data[section] = new_text
        self.save()
        return self.data

    def replace(self, section: str, old_text: str, new_text: str) -> bool:
        section = section.lower()
        if section not in self.data or old_text not in self.data[section]:
            return False
        self.data[section] = self.data[section].replace(old_text, new_text).strip()
        self.save()
        return True

    def format_prompt_block(self) -> str:
        """Outputs high-density Core Memory for prompt injection."""
        return (
            f"🧠 [CORE MEMORY (VirtualMemoryHierarchy)]\n"
            f"- Human Profile : {self.data.get('human', '')}\n"
            f"- Persona Invariants: {self.data.get('persona', '')}\n"
        )


class ArchivalMemoryManager:
    """
    Virtual Archival Memory (VirtualMemoryHierarchy + SQLite FTS5 pattern).
    Stores persistent domain knowledge, specifications, and architectural invariants.
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._closed = False
        self._conn: Optional[sqlite3.Connection] = None

    def _get_connection(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
            self._conn = connect_sqlite(self.db_path)
        else:
            self._conn = sqlite3.connect(":memory:")
        return self._conn

    def _init_vectors(self, conn: sqlite3.Connection) -> None:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS archival_vectors (
            id TEXT PRIMARY KEY,
            content TEXT,
            embedding BLOB,
            created_at REAL
        );
        """)

    def insert(self, path: str, content: str, category: str = "archival", pillar: str = "core") -> bool:
        if not os.path.exists(self.db_path) and self.db_path != ":memory:":
            return False
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        try:
            conn = self._get_connection()
            with conn:
                conn.execute(
                    "INSERT OR REPLACE INTO pages (path, sha256, category, pillar, updated, access_count, importance) VALUES (?, ?, ?, ?, datetime('now'), 0, 1.0)",
                    (path, content_hash, category, pillar)
                )
                conn.execute(
                    "INSERT OR REPLACE INTO pages_fts (path, content) VALUES (?, ?)",
                    (path, content)
                )
            return True
        except Exception as e:
            _log_telemetry(e, 'memory.py:ArchivalMemoryManager.insert')
            return False

    def insert_vector(self, item_id: str, content: str, embedding: List[float]) -> bool:
        """Stores float32 embedding vector as SQLite BLOB (Vector BLOB Storage)."""
        try:
            blob = pack_vector(embedding)
            conn = self._get_connection()
            with conn:
                self._init_vectors(conn)
                conn.execute(
                    "INSERT OR REPLACE INTO archival_vectors (id, content, embedding, created_at) VALUES (?, ?, ?, ?)",
                    (item_id, content, blob, time.time())
                )
            return True
        except Exception as e:
            _log_telemetry(e, 'memory.py:ArchivalMemoryManager.insert_vector')
            return False

    def search_vectors(self, query_vec: List[float], top_k: int = 5) -> List[Tuple[str, str, float]]:
        """Performs in-memory cosine similarity search across float32 BLOB vectors."""
        try:
            conn = self._get_connection()
            self._init_vectors(conn)
            cur = conn.cursor()
            cur.execute("SELECT id, content, embedding FROM archival_vectors")
            rows = cur.fetchall()

            scored = []
            for item_id, content, blob in rows:
                if blob:
                    sim = cosine_similarity(blob, query_vec)
                    scored.append((item_id, content, sim))
            scored.sort(key=lambda x: x[2], reverse=True)
            return scored[:top_k]
        except Exception as e:
            _log_telemetry(e, 'memory.py:ArchivalMemoryManager.search_vectors')
            return []

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not os.path.exists(self.db_path) and self.db_path != ":memory:":
            return []
        # Sanitize query for FTS5 using core.db single source of truth
        match_expr = build_fts_query_or(query)
        if not match_expr:
            return []

        results = []
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.path, p.category, p.pillar, p.updated, snippet(pages_fts, 1, '«', '»', '...', 20), rank
                FROM pages_fts
                JOIN pages p ON pages_fts.path = p.path
                WHERE pages_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (match_expr, limit)
            )
            for row in cursor.fetchall():
                results.append({
                    "path": row[0],
                    "category": row[1],
                    "pillar": row[2],
                    "updated": row[3],
                    "snippet": row[4],
                    "rank": row[5]
                })
        except Exception as e:
            _log_telemetry(e, 'memory.py:ArchivalMemoryManager.search')
        return results

    def close(self) -> None:
        if self._closed:
            return
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception as _e:
                _log_telemetry(_e, "ArchivalMemoryManager:close")
            finally:
                self._conn = None
                self._closed = True


class RecallMemoryManager:
    """
    Virtual Recall Memory (VirtualMemoryHierarchy + SQLite Telemetry pattern).
    Tracks historical operational events, exit codes, and recent conversational pulses.
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._closed = False
        self._conn: Optional[sqlite3.Connection] = None

    def _get_connection(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
            self._conn = connect_sqlite(self.db_path)
        else:
            self._conn = sqlite3.connect(":memory:")
        return self._conn

    def _init_turns(self, conn: sqlite3.Connection) -> None:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS recall_turns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            tool_calls TEXT,
            created_at REAL NOT NULL
        );
        """)

    def record_turn(self, role: str, content: str, tool_calls: Optional[str] = None) -> bool:
        """Records conversational interaction turn into rolling recall memory."""
        try:
            conn = self._get_connection()
            with conn:
                self._init_turns(conn)
                conn.execute(
                    "INSERT INTO recall_turns (role, content, tool_calls, created_at) VALUES (?, ?, ?, ?)",
                    (role, content, tool_calls, time.time())
                )
            return True
        except Exception as e:
            _log_telemetry(e, 'memory.py:RecallMemoryManager.record_turn')
            return False

    def get_recent_turns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves recent conversation turns ordered by recency descending."""
        try:
            if not os.path.exists(self.db_path) and self.db_path != ":memory:":
                return []
            conn = self._get_connection()
            self._init_turns(conn)
            cur = conn.cursor()
            cur.execute(
                "SELECT id, role, content, tool_calls, created_at FROM recall_turns ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = [
                {
                    "id": r[0],
                    "role": r[1],
                    "content": r[2],
                    "tool_calls": r[3],
                    "created_at": r[4]
                }
                for r in cur.fetchall()
            ]
            return rows
        except Exception as e:
            _log_telemetry(e, 'memory.py:RecallMemoryManager.get_recent_turns')
            return []

    def record_event(self, event_type: str, exit_code: int = 0, context_load: int = 0) -> bool:
        if not os.path.exists(self.db_path) and self.db_path != ":memory:":
            return False
        try:
            conn = self._get_connection()
            with conn:
                conn.execute(
                    "INSERT INTO telemetry (timestamp, event_type, exit_code, context_load) VALUES (datetime('now'), ?, ?, ?)",
                    (event_type, exit_code, context_load)
                )
            return True
        except Exception as e:
            _log_telemetry(e, 'memory.py:RecallMemoryManager.record_event')
            return False

    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        if not os.path.exists(self.db_path) and self.db_path != ":memory:":
            return []
        results = []
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, timestamp, event_type, exit_code, context_load FROM telemetry ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "event_type": row[2],
                    "exit_code": row[3],
                    "context_load": row[4]
                })
        except Exception as e:
            _log_telemetry(e, 'memory.py:RecallMemoryManager.get_recent')
        return results

    def close(self) -> None:
        if self._closed:
            return
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception as _e:
                _log_telemetry(_e, "RecallMemoryManager:close")
            finally:
                self._conn = None
                self._closed = True



class GraphCommunityClusterer:
    """
    Hierarchical Community Clustering (DualLevelGraphRAG Louvain pattern).
    Discovers topological semantic communities from Orion SQLite knowledge graph.
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def detect_communities(self, max_communities: int = 10) -> List[Dict[str, Any]]:
        if not os.path.exists(self.db_path):
            return []
        try:
            with OrionGraphStore(self.db_path) as store:
                store.sync_from_legacy_tables()
                cur = store.conn.cursor()
                cur.execute("SELECT COUNT(*) FROM communities")
                if cur.fetchone()[0] == 0:
                    store.compute_louvain_communities()

                cur.execute("""
                    SELECT c.id, c.cluster_id, c.dominant_type, c.size, c.summary, c.modularity_q,
                           GROUP_CONCAT(cm.entity_name, ',') as members
                    FROM communities c
                    LEFT JOIN community_members cm ON c.id = cm.community_id
                    WHERE c.level = (SELECT COALESCE(MAX(level), 0) FROM communities)
                    GROUP BY c.id
                    ORDER BY c.size DESC
                    LIMIT ?
                """, (max_communities,))

                rows = cur.fetchall()
                communities = []
                for idx, r in enumerate(rows, 1):
                    raw_members = [m.strip() for m in (r["members"] or "").split(",") if m.strip()]
                    communities.append({
                        "community_id": idx,
                        "size": int(r["size"] or len(raw_members)),
                        "dominant_type": r["dominant_type"] or "entity",
                        "top_entities": raw_members[:8],
                        "modularity_q": round(float(r["modularity_q"] or 0.0), 4),
                        "summary": r["summary"] or f"Cluster of {r['size']} {r['dominant_type']} nodes"
                    })
                return communities
        except Exception as e:
            _log_telemetry(e, 'memory.py:GraphCommunityClusterer.detect_communities')
            return []


def _safe_stem(name: str, limit: int = 150) -> str:
    """Sanitize node or community label for safe on-disk filename and wikilink."""
    s = re.sub(r'[<>:"/\\|?*#%\x00-\x1f\x7f]', '_', name)
    s = s.replace(' ', '_').strip('. ')
    return s[:limit] if s else 'unnamed'


class ObsidianVaultExporter:
    """
    Exports Orion SQLite Knowledge Graph to an interactive Obsidian Vault.
    Emits linked Markdown notes with [[wikilinks]], community overviews, and tags.
    Pure Python standard library implementation.
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def export_vault(self, output_dir: Optional[str] = None) -> Dict[str, Any]:
        if output_dir is None:
            output_dir = os.path.join(ORION_DIR, "export", "vault")
        out = os.path.abspath(output_dir)
        nodes_dir = os.path.join(out, "nodes")
        comms_dir = os.path.join(out, "communities")
        os.makedirs(nodes_dir, exist_ok=True)
        os.makedirs(comms_dir, exist_ok=True)

        if not os.path.exists(self.db_path):
            return {"status": "ERROR", "message": "orion.db not found"}

        store = None
        try:
            store = OrionGraphStore(self.db_path)
            store.sync_from_legacy_tables()
            store.compute_louvain_communities()
            cur = store.conn.cursor()
            cur.execute("SELECT COALESCE(MAX(modularity_q), 0.0) FROM communities")
            modularity_q = round(float(cur.fetchone()[0] or 0.0), 4)

            # Primary: Read from entities
            cur.execute("SELECT id, type, name, source_path FROM entities")
            nodes = {str(r["name"]): {"type": r["type"] or "entity", "name": r["name"], "source": r["source_path"] or ""} for r in cur.fetchall()}

            if not nodes:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'")
                if cur.fetchone():
                    cur.execute("SELECT id, type, name, source_path FROM nodes")
                    nodes = {str(r[0]): {"type": r[1] or "entity", "name": r[2] or r[0], "source": r[3] or ""} for r in cur.fetchall()}

            # Primary: Read from relations
            cur.execute("SELECT subject_id, object_id, predicate, weight FROM relations")
            edges = [(str(r["subject_id"]), str(r["object_id"]), r["predicate"], float(r["weight"] or 1.0)) for r in cur.fetchall()]

            if not edges:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='edges'")
                if cur.fetchone():
                    cur.execute("SELECT source_id, target_id, relation, confidence FROM edges")
                    edges = [(str(r[0]), str(r[1]), r[2], float(r[3] or 1.0)) for r in cur.fetchall()]

            # Read directly from communities and community_members tables
            cur.execute("""
                SELECT c.id, c.cluster_id, c.dominant_type, c.size, c.summary, c.modularity_q,
                       GROUP_CONCAT(cm.entity_name, ',') as members
                FROM communities c
                LEFT JOIN community_members cm ON c.id = cm.community_id
                WHERE c.level = (SELECT COALESCE(MAX(level), 0) FROM communities)
                GROUP BY c.id
                ORDER BY c.size DESC
                LIMIT 25
            """)
            communities = []
            node_to_comm: Dict[str, int] = {}
            for idx, r in enumerate(cur.fetchall(), 1):
                raw_members = [m.strip() for m in (r["members"] or "").split(",") if m.strip()]
                communities.append({
                    "community_id": idx,
                    "size": int(r["size"] or len(raw_members)),
                    "dominant_type": r["dominant_type"] or "entity",
                    "top_entities": raw_members[:8],
                    "modularity_q": modularity_q,
                    "summary": r["summary"] or f"Cluster of {r['size']} {r['dominant_type']} nodes"
                })
                for entity_name in raw_members:
                    node_to_comm[entity_name] = idx

            store.close()
            store = None
        except Exception as e:
            if store is not None:
                store.close()
            _log_telemetry(e, 'memory.py:export_vault:db')
            return {"status": "ERROR", "message": str(e)}

        # Build adjacency for bidirectional wikilinks
        out_edges: Dict[str, List[Tuple[str, str]]] = {n: [] for n in nodes}
        in_edges: Dict[str, List[Tuple[str, str]]] = {n: [] for n in nodes}
        for s, t, rel, conf in edges:
            if s in nodes and t in nodes:
                out_edges[s].append((t, rel))
                in_edges[t].append((s, rel))

        written_files = []
        stem_map = {nid: _safe_stem(nodes[nid]["name"]) for nid in nodes}

        # 1. Write individual node notes
        for nid, data in nodes.items():
            stem = stem_map[nid]
            filepath = os.path.join(nodes_dir, f"{stem}.md")
            comm_id = node_to_comm.get(data["name"], "none")

            md_lines = [
                "---",
                f"id: \"{nid}\"",
                f"name: \"{data['name']}\"",
                f"type: \"{data['type']}\"",
                f"community: {comm_id}",
                f"source: \"{data['source']}\"",
                "tags:",
                "  - orion/graph",
                f"  - type/{data['type'].lower()}",
                "---",
                "",
                f"# {data['name']}",
                "",
                f"> Node Type: `{data['type']}` | Source: `{data['source'] or 'knowledge-base'}`",
                "",
            ]

            if out_edges[nid]:
                md_lines.append("## Outbound References")
                for tgt, rel in out_edges[nid][:20]:
                    tgt_stem = stem_map.get(tgt, _safe_stem(tgt))
                    tgt_name = nodes[tgt]["name"] if tgt in nodes else tgt
                    md_lines.append(f"- **{rel}** ➔ [[{tgt_stem}|{tgt_name}]]")
                md_lines.append("")

            if in_edges[nid]:
                md_lines.append("## Inbound References")
                for src, rel in in_edges[nid][:20]:
                    src_stem = stem_map.get(src, _safe_stem(src))
                    src_name = nodes[src]["name"] if src in nodes else src
                    md_lines.append(f"- **{rel}** ⬅ [[{src_stem}|{src_name}]]")
                md_lines.append("")

            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("\n".join(md_lines))
                written_files.append(filepath)
            except Exception as e:
                _log_telemetry(e, 'memory.py:write_node_note')

        # 2. Write Community Overviews
        for comm in communities:
            comm_stem = f"_COMMUNITY_{comm['community_id']:02d}_{_safe_stem(comm['dominant_type'])}"
            comm_file = os.path.join(comms_dir, f"{comm_stem}.md")
            comm_lines = [
                "---",
                f"community_id: {comm['community_id']}",
                f"dominant_type: \"{comm['dominant_type']}\"",
                f"member_count: {comm['size']}",
                "tags:",
                "  - orion/community",
                "---",
                "",
                f"# Community #{comm['community_id']:02d}: {comm['dominant_type'].capitalize()}",
                "",
                f"**Summary**: {comm['summary']}",
                f"**Total Members**: {comm['size']}",
                "",
                "## Top Entities",
            ]
            for ent in comm["top_entities"]:
                ent_stem = _safe_stem(ent)
                comm_lines.append(f"- [[{ent_stem}|{ent}]]")
            comm_lines.append("")

            try:
                with open(comm_file, 'w', encoding='utf-8') as f:
                    f.write("\n".join(comm_lines))
                written_files.append(comm_file)
            except Exception as e:
                _log_telemetry(e, 'memory.py:write_comm_note')

        # 3. Write Index Note
        index_path = os.path.join(out, "index.md")
        index_lines = [
            "# 🌌 Orion Knowledge Graph Vault",
            "",
            "Welcome to your interactive Orion Second Brain. Open this directory as an Obsidian Vault to explore the graph view.",
            "",
            "## Subsystem Communities",
        ]
        for comm in communities:
            comm_stem = f"_COMMUNITY_{comm['community_id']:02d}_{_safe_stem(comm['dominant_type'])}"
            index_lines.append(f"- [[{comm_stem}|Community #{comm['community_id']:02d} ({comm['dominant_type']})]] — {comm['summary']}")
        index_lines.append("")

        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(index_lines))
            written_files.append(index_path)
        except Exception as e:
            _log_telemetry(e, 'memory.py:write_index_note')

        # 3b. Write ORION GRAPH_REPORT.md (God Nodes, Communities & Provenance Summary)
        report_path = os.path.join(out, "GRAPH_REPORT.md")
        degree_rank = sorted(
            nodes.keys(),
            key=lambda k: len(out_edges.get(k, [])) + len(in_edges.get(k, [])),
            reverse=True
        )[:10]
        report_lines = [
            "# 📊 ORION KNOWLEDGE GRAPH REPORT",
            "",
            f"- **Total Entities**: {len(nodes)}",
            f"- **Total Relations**: {len(edges)}",
            f"- **Louvain Communities**: {len(communities)}",
            "",
            "## 🏛️ Top God Nodes (Highest Degree Centrality)",
        ]
        for idx, gn in enumerate(degree_rank, 1):
            deg = len(out_edges.get(gn, [])) + len(in_edges.get(gn, []))
            gn_stem = stem_map.get(gn, _safe_stem(gn))
            report_lines.append(f"{idx}. [[{gn_stem}|{nodes[gn]['name']}]] (`{nodes[gn]['type']}`) — **{deg} connections**")
        report_lines.extend(["", "## 🌌 Subsystem Communities"])
        for comm in communities[:10]:
            comm_stem = f"_COMMUNITY_{comm['community_id']:02d}_{_safe_stem(comm['dominant_type'])}"
            report_lines.append(f"- [[{comm_stem}|Community #{comm['community_id']:02d}]] ({comm['size']} members): {comm['summary']}")
        try:
            with open(report_path, 'w', encoding='utf-8') as rf:
                rf.write("\n".join(report_lines) + "\n")
            written_files.append(report_path)
        except Exception as e:
            _log_telemetry(e, 'memory.py:write_graph_report')

        # 4. Manifest
        manifest_path = os.path.join(out, ".vault_manifest.json")
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump({"vault": out, "total_files": len(written_files), "generated_at": datetime.now().isoformat()}, f, indent=2)
        except Exception as e:
            _log_telemetry(e, 'memory.py:write_manifest')

        return {
            "status": "SUCCESS",
            "vault_dir": out,
            "nodes_exported": len(nodes),
            "communities_exported": len(communities),
            "total_notes": len(written_files)
        }


class SecondBrainManager:
    """
    4-Note Second Brain Protocol (Obsidian / Claude Code / Antigravity pattern).
    Maintains compact, high-density briefing notes that eliminate cold-start exploration.
    """
    def __init__(self, brain_dir: Optional[str] = None, db_path: str = DB_PATH):
        if brain_dir is None:
            brain_dir = os.path.join(ORION_DIR, "working", "brain")
        self.brain_dir = os.path.abspath(brain_dir)
        self.db_path = db_path
        os.makedirs(self.brain_dir, exist_ok=True)

    def build_second_brain(self) -> Dict[str, str]:
        # 1. 00-Overview.md
        overview_path = os.path.join(self.brain_dir, "00-Overview.md")
        overview_content = (
            "# 00 Overview — System Architecture & Mission\n\n"
            "> **Token-Lean Briefing**: Read this before exploring the codebase.\n\n"
            "## Purpose & Mission\n"
            "- **Ecosystem**: .agents (_foundation) — Autonomous Multi-Agent Habitat & Developer SDK.\n"
            "- **Core Guardrails**: Evidence Mandate (Exit Code 0), Zero-Pip Native Python, ast-grep polyglot AST.\n"
            "- **Tier Model**: Cascade to Lowest Viable Tier (PREMIUM > STANDARD > BUDGET > TIER-0 HARNESS).\n\n"
            "## Core Invariants\n"
            "- All memory operations persist to `.orion/`.\n"
            "- Source files use relative paths or `[[wikilinks]]`.\n"
            "- Mechanical verification required before declaring success.\n"
        )
        with open(overview_path, 'w', encoding='utf-8') as f:
            f.write(overview_content)

        # 2. 01-Map.md (God Nodes via PageRank)
        god_nodes = self._compute_god_nodes()
        map_path = os.path.join(self.brain_dir, "01-Map.md")
        map_lines = [
            "# 01 Map — The God Nodes (Central Architecture Hubs)\n\n"
            "> Ranked by PageRank centrality topology. Top files through which dependencies flow.\n\n"
        ]
        for idx, (path, score, role) in enumerate(god_nodes, 1):
            map_lines.append(f"[{idx:02d}] `{path}` (Centrality: {score:.4f})\n     Role: {role}\n")
        with open(map_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(map_lines))

        # 3. 02-Decisions.md (ADRs)
        decisions_path = os.path.join(self.brain_dir, "02-Decisions.md")
        decisions_content = (
            "# 02 Decisions — Architectural Decision Records (ADRs)\n\n"
            "> Check this before suggesting changes to how existing subsystems work.\n\n"
            "## ADR-001: Zero-Pip Native Python Stdlib\n"
            "- **Choice**: Pure Python 3 standard library over pip packages (e.g. networkx, pydantic).\n"
            "- **Why**: Prevents supply-chain bloat, portability failure, and environment drift across spoke repositories.\n\n"
            "## ADR-002: ast-grep as Single Native Binary Prerequisite\n"
            "- **Choice**: Registered `ast-grep` (`sg`) with standard Python AST / regex fallback.\n"
            "- **Why**: High-speed multi-language AST querying for Dart, TypeScript, Kotlin, Rust without language servers.\n\n"
            "## ADR-003: Lowest Viable Tier (LVT) Principle\n"
            "- **Choice**: Distillation downwards to Lowest Viable Tier (Tier 0 > 1 > 2 > 3).\n"
            "- **Why**: Irreducible cognitive complexity must rest at its lowest viable tier; static checks become Tier 0.\n"
        )
        with open(decisions_path, 'w', encoding='utf-8') as f:
            f.write(decisions_content)

        # 4. 03-Status.md
        status_path = os.path.join(self.brain_dir, "03-Status.md")
        status_content = (
            f"# 03 Status — Session Working State\n\n"
            f"> Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "## Done\n"
            "- [x] PageRank Repo-Map absorbed into `scanner.py`.\n"
            "- [x] Polyglot AST security & cryptographic canary defense absorbed into `security.py`.\n"
            "- [x] Mechanical mutation testing absorbed into `commands/verify_agents.py`.\n"
            "- [x] VirtualMemoryHierarchy & DualLevelGraphRAG Louvain clustering in `memory.py`.\n"
            "- [x] Layer 2 AST Token Compression & Layer 3 Distillation in `commands/brain.py`.\n"
            "- [x] VerbalReflectiveLearner failure pattern & DeclarativePromptPipeline compiler in `reflexion.py`.\n"
            "- [x] Lowest Viable Tier (LVT) Principle codified in `self-evolve/SKILL.md`.\n"
            "- [x] Native Second Brain & Obsidian Vault Exporter in `memory.py`.\n\n"
            "## In Progress\n"
            "- [ ] Project-wide spoke testing & pre-commit validation.\n\n"
            "## Next Steps\n"
            "- Execute `/session-offload` to finalize session handoff state.\n"
        )
        with open(status_path, 'w', encoding='utf-8') as f:
            f.write(status_content)

        return {
            "overview": overview_path,
            "map": map_path,
            "decisions": decisions_path,
            "status": status_path
        }

    def _compute_god_nodes(self) -> List[Tuple[str, float, str]]:
        """
        Computes the project's God Nodes dynamically using PageRank centrality
        from core.scanner.build_repo_map().
        """
        try:
            from core.scanner import build_repo_map
            workspace_root = os.getcwd()
            if os.path.basename(workspace_root) == ".agents":
                workspace_root = os.path.dirname(workspace_root)
            repo_data = build_repo_map(workspace_root, budget_tokens=2000)
            ranked = repo_data.get("ranked_files", [])
            if ranked:
                nodes = []
                cmap: Dict[str, int] = {}
                try:
                    from core.orion_graph import OrionGraphStore
                    with OrionGraphStore(self.db_path) as _store:
                        cmap = _store.compute_louvain_communities()
                except Exception as _lge:
                    _log_telemetry(_lge, "SecondBrainManager:louvain_lookup")

                for item in ranked[:10]:
                    fpath = item.get("file", "")
                    rank = round(float(item.get("rank", 0.0)), 4)
                    defs = item.get("definitions_count", 0)
                    comm_id = cmap.get(os.path.basename(fpath)) or cmap.get(fpath)
                    comm_tag = f" [Louvain Cluster #{comm_id}]" if comm_id is not None else ""
                    role = f"Central graph node ({defs} primary symbols){comm_tag}"
                    nodes.append((fpath, rank, role))
                return nodes
        except Exception as _e:
            _log_telemetry(_e, "SecondBrainManager:_compute_god_nodes")

        # Fallback to structural anchor files if repo scan returns empty
        fallback_anchors = [
            ("GEMINI.md", 0.15, "Master BIOS, JIT router, and prompt guardrails"),
            (".agents/scripts/orion.py", 0.14, "Unified CLI command dispatcher"),
            (".agents/scripts/core/memory.py", 0.13, "OS Virtual Memory & Second Brain Engine"),
            (".agents/scripts/core/scanner.py", 0.12, "PageRank code topology & symbol scanner"),
            (".agents/scripts/core/security.py", 0.11, "Polyglot AST vulnerability & canary auditor"),
            (".agents/rules/core-guardrails.md", 0.10, "Immutable engineering invariants"),
        ]
        return fallback_anchors
