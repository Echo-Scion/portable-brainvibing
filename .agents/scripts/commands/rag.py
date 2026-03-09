"""
ORION RAG & RETRIEVAL MODULE (commands/rag.py)
Encapsulates vector mathematics, RAG diagnostic evaluation (relevance & faithfulness),
lexical/semantic hybrid search (BM25 + Dense Vector RRF + 1-hop Graph Traversal),
and ephemeral context paging.
"""

import datetime
import json
import math
import os
import re
import shutil
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Base directory anchoring
_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from core.paths import get_persistence_db_path, get_agents_dir, get_workspace_dir, get_orion_dir
from core.memory import calculate_retrieval_score

try:
    from core.db import (
        connect_sqlite,
        log_telemetry as _kernel_log_telemetry,
        pack_vector,
        unpack_vector,
        cosine_similarity,
        atomic_write_text,
    )
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
    def atomic_write_text(filepath: str, content: str) -> None:
        import uuid
        abs_path = os.path.abspath(str(filepath))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        tmp_path = f"{abs_path}.tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, abs_path)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
    def cosine_similarity(v1, v2):
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

compute_cosine = cosine_similarity


# ============================================================================
# SECTION 1: RAG DIAGNOSTICS & EVALUATION
# ============================================================================

class RAGDiagnosticJudge:
    """Evaluates RAG retrieval relevance and generation faithfulness using lexical & semantic metrics."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(get_persistence_db_path())
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = connect_sqlite(self.db_path)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS rag_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    retrieved_chunks INTEGER NOT NULL,
                    relevance_score REAL NOT NULL,
                    faithfulness_score REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

    def evaluate_retrieval(
        self, query: str, chunks: List[str], generated_answer: str = ""
    ) -> Dict[str, float]:
        """Calculates query-context relevance and answer-context faithfulness."""
        query_words = set(query.lower().split())
        chunk_text = " ".join(chunks).lower()
        chunk_words = set(chunk_text.split())

        # Relevance: Semantic embedding similarity via Ollama if available, otherwise lexical token overlap
        semantic_relevance = None
        try:
            from core.capabilities import resolve_ollama_base_url, get_embedding
            host = resolve_ollama_base_url()
            if host and chunks:
                q_emb = get_embedding(query, host=host)
                if q_emb:
                    chunk_summary = " ".join([ch[:400] for ch in chunks[:3]])
                    c_emb = get_embedding(chunk_summary, host=host)
                    if c_emb:
                        from core.db import cosine_similarity
                        semantic_relevance = max(0.0, min(1.0, cosine_similarity(q_emb, c_emb)))
        except Exception as _e:
            _log_telemetry(_e, "rag.py:semantic_relevance")

        if semantic_relevance is not None:
            relevance = semantic_relevance
        else:
            query_overlap = len(query_words.intersection(chunk_words))
            relevance = query_overlap / max(len(query_words), 1)

        # Faithfulness: fraction of answer tokens grounded in retrieved chunks
        if generated_answer:
            answer_words = set(generated_answer.lower().split())
            answer_overlap = len(answer_words.intersection(chunk_words))
            faithfulness = answer_overlap / max(len(answer_words), 1)
        else:
            # Context Grounding / Coverage Density (retrieval-only mode)
            segments = [seg.strip().lower() for ch in chunks for seg in re.split(r'[\n.!?]+', ch) if seg.strip()]
            if query_words and segments:
                grounded_terms = 0
                for qw in query_words:
                    hits = sum(1 for seg in segments if qw in seg)
                    if hits >= 2:
                        grounded_terms += 1
                faithfulness = grounded_terms / len(query_words)
            elif query_words and chunk_words:
                faithfulness = query_overlap / len(query_words)
            else:
                faithfulness = 0.0

        with self.conn:
            self.conn.execute(
                """
                INSERT INTO rag_evaluations (query, retrieved_chunks, relevance_score, faithfulness_score)
                VALUES (?, ?, ?, ?)
            """,
                (query, len(chunks), round(relevance, 4), round(faithfulness, 4)),
            )

        return {"relevance": round(relevance, 4), "faithfulness": round(faithfulness, 4)}

    def get_summary(self, limit: int = 50) -> Dict[str, Any]:
        """Returns aggregate retrieval performance statistics."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*), AVG(relevance_score), AVG(faithfulness_score)
            FROM (SELECT relevance_score, faithfulness_score FROM rag_evaluations ORDER BY id DESC LIMIT ?)
        """,
            (limit,),
        )
        row = cursor.fetchone()
        return {
            "eval_count": row[0] or 0,
            "mean_relevance": round(row[1] or 0.0, 4),
            "mean_faithfulness": round(row[2] or 0.0, 4),
        }

    def close(self) -> None:
        """Closes the underlying SQLite connection."""
        if self.conn:
            try:
                self.conn.close()
            except Exception as _e:
                _log_telemetry(_e, "rag.py:judge_close")
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def diagnostics_main(argv=None):
    judge = RAGDiagnosticJudge()
    stats = judge.get_summary()
    print(f"RAG Diagnostics Initialized. Total Evaluations: {stats['eval_count']}")
    judge.close()
    return 0


# ============================================================================
# SECTION 2: CONTEXT RETRIEVAL & BRAIN SYNC ENGINE
# ============================================================================

def extract_keywords(text: str) -> List[str]:
    """Extracts search tokens from text with optional local LLM semantic synonym expansion."""
    stop_words = {'i', 'need', 'to', 'build', 'the', 'a', 'an', 'and', 'or', 'for', 'with', 'on', 'in', 'of', 'how', 'do', 'what', 'create', 'make', 'update', 'fix'}
    words = re.findall(r'\b[a-zA-Z0-9_]+\b', text.lower())
    base_keywords = [w for w in words if w not in stop_words and len(w) > 2]

    # Semantic Expansion via NanoBrain
    try:
        from commands.brain import NanoBrain
        nb = NanoBrain()
        if nb.ping():
            sys_prompt = "You are a synonym generator. Output exactly 3 comma-separated technical synonyms for the intent. NO other text. Example: 'login' -> 'auth,authentication,session'"
            prompt = f"Intent: {text}\nSynonyms:"
            expansion = nb.generate(prompt, system=sys_prompt)
            if expansion:
                expanded_words = [w.strip().lower() for w in expansion.split(",") if w.strip()]
                expanded_words = [w for w in expanded_words if len(w.split()) == 1 and w.isalpha()]
                return sorted(list(set(base_keywords + expanded_words)))
    except Exception as _e:
        _log_telemetry(_e, 'rag.py:extract_keywords')

    return sorted(base_keywords)


def search_files(directory: str, keywords: List[str]) -> List[str]:
    """Scans markdown files in directory and scores relevance based on keyword overlap."""
    matches = []
    if not os.path.exists(directory):
        return matches

    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith('.md'):
                continue
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    score = sum(1 for kw in keywords if kw in content)
                    if score > 0:
                        if any(kw in file.lower() for kw in keywords):
                            score += 3
                        matches.append((score, filepath))
            except Exception as _e:
                _log_telemetry(_e, f'rag.py:search_files:{filepath}')

    matches.sort(reverse=True, key=lambda x: x[0])
    return [m[1] for m in matches[:3]]


def get_ast_block(filepath: str, tag_name: str) -> Optional[str]:
    """Extracts custom XML/AST tags from markdown files."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        match = re.search(f'<{tag_name}>(.*?)</{tag_name}>', content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    except Exception as _e:
        _log_telemetry(_e, f'rag.py:get_ast_block:{filepath}')
    return None


def _resolve_neighbor_target(cursor, target_id: str, workspace_dir: str, neighbor_files: List[str]) -> None:
    """
    1-Hop Traversal Resolver: Maps an edge target or entity symbol to a concrete file.
    Checks direct disk paths, .md suffixes, and matches in the SQLite 'pages' table.
    """
    if not target_id or len(target_id) < 2:
        return
    # 1. Direct path check
    candidates = [
        target_id,
        os.path.join(workspace_dir, target_id),
        os.path.join(workspace_dir, target_id + ".md")
    ]
    for cand in candidates:
        if os.path.exists(cand) and os.path.isfile(cand):
            abs_cand = os.path.abspath(cand)
            if abs_cand not in neighbor_files:
                neighbor_files.append(abs_cand)
            return

    # 2. Check SQLite pages index
    try:
        clean_name = target_id.replace(".md", "").strip()
        cursor.execute("SELECT path FROM pages WHERE path LIKE ? OR path LIKE ? LIMIT 1", (f"%/{clean_name}.md", f"%{clean_name}%"))
        row = cursor.fetchone()
        if row and row[0]:
            resolved = row[0]
            abs_resolved = resolved if os.path.isabs(resolved) else os.path.abspath(os.path.join(workspace_dir, resolved))
            if os.path.exists(abs_resolved) and abs_resolved not in neighbor_files:
                neighbor_files.append(abs_resolved)
    except Exception as _e:
        _log_telemetry(_e, 'rag.py:_resolve_neighbor_target')


def sync(intent: str, delta: bool = False) -> None:
    """
    Core RAG Engine: Reciprocal Rank Fusion of FTS5 BM25, Dense Vector Embeddings,
    1-Hop Knowledge Graph Traversal, and Louvain Community Context.
    """
    print(f" BRAIN ENGINE ENGAGED: Syncing context for intent: '{intent}'")
    keywords = extract_keywords(intent)
    print(f" Extracted Tokens: {keywords}")

    agents_dir = str(get_agents_dir())
    workspace_dir = os.path.dirname(agents_dir)
    orion_dir = os.path.join(workspace_dir, '.orion')
    context_dir = os.path.join(workspace_dir, 'context')
    cache_path = os.path.join(orion_dir, "working", "route_cache.json")
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    skills = search_files(os.path.join(agents_dir, 'skills'), keywords)

    # Semantic Route via Hybrid Graph & Vector (SQLite FTS5 + Flat Cosine)
    rules = []
    hop_triplets = []
    neighbor_files = []
    db_path = os.path.join(orion_dir, 'orion.db')
    clean_keywords = [re.sub(r'[^a-zA-Z0-9_]', '', kw) for kw in keywords]
    clean_keywords = [kw for kw in clean_keywords if len(kw) >= 2]
    query_str = " OR ".join([f'"{kw}"' for kw in clean_keywords])

    cache_data = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
        except Exception as _e:
            _log_telemetry(_e, 'rag.py:cache_load')

    if query_str and query_str in cache_data and not delta:
        print(f"  [CACHE HIT] Loaded semantic routes for '{query_str}' from RAM cache.")
        rules = cache_data[query_str]
    elif not delta:
        # Generate Intent Embedding
        query_embedding = None
        temp_nb = None
        try:
            from commands.brain import NanoBrain
            temp_nb = NanoBrain()
            if temp_nb.ping(capability="EMBED"):
                query_embedding = temp_nb.embed(intent)
                if query_embedding:
                    print("  [VECTOR SEARCH] Active. Embedding generated.")
        except Exception as _e:
            _log_telemetry(_e, 'rag.py:intent_embed')

        if os.path.exists(db_path):
            try:
                conn = connect_sqlite(db_path)
                c = conn.cursor()

                RRF_K = 60.0
                scored_paths: Dict[str, float] = {}

                # 1. FTS5 Robertson BM25 Lexical Rank
                if query_str.strip():
                    c.execute('SELECT path FROM pages_fts WHERE pages_fts MATCH ? ORDER BY rank LIMIT 15', (query_str,))
                    for rank_idx, (path,) in enumerate(c.fetchall(), start=1):
                        scored_paths[path] = scored_paths.get(path, 0.0) + (1.0 / (RRF_K + rank_idx))

                # 2. Dense Vector Rank via Canonical Float32 BLOB (archival_vectors)
                if query_embedding:
                    try:
                        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='archival_vectors'")
                        if c.fetchone():
                            c.execute("SELECT id, embedding, created_at FROM archival_vectors WHERE embedding IS NOT NULL")
                            vec_hits = []
                            for path, blob, created_at in c.fetchall():
                                if not blob:
                                    continue
                                try:
                                    emb = unpack_vector(blob)
                                    sim = compute_cosine(query_embedding, emb)
                                    if sim > 0.35:
                                        decayed_sim = calculate_retrieval_score(sim, float(created_at or time.time()))
                                        vec_hits.append((path, decayed_sim))
                                except Exception as _ve:
                                    _log_telemetry(_ve, "rag.py:rrf_vec")
                            vec_hits.sort(key=lambda x: x[1], reverse=True)
                            for rank_idx, (path, _) in enumerate(vec_hits[:15], start=1):
                                scored_paths[path] = scored_paths.get(path, 0.0) + (1.2 / (RRF_K + rank_idx))
                    except Exception as _e:
                        _log_telemetry(_e, "rag.py:archival_vectors")

                # 3. Memory Hygiene Importance & Access Frequency Boost
                if scored_paths:
                    placeholders = ",".join("?" for _ in scored_paths)
                    c.execute(
                        f"SELECT path, COALESCE(access_count, 0), COALESCE(importance, 1.0) FROM pages WHERE path IN ({placeholders})",
                        list(scored_paths.keys())
                    )
                    for path, acc_cnt, imp in c.fetchall():
                        usage_boost = (0.3 * math.log1p(max(0, int(acc_cnt))) + 0.2 * float(imp)) / RRF_K
                        scored_paths[path] += usage_boost

                # Resolve final top 3 paths
                if temp_nb and getattr(temp_nb, 'use_cross_encoder', False):
                    try:
                        from commands.brain import cross_encoder_rerank
                        candidate_pool = sorted(scored_paths.keys(), key=lambda k: scored_paths[k], reverse=True)[:5]
                        final_paths = cross_encoder_rerank(intent, candidate_pool, nanobrain=temp_nb)[:3]
                        print(f"  [CROSS-ENCODER] Re-ranked {len(final_paths)} candidate paths via TitanBrain profile.")
                    except Exception:
                        final_paths = sorted(scored_paths.keys(), key=lambda k: scored_paths[k], reverse=True)[:3]
                else:
                    final_paths = sorted(scored_paths.keys(), key=lambda k: scored_paths[k], reverse=True)[:3]

                retrieval_chunks = []
                fts_content_map: Dict[str, str] = {}
                for path in final_paths:
                    try:
                        cand_path = path if os.path.isabs(path) else os.path.join(workspace_dir, path)
                        if os.path.isfile(cand_path):
                            with open(cand_path, "r", encoding="utf-8", errors="replace") as retrieved_file:
                                retrieval_chunks.append(retrieved_file.read(12000))
                        else:
                            c.execute("SELECT content FROM pages_fts WHERE path = ? LIMIT 1", (path,))
                            row_c = c.fetchone()
                            body_txt = row_c[0] if row_c and row_c[0] else path
                            fts_content_map[path] = body_txt
                            retrieval_chunks.append(body_txt[:12000])
                    except OSError as _e:
                        _log_telemetry(_e, f"rag.py:retrieval:{path}")
                try:
                    with RAGDiagnosticJudge(db_path) as judge:
                        judge.evaluate_retrieval(intent, retrieval_chunks)
                except Exception as _re:
                    _log_telemetry(_re, "rag.py:evaluate_retrieval")

                for path in final_paths:
                    cand_path = path if os.path.isabs(path) else os.path.join(workspace_dir, path)
                    if os.path.isfile(cand_path):
                        if "archive/" in cand_path.replace("\\", "/").lower():
                            normalized_path = cand_path.replace("\\", "/")
                            parts = normalized_path.split("archive/")
                            rel_path = parts[1] if len(parts) > 1 else os.path.basename(cand_path)
                            print(f"  [AMNESIA RECALL] JIT Read-Only Access to asset '{rel_path}' from archive!")
                        rules.append(cand_path)
                    else:
                        snip = fts_content_map.get(path, path).replace("\n", " ").strip()
                        print(f"  [MEMORY RECALL] ({path}) Snippet: {snip[:160]}...")

                    try:
                        c.execute("UPDATE pages SET access_count = IFNULL(access_count, 0) + 1, last_accessed = datetime('now') WHERE path = ?", (path,))
                        conn.commit()
                    except Exception as _e:
                        _log_telemetry(_e, 'rag.py:update_access_count')

                # --- 1-Hop Graph Traversal ---
                try:
                    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='relations'")
                    has_relations = bool(c.fetchone())
                    if has_relations and final_paths:
                        for seed_path in final_paths:
                            seed_clean = seed_path.replace("\\", "/")
                            seed_base = os.path.basename(seed_path)
                            seed_stem = os.path.splitext(seed_base)[0]

                            c.execute('''
                                SELECT subject_id, predicate, object_id, weight 
                                FROM relations 
                                WHERE subject_id = ? OR subject_id = ? OR subject_id LIKE ? OR source_path = ?
                                LIMIT 8
                            ''', (seed_path, seed_clean, f"%{seed_base}", seed_path))
                            for src, rel, tgt, conf in c.fetchall():
                                hop_triplets.append((os.path.basename(src), rel, tgt))
                                _resolve_neighbor_target(c, tgt, workspace_dir, neighbor_files)

                            c.execute('''
                                SELECT subject_id, predicate, object_id, weight 
                                FROM relations 
                                WHERE object_id = ? OR object_id = ? OR object_id = ? OR object_id LIKE ?
                                LIMIT 8
                            ''', (seed_path, seed_clean, seed_stem, f"%{seed_base}"))
                            for src, rel, tgt, conf in c.fetchall():
                                hop_triplets.append((os.path.basename(src), rel, os.path.basename(tgt)))
                                _resolve_neighbor_target(c, src, workspace_dir, neighbor_files)

                            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entities'")
                            if c.fetchone():
                                c.execute('''
                                    SELECT name FROM entities 
                                    WHERE source_path = ? OR source_path = ? OR source_path LIKE ?
                                    LIMIT 5
                                ''', (seed_path, seed_clean, f"%{seed_base}"))
                                for (ent_name,) in c.fetchall():
                                    c.execute('''
                                        SELECT subject_id, predicate, object_id FROM relations 
                                        WHERE subject_id = ? OR object_id = ?
                                        LIMIT 3
                                    ''', (ent_name, ent_name))
                                    for s_id, rel, t_id in c.fetchall():
                                        hop_triplets.append((s_id, rel, t_id))
                                        if s_id != ent_name:
                                            _resolve_neighbor_target(c, s_id, workspace_dir, neighbor_files)
                                        if t_id != ent_name:
                                            _resolve_neighbor_target(c, t_id, workspace_dir, neighbor_files)
                    elif final_paths:
                        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='edges'")
                        if c.fetchone():
                            for seed_path in final_paths:
                                seed_clean = seed_path.replace("\\", "/")
                                seed_base = os.path.basename(seed_path)
                                seed_stem = os.path.splitext(seed_base)[0]

                                c.execute('''
                                    SELECT source_id, relation, target_id, confidence 
                                    FROM edges 
                                    WHERE source_id = ? OR source_id = ? OR source_id LIKE ?
                                    LIMIT 8
                                ''', (seed_path, seed_clean, f"%{seed_base}"))
                                for src, rel, tgt, conf in c.fetchall():
                                    hop_triplets.append((os.path.basename(src), rel, tgt))
                                    _resolve_neighbor_target(c, tgt, workspace_dir, neighbor_files)

                                c.execute('''
                                    SELECT source_id, relation, target_id, confidence 
                                    FROM edges 
                                    WHERE target_id = ? OR target_id = ? OR target_id = ? OR target_id LIKE ?
                                    LIMIT 8
                                ''', (seed_path, seed_clean, seed_stem, f"%{seed_base}"))
                                for src, rel, tgt, conf in c.fetchall():
                                    hop_triplets.append((os.path.basename(src), rel, os.path.basename(tgt)))
                                    _resolve_neighbor_target(c, src, workspace_dir, neighbor_files)

                                c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'")
                                if c.fetchone():
                                    c.execute('''
                                        SELECT id FROM nodes 
                                        WHERE source_path = ? OR source_path = ? OR source_path LIKE ?
                                        LIMIT 5
                                    ''', (seed_path, seed_clean, f"%{seed_base}"))
                                    for (node_id,) in c.fetchall():
                                        c.execute('''
                                            SELECT source_id, relation, target_id FROM edges 
                                            WHERE source_id = ? OR target_id = ?
                                            LIMIT 3
                                        ''', (node_id, node_id))
                                        for s_id, rel, t_id in c.fetchall():
                                            hop_triplets.append((s_id, rel, t_id))
                                            if s_id != node_id:
                                                _resolve_neighbor_target(c, s_id, workspace_dir, neighbor_files)
                                            if t_id != node_id:
                                                _resolve_neighbor_target(c, t_id, workspace_dir, neighbor_files)

                        for n_path in neighbor_files:
                            if n_path not in rules:
                                rules.append(n_path)
                                print(f"  [GRAPH-HOP] 1-Hop Traversal pulled neighbor asset: '{os.path.relpath(n_path, workspace_dir)}'")
                except Exception as ge:
                    print(f"  [WARNING] Graph traversal degraded: {ge}")

                conn.close()

                # Telemetry: Record view events for pulled skills
                for r_path in rules:
                    norm = r_path.replace("\\", "/")
                    if "skills/" in norm:
                        try:
                            parts = norm.split("skills/")[1].split("/")
                            if parts:
                                sk_name = parts[0]
                                from core.harness.engine import HarnessEngine
                                HarnessEngine.record_skill_event(sk_name, "view")
                        except Exception as _ste:
                            _log_telemetry(_ste, "rag:skill_telemetry")

                cache_data[query_str] = rules
                if len(cache_data) > 50:
                    keys = list(cache_data.keys())
                    for k in keys[:-50]:
                        del cache_data[k]
                atomic_write_text(cache_path, json.dumps(cache_data, indent=2))
            except Exception as e:
                print(f"  [ERROR] Graph Query Failed: {e}")

    wiki_nodes = search_files(orion_dir, keywords)
    saas_nodes = search_files(context_dir, keywords)

    print("\n" + "="*60)
    if delta:
        print(" DELTA CONTEXT PACKET (GRAPH-HARMONIZED) - Continuous RAG")
    else:
        print(" UNIFIED CONTEXT PACKET (GRAPH-HARMONIZED)")
    print("="*60)

    nb = None
    if not delta:
        rules_index_path = os.path.join(agents_dir, "rules", "RULES_INDEX.md")
        if os.path.exists(rules_index_path):
            with open(rules_index_path, "r", encoding="utf-8") as f:
                rules_content = f.read()

            print("\n## Standard Operating Procedures (Micro-Rules)")
            matches = []
            try:
                from commands.brain import NanoBrain
                temp_nb = NanoBrain()
                if temp_nb.ping():
                    nb = temp_nb
            except Exception as _e:
                _log_telemetry(_e, 'rag.py:rules_nanobrain')

            for line in rules_content.split('\n'):
                if not line.strip() or line.startswith('#'):
                    continue
                line_lower = line.lower()
                if "global" in line_lower:
                    matches.append(line.strip())
                    continue
                is_match = any(kw in line_lower for kw in keywords) if keywords else False
                if is_match:
                    matches.append(line.strip())

            if matches:
                for m in matches[:5]:
                    print(f"  {m}")
            else:
                print("  No specific standards matched. Proceeding with global baseline.")

    if (skills or rules) and not delta:
        print("\n## Motor Cortex (Rules & Skills)")
        for r in (rules + skills)[:5]:
            rel_path = os.path.relpath(r, workspace_dir)
            is_hypothesis = False
            try:
                if r.endswith('.md') and os.path.exists(r):
                    with open(r, "r", encoding="utf-8", errors="ignore") as f_head:
                        header = f_head.read(600)
                        if "epistemic_status: HYPOTHESIS_DRAFT" in header or "needs_human_review: true" in header:
                            is_hypothesis = True
            except Exception as _e_hdr:
                _log_telemetry(_e_hdr, 'rag.py:sync:epistemic_check')
            if is_hypothesis:
                print(f"- [UNVERIFIED HYPOTHESIS - REQUIRES HUMAN REVIEW]: {rel_path}")
            else:
                print(f"- [Mandatory Execution Protocol]: {rel_path}")

    if hop_triplets and not delta:
        print("\n## 🕸️ Knowledge Graph Relations (1-Hop Traversal)")
        seen_triplets = set()
        for src, rel, tgt in hop_triplets:
            key = (src, rel, tgt)
            if key not in seen_triplets:
                seen_triplets.add(key)
                print(f"- ({src}) -[{rel}]-> ({tgt})")
                if len(seen_triplets) >= 6:
                    break

    if neighbor_files and not delta:
        print("\n## 🔗 Graph-Traversed Neighbor Assets (1-Hop Expanded Context)")
        for n in neighbor_files[:3]:
            rel_path = os.path.relpath(n, workspace_dir)
            print(f"- [Connected Asset]: {rel_path}")

    # --- Dual-Level GraphRAG: Louvain Community Context ---
    db_path = os.path.join(orion_dir, 'orion.db')
    if os.path.exists(db_path) and not delta:
        try:
            from core.orion_graph import OrionGraphStore
            graph_store = OrionGraphStore(db_path=db_path)
            stats = graph_store.get_stats()
            if stats["communities_count"] == 0 and stats["entities_count"] == 0:
                graph_store.sync_from_legacy_tables()

            rag_res = graph_store.dual_level_query(intent, top_k_communities=2, top_k_entities=3)
            macro_comms = rag_res.get("macro_communities", [])
            if macro_comms:
                print("\n## 🌌 Macro Community Context (Louvain Modularity Cluster)")
                for comm in macro_comms:
                    print(f"- [Cluster #{comm['cluster_id']} Level {comm['level']} ({comm['dominant_type']})]: {comm['summary']}")
            graph_store.close()
        except Exception as _e:
            _log_telemetry(_e, 'rag.py:dual_level_graph_rag')

    # --- Active Graph Contradictions Check ---
    if os.path.exists(db_path) and not delta:
        try:
            conn_c = connect_sqlite(db_path)
            c_cur = conn_c.cursor()
            c_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contradictions'")
            if c_cur.fetchone():
                c_cur.execute("SELECT edge_a_source, edge_a_relation, edge_a_target, edge_b_relation, edge_b_target FROM contradictions WHERE resolution = 'unresolved' LIMIT 3")
                unresolved = c_cur.fetchall()
                if unresolved:
                    print("\n## ⚠️ Active Graph Contradictions (Unresolved Collisions)")
                    for a_src, a_rel, a_tgt, b_rel, b_tgt in unresolved:
                        print(f"- [Collision Alert]: ({os.path.basename(a_src)}) -> '{a_rel} {a_tgt}' vs '{b_rel} {b_tgt}'")
            conn_c.close()
        except Exception as _e:
            _log_telemetry(_e, 'rag.py:contradictions')

    if wiki_nodes:
        print("\n## Hippocampus (Orion Knowledge)")
        for w in wiki_nodes:
            rel_path = os.path.relpath(w, workspace_dir)
            print(f"- [Concept Node]: {rel_path}")

    # --- Orion Manifest RAG injection ---
    manifest_path = os.path.join(orion_dir, "_manifest.json")
    wiki_hits = []
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                for layer, entries in manifest.get("layers", {}).items():
                    for entry in entries:
                        filepath = entry.get("filepath", "").lower()
                        if any(kw in filepath for kw in keywords):
                            wiki_hits.append(os.path.basename(entry.get("orion_file", "")).replace(".md", ""))
        except Exception as _e:
            _log_telemetry(_e, 'rag.py:manifest_rag')

    if wiki_hits:
        print("\n## Deep RAG (Orion Graph Hits)")
        print(f"  Found potential nodes: {', '.join(wiki_hits[:3])}")
        top_node = wiki_hits[0]
        print(f"  [AUTO-RAG]: Resolving primary node '{top_node}' automatically...\n")
        try:
            from commands.brain import resolve_wiki
            resolve_wiki(top_node)
        except Exception as e:
            print(f"  [ERROR] Could not execute Auto-RAG: {e}")

    if nb and nb.ping(capability="LLM"):
        print("\n## [NanoBrain] NanoBrain (Ollama) is ONLINE (LLM Active)")
        print("  [CAPABILITY]: You can use `python .agents/scripts/orion.py brain nanobrain vibe_check <text>` for instant UI aesthetic validation without consuming major tokens.")
    else:
        print("\n## [NanoBrain] [WARNING] NanoBrain LLM features disabled — (Status OFF or EMBED)")

    # --- Working Memory (Holographic Handoff) ---
    handoff_path = os.path.join(orion_dir, "working", "handoff.md")
    if os.path.exists(handoff_path):
        print("\n## Working Memory (Session Handoff)")
        try:
            with open(handoff_path, "r", encoding="utf-8") as f:
                handoff_content = f.read()
            print("  [ACTIVE HANDOFF DETECTED]:")
            for line in handoff_content.splitlines():
                print(f"    {line}")

            episodic_dir = os.path.join(orion_dir, "episodic")
            if not os.path.exists(episodic_dir):
                os.makedirs(episodic_dir)

            mtime = os.path.getmtime(handoff_path)
            age_hours = (time.time() - mtime) / 3600

            archive_marker = os.path.join(episodic_dir, ".last_archived_mtime")
            last_mtime = 0
            if os.path.exists(archive_marker):
                try:
                    with open(archive_marker, "r", encoding="utf-8") as mf:
                        last_mtime = float(mf.read().strip())
                except Exception as _e:
                    _log_telemetry(_e, 'rag.py:archive_marker')

            if mtime > last_mtime:
                stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                if age_hours > 48:
                    print(f"  [WARNING] Handoff is {age_hours:.0f}h old. May be stale. Archiving with STALE prefix.")
                    shutil.copy2(handoff_path, os.path.join(episodic_dir, f"STALE_handoff_{stamp}.md"))
                else:
                    shutil.copy2(handoff_path, os.path.join(episodic_dir, f"handoff_{stamp}.md"))
                    print("  [INFO] Handoff backed up to episodic memory.")

                atomic_write_text(archive_marker, str(mtime))
        except Exception as e:
            print(f"  [ERROR] Failed to process working memory: {e}")

    try:
        from core.memory import MultiLayerMemoryManager
        ml_mgr = MultiLayerMemoryManager()
        try:
            facts = ml_mgr.get_facts()
            if facts:
                print("\n## 🧠 Semantic Memory Facts (Tier 1)")
                for k, v in list(facts.items())[:5]:
                    print(f"- [{k}]: {v}")
        finally:
            ml_mgr.close()
    except Exception as _e:
        _log_telemetry(_e, 'rag.py:sync_facts')

    if saas_nodes:
        print("\n## Working Memory (SaaS State)")
        for s in saas_nodes:
            rel_path = os.path.relpath(s, workspace_dir)
            print(f"- [Active State]: {rel_path}")
            if get_ast_block(s, 'saas-state'):
                print("  [DATA-NODE]: Extracted semantic state successfully.")

    if not (skills or rules or wiki_nodes or saas_nodes):
        print("\n[WARNING]: No contextual nodes found for these tokens. AI must rely on zero-shot reasoning.")

    try:
        from commands.brain import record_db_telemetry
        record_db_telemetry("brain_sync", exit_code=0, context_load=len(rules + skills))
    except Exception as _e:
        _log_telemetry(_e, 'rag.py:telemetry')

    print("\n---\n[DIRECTIVE] Read the above files with `view_file` BEFORE modifying code. Adhere to rules. Proceed.")


def page_context(keywords: List[str]) -> None:
    """Ephemeral Lessword compilation of relevant rules/skills into .orion/page.md."""
    agents_dir = str(get_agents_dir())
    workspace_dir = os.path.dirname(agents_dir)
    orion_dir = os.path.join(workspace_dir, ".orion")
    if not os.path.exists(orion_dir):
        os.makedirs(orion_dir)

    page_path = os.path.join(orion_dir, "page.md")
    targets = [os.path.join(agents_dir, "rules"), os.path.join(agents_dir, "skills")]
    relevant_chunks = []

    for target in targets:
        for root, dirs, files in os.walk(target):
            for file in files:
                if not file.endswith(".md"):
                    continue
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    chunks = re.split(r'\n(?=#+ )', content)
                    try:
                        for chunk in chunks:
                            chunk_lower = chunk.lower()
                            if any(kw.lower() in chunk_lower for kw in keywords):
                                header_match = re.match(r'(#+ .*?)\n', chunk)
                                header = header_match.group(1) if header_match else f"Excerpt from {file}"

                                try:
                                    from commands.brain import parse_markdown_to_dict
                                    chunk_dict = parse_markdown_to_dict(chunk.strip())
                                    dense_json = json.dumps(chunk_dict, indent=2)
                                    relevant_chunks.append(f"### Source: {file} | {header}\n```json\n{dense_json}\n```\n")
                                except Exception:
                                    relevant_chunks.append(f"### Source: {file} | {header}\n{chunk.strip()}\n")
                    except Exception as e:
                        for chunk in chunks:
                            chunk_lower = chunk.lower()
                            if any(kw.lower() in chunk_lower for kw in keywords):
                                header_match = re.match(r'(#+ .*?)\n', chunk)
                                header = header_match.group(1) if header_match else f"Excerpt from {file}"
                                relevant_chunks.append(f"### Source: {file} | {header}\n{chunk.strip()}\n")
                except Exception as _e:
                    _log_telemetry(_e, f'rag.py:page_context:{filepath}')

    atomic_write_text(page_path, "# Ephemeral Pager Context\n\n" + "\n---\n".join(relevant_chunks))
    print(f"Paging complete. {len(relevant_chunks)} chunks swapped into {os.path.relpath(page_path, workspace_dir)}")


def rag_main(argv=None) -> int:
    """CLI dispatcher for RAG and context operations."""
    if argv is None:
        argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help", "help"):
        print("Usage: python rag.py <sync|diagnostics|page> [args...]")
        return 0
    cmd = argv[0]
    sub_args = argv[1:]
    if cmd in ("sync", "retrieve"):
        intent = " ".join(sub_args) if sub_args else "default intent"
        sync(intent)
        return 0
    elif cmd in ("diagnostics", "eval"):
        return diagnostics_main(sub_args)
    elif cmd == "page":
        if not sub_args:
            print("Provide keywords for context paging.")
            return 1
        page_context(sub_args)
        return 0
    else:
        print(f"Unknown RAG command: {cmd}")
        return 1


if __name__ == "__main__":
    sys.exit(rag_main(sys.argv[1:]))
