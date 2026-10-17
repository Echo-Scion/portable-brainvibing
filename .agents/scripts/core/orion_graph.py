import os
import sys
import sqlite3
import json
import re
import math
import argparse
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Any, Optional

try:
    from core import log_telemetry as _log_telemetry
except ImportError:
    def _log_telemetry(err: Exception = None, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG"):
            msg = f": {err}" if err else ""
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")


if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception as _e:
        _log_telemetry(_e, 'orion_graph.py:reconfigure')


# Import unified primitives from core.kernel
_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

try:
    from core import (
        connect_sqlite,
        get_persistence_db_path,
        log_telemetry as _kernel_log_telemetry,
    )
    def _log_telemetry(err: Exception, context: str = "") -> None:
        _kernel_log_telemetry(err, context)
except ImportError:
    def _log_telemetry(err: Exception, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG"):
            msg = f": {err}" if err else ""
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")
    def connect_sqlite(db_path, wal=True, timeout_sec=5.0):
        conn = sqlite3.connect(db_path, timeout=timeout_sec)
        conn.execute(f"PRAGMA busy_timeout={int(timeout_sec * 1000)};")
        return conn
    def get_persistence_db_path():
        return os.path.join(os.getcwd(), ".orion", "orion.db")

from core.db import build_fts_query_or as sanitize_fts_query


class OrionGraphStore:
    """
    Production-grade Hierarchical DualLevelGraphRAG Store.
    Combines SQLite3 FTS5 Robertson BM25 full-text indexing, entity-triplet store,
    pure-Python multi-level Louvain modularity clustering, and dual-level retrieval.
    Zero external pip dependencies.
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(get_persistence_db_path())
        self._closed = False
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
            self.conn = connect_sqlite(self.db_path)
        else:
            self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self._configure_connection()
        self.init_schema()

    def _configure_connection(self) -> None:
        try:
            self.conn.execute("PRAGMA foreign_keys = ON;")
            self.conn.execute("PRAGMA synchronous = NORMAL;")
        except Exception as _e:
            _log_telemetry(_e, "configure_connection")

    def init_schema(self) -> None:
        """Initializes relational tables and SQLite3 FTS5 virtual tables with synchronization triggers."""
        cur = self.conn.cursor()

        # 1. Entities / Nodes Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL,
                description TEXT DEFAULT '',
                source_path TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)

        # 2. Entities FTS5 Full-Text Index
        cur.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS entities_fts USING fts5(
                name,
                type,
                description,
                source_path UNINDEXED,
                tokenize = 'porter unicode61'
            );
        """)

        # Sync Triggers for Entities FTS
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS entities_ai AFTER INSERT ON entities BEGIN
                INSERT INTO entities_fts(rowid, name, type, description, source_path)
                VALUES (new.id, new.name, new.type, new.description, new.source_path);
            END;
        """)
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS entities_ad AFTER DELETE ON entities BEGIN
                DELETE FROM entities_fts WHERE rowid = old.id;
            END;
        """)
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS entities_au AFTER UPDATE ON entities BEGIN
                DELETE FROM entities_fts WHERE rowid = old.id;
                INSERT INTO entities_fts(rowid, name, type, description, source_path)
                VALUES (new.id, new.name, new.type, new.description, new.source_path);
            END;
        """)

        # 3. Relations / Triplets Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object_id TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                provenance TEXT DEFAULT 'EXTRACTED',
                source_path TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now')),
                UNIQUE(subject_id, predicate, object_id)
            );
        """)

        # 4. Relations FTS5 Full-Text Index
        cur.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS relations_fts USING fts5(
                subject_id,
                predicate,
                object_id,
                tokenize = 'porter unicode61'
            );
        """)

        # Sync Triggers for Relations FTS
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS relations_ai AFTER INSERT ON relations BEGIN
                INSERT INTO relations_fts(rowid, subject_id, predicate, object_id)
                VALUES (new.id, new.subject_id, new.predicate, new.object_id);
            END;
        """)
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS relations_ad AFTER DELETE ON relations BEGIN
                DELETE FROM relations_fts WHERE rowid = old.id;
            END;
        """)
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS relations_au AFTER UPDATE ON relations BEGIN
                DELETE FROM relations_fts WHERE rowid = old.id;
                INSERT INTO relations_fts(rowid, subject_id, predicate, object_id)
                VALUES (new.id, new.subject_id, new.predicate, new.object_id);
            END;
        """)

        # 5. Louvain Hierarchical Communities Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS communities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level INTEGER NOT NULL,
                cluster_id INTEGER NOT NULL,
                dominant_type TEXT,
                size INTEGER NOT NULL,
                summary TEXT NOT NULL,
                modularity_q REAL DEFAULT 0.0,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)

        # 6. Communities FTS5 Full-Text Index
        cur.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS communities_fts USING fts5(
                dominant_type,
                summary,
                tokenize = 'porter unicode61'
            );
        """)

        # Sync Triggers for Communities FTS
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS communities_ai AFTER INSERT ON communities BEGIN
                INSERT INTO communities_fts(rowid, dominant_type, summary)
                VALUES (new.id, new.dominant_type, new.summary);
            END;
        """)
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS communities_ad AFTER DELETE ON communities BEGIN
                DELETE FROM communities_fts WHERE rowid = old.id;
            END;
        """)

        # 7. Community Membership Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS community_members (
                community_id INTEGER NOT NULL,
                entity_name TEXT NOT NULL,
                PRIMARY KEY (community_id, entity_name),
                FOREIGN KEY (community_id) REFERENCES communities(id) ON DELETE CASCADE
            );
        """)

        self.conn.commit()
        try:
            cur.execute("PRAGMA table_info(relations)")
            cols = {r[1] for r in cur.fetchall()}
            if "provenance" not in cols:
                cur.execute("ALTER TABLE relations ADD COLUMN provenance TEXT DEFAULT 'EXTRACTED'")
                self.conn.commit()
        except Exception as _e:
            _log_telemetry(_e, "orion_graph:migrate_provenance")

    def add_entity(self, name: str, entity_type: str, description: str = "", source_path: str = "") -> int:
        """Adds or updates an entity node in the knowledge graph."""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO entities (name, type, description, source_path)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                type = excluded.type,
                description = CASE WHEN excluded.description != '' THEN excluded.description ELSE entities.description END,
                source_path = CASE WHEN excluded.source_path != '' THEN excluded.source_path ELSE entities.source_path END
        """, (name.strip(), entity_type.strip(), description.strip(), source_path.strip()))
        self.conn.commit()
        return cur.lastrowid

    def add_triplet(
        self,
        subject: str,
        predicate: str,
        object_: str,
        weight: float = 1.0,
        source_path: str = "",
        provenance: str = "EXTRACTED",
    ) -> None:
        """Adds an entity relationship triplet with Orion Knowledge Graph provenance ('EXTRACTED'|'INFERRED'|'AMBIGUOUS')."""
        s = subject.strip()
        p = predicate.strip()
        o = object_.strip()
        if not s or not p or not o:
            return
        prov = provenance.upper() if provenance.upper() in ("EXTRACTED", "INFERRED", "AMBIGUOUS") else "EXTRACTED"

        cur = self.conn.cursor()
        # Ensure subject and object exist in entities table
        cur.execute("INSERT OR IGNORE INTO entities (name, type) VALUES (?, 'unknown')", (s,))
        cur.execute("INSERT OR IGNORE INTO entities (name, type) VALUES (?, 'unknown')", (o,))

        cur.execute("""
            INSERT INTO relations (subject_id, predicate, object_id, weight, provenance, source_path)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(subject_id, predicate, object_id) DO UPDATE SET
                weight = relations.weight + excluded.weight,
                provenance = excluded.provenance
        """, (s, p, o, float(weight), prov, source_path.strip()))
        self.conn.commit()

    def sync_from_legacy_tables(self) -> int:
        """
        Harmonizes legacy nodes & edges tables into entities & relations,
        then automatically triggers Louvain clustering if new relations exist.
        Returns count of synced edges.
        """
        cur = self.conn.cursor()
        # Check if legacy tables exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'")
        has_nodes = bool(cur.fetchone())
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='edges'")
        has_edges = bool(cur.fetchone())

        if not has_edges:
            return 0

        # Ingest legacy nodes
        legacy_ids = {}
        if has_nodes:
            cur.execute("SELECT id, type, name, source_path FROM nodes")
            for r in cur.fetchall():
                n_id = r[0] if isinstance(r, (tuple, list)) else r["id"]
                n_type = r[1] if isinstance(r, (tuple, list)) else r["type"]
                n_name = (r[2] if isinstance(r, (tuple, list)) else r["name"]) or ""
                n_source = (r[3] if isinstance(r, (tuple, list)) else r["source_path"]) or ""
                legacy_ids[str(n_id)] = n_name or str(n_id)
                self.add_entity(
                    n_name or n_id,
                    n_type or "node",
                    description=n_name,
                    source_path=n_source,
                )

        # Ingest legacy edges, including older schemas without source_path.
        cur.execute("PRAGMA table_info(edges)")
        edge_columns = {row[1] for row in cur.fetchall()}
        if "source_path" in edge_columns:
            cur.execute("SELECT source_id, target_id, relation, confidence, source_path FROM edges")
        else:
            cur.execute("SELECT source_id, target_id, relation, confidence FROM edges")
        edge_rows = cur.fetchall()
        for r in edge_rows:
            src = r[0] if isinstance(r, (tuple, list)) else r["source_id"]
            tgt = r[1] if isinstance(r, (tuple, list)) else r["target_id"]
            rel = r[2] if isinstance(r, (tuple, list)) else r["relation"]
            w = r[3] if isinstance(r, (tuple, list)) else r["confidence"]
            sf = (
                (r[4] if isinstance(r, (tuple, list)) else r["source_path"])
                if "source_path" in edge_columns
                else ""
            ) or ""
            self.add_triplet(
                legacy_ids.get(str(src), str(src)),
                rel or "related_to",
                legacy_ids.get(str(tgt), str(tgt)),
                weight=float(w or 1.0),
                source_path=sf,
            )

        # Trigger Louvain clustering to synthesize macro communities
        self.compute_louvain_communities()
        return len(edge_rows)

    # === PURE-PYTHON LOUVAIN MODULARITY CLUSTERING ===

    def compute_louvain_communities(self) -> Dict[str, int]:
        """
        Executes pure-Python multi-level Louvain community clustering.
        Maximizes Newman-Girvan Modularity:
          Q = 1/(2m) * sum_{ij} [ A_{ij} - (k_i * k_j) / (2m) ] * delta(c_i, c_j)
        with O(1) delta-Q local moves and multi-level super-node aggregation.
        Returns mapping of entity_name -> cluster_id (at the highest modularity level).
        """
        cur = self.conn.cursor()
        cur.execute("SELECT name, type FROM entities")
        entity_rows = cur.fetchall()
        entities = [r["name"] for r in entity_rows]
        entity_types = {r["name"]: r["type"] for r in entity_rows}

        if not entities:
            return {}

        cur.execute("SELECT subject_id, predicate, object_id, weight FROM relations")
        relation_rows = cur.fetchall()

        # Build undirected graph: node_idx <-> name
        node_to_idx = {name: i for i, name in enumerate(entities)}
        idx_to_node = {i: name for i, name in enumerate(entities)}
        N = len(entities)

        adj: Dict[int, Dict[int, float]] = {i: defaultdict(float) for i in range(N)}
        total_weight_accum = 0.0

        for r in relation_rows:
            u_name = r["subject_id"]
            v_name = r["object_id"]
            if u_name in node_to_idx and v_name in node_to_idx:
                u = node_to_idx[u_name]
                v = node_to_idx[v_name]
                w = float(r["weight"])
                if u != v:
                    adj[u][v] += w
                    adj[v][u] += w
                    total_weight_accum += w
                else:
                    adj[u][u] += 2.0 * w
                    total_weight_accum += w

        m = total_weight_accum  # Total graph edge weight
        if m <= 0.0:
            # Disconnected / edgeless graph: each node in its own community
            trivial_map = {name: i for i, name in enumerate(entities)}
            self._record_communities_level(0, trivial_map, entities, entity_types, relation_rows, 0.0)
            return trivial_map

        # Multi-level hierarchical Louvain
        current_adj = adj
        current_node_count = N
        node_community_mapping = {i: i for i in range(N)}
        level = 0
        best_modularity = -1.0

        while True:
            # Phase 1: Local modularity optimization on current level graph
            partition, mod_q = self._louvain_phase_one(current_adj, current_node_count, m)
            
            # Map original node IDs to new communities
            new_node_community_mapping = {}
            for orig_idx, curr_cluster in node_community_mapping.items():
                new_node_community_mapping[orig_idx] = partition[curr_cluster]

            node_community_mapping = new_node_community_mapping

            # Number of unique communities formed
            unique_communities = sorted(list(set(partition.values())))
            
            if level > 0 and (
                mod_q - best_modularity < 1e-4
                or len(unique_communities) >= current_node_count
            ):
                break

            # Save this hierarchy level
            final_name_to_cluster = {idx_to_node[i]: node_community_mapping[i] for i in range(N)}
            self._record_communities_level(level, final_name_to_cluster, entities, entity_types, relation_rows, mod_q)
            best_modularity = max(best_modularity, mod_q)

            if len(unique_communities) == 1:
                break

            # Phase 2: Community aggregation (coarse graph construction)
            current_adj, current_node_count = self._louvain_phase_two(current_adj, partition, unique_communities)
            level += 1

        final_mapping = {idx_to_node[i]: node_community_mapping[i] for i in range(N)}
        return final_mapping

    @staticmethod
    def _louvain_phase_one(
        adj: Dict[int, Dict[int, float]],
        num_nodes: int,
        m: float
    ) -> Tuple[Dict[int, int], float]:
        """
        Phase 1: Moves nodes to neighboring communities that maximize modularity gain Delta Q in O(1).
        Delta Q(i -> C) = k_{i, in}(C) / m - (Sigma_tot(C) * k_i) / (2 * m^2)
        """
        # Node degrees: k_i = sum_j A_{ij}
        degrees = {i: sum(adj[i].values()) for i in range(num_nodes)}
        
        # Initial partition: each node in its own community
        community = {i: i for i in range(num_nodes)}
        sigma_tot = {i: degrees[i] for i in range(num_nodes)}
        sigma_in = {i: adj[i].get(i, 0.0) for i in range(num_nodes)}

        two_m = 2.0 * m
        two_m_sq = 2.0 * (m ** 2)

        improved = True
        passes = 0
        max_passes = 25

        while improved and passes < max_passes:
            improved = False
            passes += 1

            for i in range(num_nodes):
                c_orig = community[i]
                k_i = degrees[i]
                if k_i == 0.0:
                    continue

                # Compute connections from i to its current community c_orig (excluding self-loop)
                k_i_in_orig = sum(w for j, w in adj[i].items() if community[j] == c_orig and j != i)

                # Remove i from its current community
                sigma_tot[c_orig] -= k_i
                sigma_in[c_orig] -= (2.0 * k_i_in_orig + adj[i].get(i, 0.0))

                # Weight to neighboring communities
                weights_to_comm: Dict[int, float] = defaultdict(float)
                for j, w in adj[i].items():
                    if j != i:
                        weights_to_comm[community[j]] += w

                stay_gain = (k_i_in_orig / m) - (sigma_tot[c_orig] * k_i / two_m_sq)
                best_comm = c_orig
                best_gain = 0.0

                # Evaluate delta Q for moving i into neighbor communities
                for c_cand, k_i_in_cand in weights_to_comm.items():
                    if c_cand == c_orig:
                        continue
                    cand_gain = (k_i_in_cand / m) - (sigma_tot[c_cand] * k_i / two_m_sq)
                    net_delta_q = cand_gain - stay_gain
                    if net_delta_q > best_gain + 1e-9:
                        best_gain = net_delta_q
                        best_comm = c_cand

                # Insert i into best community
                community[i] = best_comm
                sigma_tot[best_comm] += k_i
                k_i_in_best = weights_to_comm[best_comm] if best_comm != c_orig else k_i_in_orig
                sigma_in[best_comm] += (2.0 * k_i_in_best + adj[i].get(i, 0.0))

                if best_comm != c_orig:
                    improved = True

        # Calculate final modularity Q for partition:
        # Q = sum_c [ sigma_in[c] / (2m) - (sigma_tot[c] / (2m))^2 ]
        q = 0.0
        unique_comms = set(community.values())
        for c in unique_comms:
            in_w = sigma_in[c]
            tot_w = sigma_tot[c]
            q += (in_w / two_m) - ((tot_w / two_m) ** 2)

        # Renumber communities to contiguous integers 0..K-1
        comm_remap = {}
        for c in community.values():
            if c not in comm_remap:
                comm_remap[c] = len(comm_remap)
        normalized_community = {i: comm_remap[community[i]] for i in range(num_nodes)}

        return normalized_community, q

    @staticmethod
    def _louvain_phase_two(
        adj: Dict[int, Dict[int, float]],
        partition: Dict[int, int],
        unique_communities: List[int]
    ) -> Tuple[Dict[int, Dict[int, float]], int]:
        """
        Phase 2: Aggregates communities into super-nodes to construct the coarse graph.
        """
        num_super_nodes = len(unique_communities)
        super_adj: Dict[int, Dict[int, float]] = {c: defaultdict(float) for c in range(num_super_nodes)}

        for u, neighbors in adj.items():
            c_u = partition[u]
            for v, weight in neighbors.items():
                c_v = partition[v]
                super_adj[c_u][c_v] += weight

        return super_adj, num_super_nodes

    def _record_communities_level(
        self,
        level: int,
        name_to_cluster: Dict[str, int],
        entities: List[str],
        entity_types: Dict[str, str],
        relation_rows: List[sqlite3.Row],
        modularity_q: float
    ) -> None:
        """Saves community clustering results and generates macro summaries into SQLite & FTS5."""
        cur = self.conn.cursor()

        # Group entities by cluster_id
        clusters: Dict[int, List[str]] = defaultdict(list)
        for name, cid in name_to_cluster.items():
            clusters[cid].append(name)

        # Pre-group intra-cluster relations in a single O(E) pass
        intra_by_cluster: Dict[int, List[str]] = defaultdict(list)
        for r in relation_rows:
            c_u = name_to_cluster.get(r["subject_id"])
            c_v = name_to_cluster.get(r["object_id"])
            if c_u is not None and c_u == c_v and len(intra_by_cluster[c_u]) < 4:
                intra_by_cluster[c_u].append(f"{r['subject_id']} --{r['predicate']}--> {r['object_id']}")

        # Clear existing communities at this level to support re-clustering
        cur.execute("DELETE FROM communities WHERE level = ?", (level,))

        member_records: List[Tuple[int, str]] = []
        for cid, members in clusters.items():
            size = len(members)
            types = [entity_types.get(m, "unknown") for m in members]
            type_counts = Counter(types)
            dominant_type = type_counts.most_common(1)[0][0] if type_counts else "general"

            intra_relations = intra_by_cluster.get(cid, [])
            rel_str = "; ".join(intra_relations) if intra_relations else "co-located module elements"
            top_entities = members[:6]
            summary = (
                f"Community #{cid} (Level {level}, {size} members, dominant: {dominant_type}). "
                f"Core entities: {', '.join(top_entities)}. Relationships: {rel_str}."
            )

            cur.execute("""
                INSERT INTO communities (level, cluster_id, dominant_type, size, summary, modularity_q)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (level, cid, dominant_type, size, summary, float(modularity_q)))
            comm_id = cur.lastrowid

            for m in members:
                member_records.append((comm_id, m))

        if member_records:
            cur.executemany("""
                INSERT OR REPLACE INTO community_members (community_id, entity_name)
                VALUES (?, ?)
            """, member_records)

        self.conn.commit()

    def search_dual_level(
        self,
        query: str,
        top_k_communities: int = 3,
        top_k_entities: int = 5
    ) -> Dict[str, Any]:
        """
        Executes Hierarchical DualLevelGraphRAG retrieval:
        1. Macro Level: Queries global community summaries via SQLite3 FTS5 BM25.
        2. Micro Level: Queries local entities and relationship triplets via SQLite3 FTS5 BM25.
        3. Context Fusion: Synthesizes macro and micro results into a unified prompt context.
        """
        return self._search_dual_level_impl(query, top_k_communities, top_k_entities)

    def dual_level_query(
        self,
        query: str,
        top_k_communities: int = 3,
        top_k_entities: int = 5
    ) -> Dict[str, Any]:
        """Alias for search_dual_level."""
        return self.search_dual_level(query, top_k_communities, top_k_entities)

    def _search_dual_level_impl(
        self,
        query: str,
        top_k_communities: int = 3,
        top_k_entities: int = 5
    ) -> Dict[str, Any]:
        clean_fts_query = sanitize_fts_query(query)
        cur = self.conn.cursor()

        macro_results: List[Dict[str, Any]] = []
        micro_entities: List[Dict[str, Any]] = []
        triplets: List[Dict[str, Any]] = []

        if clean_fts_query:
            # 1. Macro Search: Communities FTS5 BM25
            try:
                cur.execute("""
                    SELECT c.id, c.level, c.cluster_id, c.dominant_type, c.size, c.summary, c.modularity_q,
                           bm25(communities_fts) as rank
                    FROM communities_fts
                    JOIN communities c ON communities_fts.rowid = c.id
                    WHERE communities_fts MATCH ?
                    ORDER BY rank ASC
                    LIMIT ?
                """, (clean_fts_query, top_k_communities))
                for r in cur.fetchall():
                    m_cur = self.conn.cursor()
                    m_cur.execute("SELECT entity_name FROM community_members WHERE community_id = ? LIMIT 8", (r["id"],))
                    comm_members = [m["entity_name"] for m in m_cur.fetchall()]
                    macro_results.append({
                        "id": r["id"],
                        "level": r["level"],
                        "cluster_id": r["cluster_id"],
                        "dominant_type": r["dominant_type"],
                        "size": r["size"],
                        "summary": r["summary"],
                        "members": comm_members,
                        "modularity_q": r["modularity_q"],
                        "bm25_score": round(float(r["rank"]), 4)
                    })
            except Exception as _e:
                _log_telemetry(_e, "search_communities_fts")

            # 2. Micro Search: Entities FTS5 BM25
            try:
                cur.execute("""
                    SELECT e.id, e.name, e.type, e.description, e.source_path,
                           bm25(entities_fts) as rank
                    FROM entities_fts
                    JOIN entities e ON entities_fts.rowid = e.id
                    WHERE entities_fts MATCH ?
                    ORDER BY rank ASC
                    LIMIT ?
                """, (clean_fts_query, top_k_entities))
                for r in cur.fetchall():
                    micro_entities.append({
                        "id": r["id"],
                        "name": r["name"],
                        "type": r["type"],
                        "description": r["description"],
                        "source_path": r["source_path"],
                        "bm25_score": round(float(r["rank"]), 4)
                    })
            except Exception as _e:
                _log_telemetry(_e, "search_entities_fts")

            # 3. Micro Triplets: Fetch immediate relation edges for matched entities
            matched_names = [e["name"] for e in micro_entities]
            if matched_names:
                placeholders = ",".join("?" for _ in matched_names)
                try:
                    cur.execute(f"""
                        SELECT subject_id, predicate, object_id, weight, source_path
                        FROM relations
                        WHERE subject_id IN ({placeholders}) OR object_id IN ({placeholders})
                        ORDER BY weight DESC
                        LIMIT 15
                    """, matched_names + matched_names)
                    for r in cur.fetchall():
                        triplets.append({
                            "subject": r["subject_id"],
                            "predicate": r["predicate"],
                            "object": r["object_id"],
                            "weight": float(r["weight"]),
                            "source_path": r["source_path"]
                        })
                except Exception as _e:
                    _log_telemetry(_e, "search_relations_triplets")

            # 3b. Direct FTS5 Relation Search via relations_fts
            if len(triplets) < 5:
                try:
                    cur.execute("""
                        SELECT r.subject_id, r.predicate, r.object_id, r.weight, r.source_path
                        FROM relations_fts
                        JOIN relations r ON relations_fts.rowid = r.id
                        WHERE relations_fts MATCH ?
                        ORDER BY r.weight DESC
                        LIMIT 10
                    """, (clean_fts_query,))
                    for r in cur.fetchall():
                        cand = {
                            "subject": r["subject_id"],
                            "predicate": r["predicate"],
                            "object": r["object_id"],
                            "weight": float(r["weight"]),
                            "source_path": r["source_path"]
                        }
                        if cand not in triplets:
                            triplets.append(cand)
                except Exception as _e:
                    _log_telemetry(_e, "search_relations_fts")

        # 4. Context Fusion Synthesis
        context_blocks = []
        if macro_results:
            context_blocks.append("=== MACRO COMMUNITY CONTEXT (System Level) ===")
            for c in macro_results:
                context_blocks.append(f"• [Level {c['level']} Cluster {c['cluster_id']} - {c['dominant_type']}] {c['summary']}")

        if micro_entities:
            context_blocks.append("\n=== MICRO ENTITY DEFINITIONS ===")
            for e in micro_entities:
                desc = f": {e['description']}" if e['description'] else ""
                src = f" ({e['source_path']})" if e['source_path'] else ""
                context_blocks.append(f"• [{e['type']}] {e['name']}{desc}{src}")

        if triplets:
            context_blocks.append("\n=== KNOWLEDGE GRAPH RELATION TRACES ===")
            for t in triplets:
                context_blocks.append(f"• ({t['subject']}) --[{t['predicate']} (w={t['weight']})]--> ({t['object']})")

        fusion_context = "\n".join(context_blocks).strip()
        if not fusion_context:
            fusion_context = "(No matching graph entities or community summaries found for query)"

        return {
            "query": query,
            "sanitized_query": clean_fts_query,
            "macro_communities": macro_results,
            "micro_entities": micro_entities,
            "triplets": triplets,
            "fusion_context": fusion_context
        }

    def find_shortest_path(self, source_entity: str, target_entity: str, max_hops: int = 5) -> List[Dict[str, Any]]:
        """Orion BFS Shortest Path Tracer between two entities across the knowledge graph."""
        from collections import deque
        cur = self.conn.cursor()
        cur.execute("SELECT subject_id, predicate, object_id, weight, COALESCE(provenance, 'EXTRACTED') as provenance FROM relations")
        adj: Dict[str, List[Tuple[str, str, float, str, str]]] = defaultdict(list)
        nodes_lower: Dict[str, str] = {}
        for r in cur.fetchall():
            u, pred, v, w, prov = r["subject_id"], r["predicate"], r["object_id"], float(r["weight"]), r["provenance"]
            adj[u].append((v, pred, w, prov, "->"))
            adj[v].append((u, pred, w, prov, "<-"))
            nodes_lower[u.lower()] = u
            nodes_lower[v.lower()] = v

        start = nodes_lower.get(source_entity.strip().lower(), source_entity.strip())
        goal = nodes_lower.get(target_entity.strip().lower(), target_entity.strip())
        if start == goal:
            return [{"step": 0, "from": start, "predicate": "SELF", "to": goal, "provenance": "EXTRACTED"}]

        queue = deque([(start, [])])
        visited = {start}
        while queue:
            curr, path = queue.popleft()
            if len(path) >= max_hops:
                continue
            for nxt, pred, w, prov, direction in adj.get(curr, []):
                step_info = {
                    "step": len(path) + 1,
                    "from": curr if direction == "->" else nxt,
                    "predicate": pred,
                    "to": nxt if direction == "->" else curr,
                    "direction": direction,
                    "weight": w,
                    "provenance": prov,
                }
                if nxt == goal:
                    return path + [step_info]
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + [step_info]))
        return []

    def explain_entity(self, entity_name: str) -> Dict[str, Any]:
        """Orion Explain Node: returns full entity metadata, community cluster, and 1-hop provenance edges."""
        cur = self.conn.cursor()
        cur.execute("SELECT name, type, description, source_path FROM entities WHERE lower(name) = lower(?) LIMIT 1", (entity_name.strip(),))
        row = cur.fetchone()
        if not row:
            cur.execute("SELECT name, type, description, source_path FROM entities WHERE lower(name) LIKE ? LIMIT 1", (f"%{entity_name.strip().lower()}%",))
            row = cur.fetchone()
        target_name = row["name"] if row else entity_name.strip()
        info = dict(row) if row else {"name": target_name, "type": "unknown", "description": "", "source_path": ""}

        cur.execute("""
            SELECT subject_id, predicate, object_id, weight, COALESCE(provenance, 'EXTRACTED') as provenance, source_path
            FROM relations
            WHERE lower(subject_id) = lower(?) OR lower(object_id) = lower(?)
            ORDER BY weight DESC LIMIT 25
        """, (target_name, target_name))
        edges = [dict(r) for r in cur.fetchall()]

        cur.execute("""
            SELECT c.cluster_id, c.level, c.dominant_type, c.summary
            FROM community_members cm
            JOIN communities c ON cm.community_id = c.id
            WHERE lower(cm.entity_name) = lower(?)
            ORDER BY c.level DESC LIMIT 1
        """, (target_name,))
        comm_row = cur.fetchone()
        return {
            "entity": info,
            "community": dict(comm_row) if comm_row else None,
            "relations": edges,
        }

    def get_stats(self) -> Dict[str, int]:
        """Returns entity, relation, and community counts."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM entities")
        n_entities = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM relations")
        n_relations = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM communities")
        n_communities = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM community_members")
        n_members = cur.fetchone()[0]
        return {
            "entities_count": n_entities,
            "relations_count": n_relations,
            "communities_count": n_communities,
            "community_members_count": n_members
        }

    @property
    def is_closed(self) -> bool:
        """Return whether underlying connection has been closed."""
        return self._closed

    def get_community_members(self, community_id: int) -> List[str]:
        """Returns entity names belonging to a community cluster."""
        cur = self.conn.cursor()
        cur.execute("SELECT entity_name FROM community_members WHERE community_id = ?", (community_id,))
        return [r["entity_name"] for r in cur.fetchall()]

    def close(self) -> None:
        """Closes the underlying SQLite connection."""
        if self._closed:
            return
        try:
            self.conn.close()
            self._closed = True
        except Exception as _e:
            _log_telemetry(_e, "orion_graph.py:close")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# === CLI DISPATCH ===

def main() -> None:
    known_actions = {"init", "cluster", "search", "query", "path", "explain", "add-entity", "add-triplet", "stats"}
    if len(sys.argv) > 1 and sys.argv[1] in known_actions:
        sys.argv.insert(1, str(get_persistence_db_path()))

    parser = argparse.ArgumentParser(description="Orion Graph Store & Knowledge Graph Engine CLI")
    parser.add_argument("db_path", nargs="?", default=str(get_persistence_db_path()), help="Path to SQLite3 graph database file")
    subparsers = parser.add_subparsers(dest="action")

    # init
    subparsers.add_parser("init", help="Initialize database schema and FTS5 virtual tables")

    # cluster
    subparsers.add_parser("cluster", help="Compute pure-Python Louvain communities and generate summaries")

    # search
    search_parser = subparsers.add_parser("search", help="Perform dual-level retrieval")
    search_parser.add_argument("query", help="Search query string")
    search_parser.add_argument("--communities", type=int, default=3, help="Top-K macro communities")
    search_parser.add_argument("--entities", type=int, default=5, help="Top-K micro entities")
    search_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # query
    query_parser = subparsers.add_parser("query", help="Orion dual-level query")
    query_parser.add_argument("query", help="Search query string")
    query_parser.add_argument("--communities", type=int, default=3, help="Top-K macro communities")
    query_parser.add_argument("--entities", type=int, default=5, help="Top-K micro entities")
    query_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # path
    path_parser = subparsers.add_parser("path", help="Find shortest path between two entities")
    path_parser.add_argument("source", help="Source entity")
    path_parser.add_argument("target", help="Target entity")
    path_parser.add_argument("--max-hops", type=int, default=5, help="Max BFS hops")

    # explain
    explain_parser = subparsers.add_parser("explain", help="Explain an entity node and its provenance relations")
    explain_parser.add_argument("entity", help="Entity name")
    explain_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # add-entity
    add_e_parser = subparsers.add_parser("add-entity", help="Add an entity")
    add_e_parser.add_argument("name", help="Entity name")
    add_e_parser.add_argument("type", help="Entity type (e.g. class, function, module)")
    add_e_parser.add_argument("--desc", default="", help="Description")
    add_e_parser.add_argument("--path", default="", help="Source path")

    # add-triplet
    add_t_parser = subparsers.add_parser("add-triplet", help="Add a triplet")
    add_t_parser.add_argument("subject", help="Subject entity name")
    add_t_parser.add_argument("predicate", help="Predicate relation")
    add_t_parser.add_argument("object", help="Object entity name")
    add_t_parser.add_argument("--weight", type=float, default=1.0, help="Relation weight")
    add_t_parser.add_argument("--provenance", default="EXTRACTED", help="Relation provenance (EXTRACTED, INFERRED, AMBIGUOUS)")

    # stats
    subparsers.add_parser("stats", help="Show database graph statistics")

    args = parser.parse_args()
    store = OrionGraphStore(args.db_path)
    try:
        if args.action == "init":
            print(f"[OK] Initialized schema and FTS5 tables in: {args.db_path}")

        elif args.action == "cluster":
            print(f"[GRAPH] Computing pure-Python Louvain modularity clustering on: {args.db_path}")
            partition = store.compute_louvain_communities()
            stats = store.get_stats()
            print(f"[OK] Louvain clustering complete. Partitioned {len(partition)} entities into communities across {stats['communities_count']} cluster summaries.")

        elif args.action in ("search", "query"):
            comms = getattr(args, "communities", 3)
            ents = getattr(args, "entities", 5)
            result = store.search_dual_level(args.query, top_k_communities=comms, top_k_entities=ents)
            if getattr(args, "json", False):
                print(json.dumps(result, indent=2))
            else:
                print(f"\n🔍 DualLevelGraphRAG Search for: '{args.query}'")
                print("=" * 60)
                print(result["fusion_context"])

        elif args.action == "path":
            steps = store.find_shortest_path(args.source, args.target, max_hops=args.max_hops)
            if not steps:
                print(f"[ORION GRAPH PATH] No path found between '{args.source}' and '{args.target}' within {args.max_hops} hops.")
            else:
                print(f"🔗 Orion Graph Shortest Path ({len(steps)} hops): {args.source} -> {args.target}")
                for s in steps:
                    print(f"  {s['step']}. ({s['from']}) --[{s['predicate']} | {s['provenance']}]--> ({s['to']})")

        elif args.action == "explain":
            info = store.explain_entity(args.entity)
            if getattr(args, "json", False):
                print(json.dumps(info, indent=2))
            else:
                ent = info["entity"]
                print(f"🧠 Orion Graph Node Explain: {ent['name']} (Type: {ent['type']}, Source: {ent.get('source_path') or 'N/A'})")
                if info["community"]:
                    c = info["community"]
                    print(f"   Community: Cluster #{c['cluster_id']} (Level {c['level']}) - {c['summary']}")
                print(f"   Connected Relations ({len(info['relations'])}):")
                for r in info["relations"][:15]:
                    print(f"     • ({r['subject_id']}) --[{r['predicate']} | {r['provenance']}]--> ({r['object_id']})")

        elif args.action == "add-entity":
            eid = store.add_entity(args.name, args.type, description=args.desc, source_path=args.path)
            print(f"[OK] Added entity '{args.name}' with ID {eid}")

        elif args.action == "add-triplet":
            store.add_triplet(args.subject, args.predicate, args.object, weight=args.weight, provenance=getattr(args, "provenance", "EXTRACTED"))
            print(f"[OK] Added triplet: ({args.subject}) --[{args.predicate} | {getattr(args, 'provenance', 'EXTRACTED')}]--> ({args.object})")

        elif args.action == "stats":
            stats = store.get_stats()
            print(f"📊 Orion Graph Store Stats ({args.db_path}):")
            print(f"  • Entities    : {stats['entities_count']}")
            print(f"  • Relations   : {stats['relations_count']}")
            print(f"  • Communities : {stats['communities_count']}")

        else:
            stats = store.get_stats()
            print(f"Orion Graph Store: {args.db_path} (Entities: {stats['entities_count']}, Relations: {stats['relations_count']})")
            parser.print_help()
    finally:
        store.close()


if __name__ == "__main__":
    main()
