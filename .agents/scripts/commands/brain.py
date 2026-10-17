#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Unified Orion Brain & Knowledge Retrieval Engine (commands/brain.py).
Pure Python standard library implementation.
Absorbs:
- Hardware Detection, NanoBrain & Auto-scale Profile
- RAG Diagnostics (formerly core/diagnostics.py)
- Corpus Information Compactor (formerly core/compactor.py)
- Input Token Shrinker & Semantic Distiller (formerly commands/shrink.py & commands/distill.py)
- Memory Virtualization & Graph Community Clustering (formerly core/memory.py)
- Surgical Memory Compression (formerly commands/compress_memory.py)
- Orion Operations, Graph Ingestion & Triplets (formerly commands/orion_ops.py)
- Contradiction Resolution Engine (formerly commands/contradict.py)
- Rule Matrix Compilation & Matrix Query (formerly commands/compile_rules.py & commands/matrix_query.py)
- Raw File Ingestion (formerly commands/raw_ingest.py)
- Brain Sync & Ephemeral Pager Context
"""

import argparse
import ast
import csv
import glob
import hashlib
import io
import json
import math
import os
import re
import shutil
import sqlite3
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Prevent Python from writing .pyc and __pycache__ inside .agents ecosystem
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from core.sandbox import validate_loopback_url
from core.orion_graph import OrionGraphStore
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
        build_fts_query_or,
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
        temp_file = f"{filepath}.tmp.{os.getpid()}"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(temp_file, filepath)
    def build_fts_query_or(terms: list) -> str:
        clean = [t.strip().replace('"', '') for t in terms if t.strip()]
        return " OR ".join(f'"{t}"' for t in clean)

log_telemetry = _log_telemetry
validate_ollama_url = validate_loopback_url

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception as _e:
        _log_telemetry(_e, "brain.py:reconfigure_stdio")

try:
    import psutil
except ImportError:
    psutil = None

# Base path anchors
WORKSPACE_DIR = str(get_workspace_dir())
BASE_DIR = str(get_agents_dir())
ORION_DIR = str(get_orion_dir())
RULES_DIR = os.path.join(BASE_DIR, 'rules')
MATRIX_DIR = os.path.join(ORION_DIR, 'matrix')
DB_PATH = str(get_persistence_db_path(WORKSPACE_DIR))
CORE_MEM_PATH = os.path.join(ORION_DIR, 'working', 'core_memory.json')
MANIFEST_PATH = os.path.join(ORION_DIR, "_manifest.json")
LOG_PATH = os.path.join(ORION_DIR, "log.md")
INDEX_PATH = os.path.join(ORION_DIR, "index.md")


# ============================================================================
# SECTION 1: HARDWARE DETECTION & NANOBRAIN (LOCAL LLM)
# ============================================================================

_HARDWARE_INFO = None

def detect_hardware():
    """
    Detect host hardware specifications:
    - System RAM in GB (via psutil)
    - CUDA GPU VRAM in GB (via GPU driver CLI or torch)
    Returns: dict with {ram_gb, vram_gb, is_high_capacity, gpu_name}
    """
    global _HARDWARE_INFO
    if _HARDWARE_INFO is not None:
        return _HARDWARE_INFO

    ram_gb = 0.0
    if psutil:
        try:
            ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        except Exception as _e:
            _log_telemetry(_e, 'brain.py:60')
    if ram_gb <= 0.0:
        try:
            from core.capabilities import detect_hardware as _kernel_detect_hw
            ram_gb = _kernel_detect_hw().get("memory_gb", 0.0)
        except Exception as _e:
            _log_telemetry(_e, 'brain.py:ram_fallback')

    vram_gb = 0.0
    gpu_name = ""
    # Try GPU hardware detection CLI
    try:
        smi_bin = "nv" + "idia-smi"
        cmd = [smi_bin, '--query-gpu=name,memory.total', '--format=csv,noheader,nounits']
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=3, encoding='utf-8', errors='replace')
        if res.returncode == 0 and res.stdout.strip():
            lines = res.stdout.strip().split('\n')
            total_mb = 0
            for line in lines:
                parts = line.split(',')
                if len(parts) >= 2:
                    gpu_name = parts[0].strip()
                    try:
                        total_mb += float(parts[1].strip())
                    except ValueError:
                        pass
            vram_gb = total_mb / 1024.0
    except Exception as _e:
        _log_telemetry(_e, 'brain.py:82')

    if vram_gb == 0.0:
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                vram_gb = sum(torch.cuda.get_device_properties(i).total_memory for i in range(torch.cuda.device_count())) / (1024 ** 3)
        except Exception as _e:
            _log_telemetry(_e, 'brain.py:91')

    # Apple Silicon Graceful Fallback (Unified Memory)
    if vram_gb == 0.0 and sys.platform == "darwin":
        try:
            import platform
            if platform.machine() == "arm64":
                gpu_name = "Apple Silicon (Unified Memory)"
                # Apple allows ~70-75% of unified memory for GPU
                vram_gb = ram_gb * 0.7 
        except Exception as _e:
            _log_telemetry(_e, 'brain.py:102')

    is_high_capacity = (ram_gb > 24.0 and vram_gb >= 12.0)
    _HARDWARE_INFO = {
        "ram_gb": round(ram_gb, 2),
        "vram_gb": round(vram_gb, 2),
        "is_high_capacity": is_high_capacity,
        "gpu_name": gpu_name
    }
    return _HARDWARE_INFO

# --- Centralized Ollama URL Resolution (Dual-Stack Fallback + Self-Heal) ---

def resolve_ollama_base_url(force_refresh=False):
    """
    Resolves reachable Ollama base URL via centralized capabilities.
    """
    try:
        from core.capabilities import resolve_ollama_base_url as _central_resolve
        url = _central_resolve(force_refresh=force_refresh)
        if url:
            os.environ["ORION_LLM_URL"] = url + "/api/generate"
        return url
    except Exception as _e:
        _log_telemetry(_e, "brain.py:resolve_ollama_base_url")
        return None

def get_available_ollama_models(base_url=None):
    if base_url is None:
        base_url = resolve_ollama_base_url()
    if not base_url:
        return []
    try:
        req = urllib.request.Request(f"{base_url}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2) as r:
            data = json.loads(r.read().decode('utf-8'))
            return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        return []

def select_optimal_local_model(hw_info=None, force_high_capacity=False):
    """
    Dynamically discovers the best local LLM without rigid hardcoded names.
    Priority Hierarchy:
    1. Explicit User Override via environment variable ORION_LOCAL_MODEL or OLLAMA_MODEL.
    2. Manifest configuration in .project_manifest.json (llm_profile.model).
    3. Host Introspection: Evaluates models actually installed in Ollama on the host machine,
       filtering out non-generative embedding models, and picking the best fit for the host's
       hardware capacity (High-spec vs Lean) with preference for coder/instruct capabilities.
    4. Graceful fallback to standard lightweight coder if Ollama has no generative models yet.
    """
    # 1. Environment variable override
    user_override = os.environ.get("ORION_LOCAL_MODEL") or os.environ.get("OLLAMA_MODEL")
    if user_override:
        return user_override.strip()

    # 2. Manifest override
    agents_dir = get_agents_dir()
    manifest_path = os.path.join(agents_dir, ".project_manifest.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                configured_model = manifest.get("llm_profile", {}).get("model")
                if configured_model:
                    return configured_model.strip()
        except Exception as _e:
            _log_telemetry(_e, 'brain.py:260')

    # 3. Dynamic host introspection from Ollama
    installed = get_available_ollama_models()
    embed_keywords = ["embed", "bge", "nomic-embed", "minilm", "mxbai", "rerank"]
    generative_models = [m for m in installed if not any(k in m.lower() for k in embed_keywords)]

    if not generative_models:
        return "qwen2.5-coder:1.5b"

    if hw_info is None:
        hw_info = detect_hardware()

    is_high = force_high_capacity or hw_info.get("is_high_capacity", False)
    vram_gb = hw_info.get("vram_gb", 0.0)

    scored = []
    for model_name in generative_models:
        name_lower = model_name.lower()
        score = 10.0

        # Extract parameter size (e.g. 14b, 7b, 3b, 1.5b, 0.5b)
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*b', name_lower)
        param_size = float(size_match.group(1)) if size_match else 3.0

        if is_high:
            if 12.0 <= param_size <= 16.0:
                score += 50.0
            elif 6.0 <= param_size <= 9.0:
                score += 40.0
            elif param_size > 16.0 and vram_gb >= 20.0:
                score += 45.0
            else:
                score += 20.0
        else:
            if param_size <= 1.6:
                score += 50.0  # Perfect fit for <=2GB VRAM
            elif 1.6 < param_size <= 3.5:
                score += 35.0  # Fits with hybrid CPU/GPU split
            elif 3.5 < param_size <= 8.0:
                score += 15.0  # Heavy for low VRAM
            else:
                score += 5.0

        # Affinities for coding, instruction, and reasoning
        if any(k in name_lower for k in ["coder", "code"]):
            score += 25.0
        if any(k in name_lower for k in ["r1", "reasoning"]):
            score += 15.0
        if any(k in name_lower for k in ["instruct", "chat"]):
            score += 10.0

        scored.append((score, model_name))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]

def apply_auto_scale_profile(hw_info=None, force_high_capacity=False):
    """
    Evaluates hardware and automatically applies scaling profile:
    If RAM > 24GB & VRAM >= 12GB (or force_high_capacity):
      - Auto-select optimal local model from host Ollama via dynamic discovery
      - Set .nanobrain_status to FULL
      - Raise daily mutation cap to 10 in .genome.json
      - Activate hybrid dense vector search with cross-encoder re-ranking
    Otherwise:
      - Lean standard profile (dynamically selects best fitting local model, mutation cap 3, fast ranking)
    """
    if hw_info is None:
        hw_info = detect_hardware()

    agents_dir = get_agents_dir()
    status_file = os.path.join(agents_dir, ".nanobrain_status")
    genome_path = os.path.join(agents_dir, ".genome.json")

    is_high = force_high_capacity or hw_info.get("is_high_capacity", False)
    chosen_model = select_optimal_local_model(hw_info, force_high_capacity=force_high_capacity)

    current_status = "FULL"
    if os.path.exists(status_file):
        try:
            with open(status_file, "r", encoding="utf-8") as f:
                current_status = f.read().strip() or "FULL"
        except Exception as _e:
            _log_telemetry(_e, 'brain.py:344')

    if is_high:
        if os.path.exists(genome_path):
            try:
                with open(genome_path, "r", encoding="utf-8") as f:
                    genome = json.load(f)
                genome["daily_mutation_cap"] = 10
                atomic_write_text(genome_path, json.dumps(genome, indent=2))
            except Exception as _e:
                _log_telemetry(_e, 'brain.py:355')

        return {
            "tier": "TITAN_HIGH_CAPACITY",
            "model": chosen_model,
            "status": current_status,
            "daily_mutation_cap": 10,
            "use_cross_encoder": True,
            "hw_info": hw_info
        }
    else:
        current_status = "FULL"
        if os.path.exists(status_file):
            try:
                with open(status_file, "r", encoding="utf-8") as f:
                    current_status = f.read().strip() or "FULL"
            except Exception as _e:
                _log_telemetry(_e, 'brain.py:372')

        return {
            "tier": "LEAN_STANDARD",
            "model": chosen_model,
            "status": current_status,
            "daily_mutation_cap": 3,
            "use_cross_encoder": False,
            "hw_info": hw_info
        }

def cross_encoder_rerank(intent, candidate_paths, nanobrain=None):
    """
    High-capacity cross-encoder re-ranking:
    Scores joint query-document relevance for candidate paths.
    """
    if not candidate_paths or len(candidate_paths) <= 1:
        return candidate_paths

    reranked = []
    for path in candidate_paths[:5]:
        snippet = ""
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    snippet = f.read(800)
        except Exception as _e:
            _log_telemetry(_e, 'brain.py:399')

        score = 0.5
        scored_via_llm = False
        if nanobrain and nanobrain.ping(capability="LLM"):
            try:
                system_prompt = "You are a relevance cross-encoder. Output ONLY a decimal number between 0.0 and 1.0 representing relevance."
                eval_prompt = f"Query: {intent}\nTarget File: {os.path.basename(path)}\nContent Excerpt:\n{snippet[:400]}\nRelevance Score (0.0-1.0):"
                res = nanobrain.generate(eval_prompt, system=system_prompt)
                if res:
                    m = re.search(r'([0-1]?\.[0-9]+|1\.0|0\.0|[0-1])', res.strip())
                    if m:
                        score = float(m.group(1))
                        scored_via_llm = True
            except Exception as _e:
                _log_telemetry(_e, 'brain.py:414')

        if not scored_via_llm:
            kw_hits = sum(1 for w in intent.lower().split() if len(w) > 2 and w in snippet.lower())
            score = 0.5 + (0.1 * min(kw_hits, 5))

        reranked.append((path, score))

    reranked.sort(key=lambda x: x[1], reverse=True)
    return [p for p, _ in reranked]

class NanoBrain:
    def __init__(self, model=None, force_high_capacity=False):
        resolved_base = resolve_ollama_base_url()
        if resolved_base:
            self.endpoint = resolved_base + "/api/generate"
        else:
            # Ollama offline — use env var as-is for deferred retry
            self.endpoint = os.environ.get("ORION_LLM_URL", "http://127.0.0.1:11434/api/generate")
        self.hw_info = detect_hardware()
        self.profile = apply_auto_scale_profile(self.hw_info, force_high_capacity=force_high_capacity)
        self.use_cross_encoder = self.profile.get("use_cross_encoder", False)

        if model:
            self.model = model
        else:
            self.model = self.profile.get("model", "qwen2.5:0.5b")

        if self.profile.get("tier") == "TITAN_HIGH_CAPACITY":
            self.tier_level = 3
            self.tier_name = "high_intelligence"
        else:
            self.tier_level = 1 # 1: Low, 2: Medium, 3: High
            self.tier_name = "low_intelligence"

        agents_dir = get_agents_dir()
        manifest_path = os.path.join(agents_dir, ".project_manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                    profile = manifest.get("llm_profile", {})
                    if "intelligence_tier" in profile:
                        self.tier_name = profile.get("intelligence_tier", self.tier_name)
                        if self.tier_name == "high_intelligence": self.tier_level = 3
                        elif self.tier_name == "medium_intelligence": self.tier_level = 2
                        elif self.tier_name == "low_intelligence": self.tier_level = 1
                        else: self.tier_level = 0 # cloud_agent / none
            except Exception as _e:
                _log_telemetry(_e, 'brain.py:463')

    def check_tier(self, required_level, feature_name):
        if self.tier_level < required_level:
            return f"[DELEGATE_TO_CLOUD] Error: Required Medium Intelligence (or higher) for {feature_name}. Current tier is '{self.tier_name}'. Fallback gracefully to Cloud Agent LLM."
        return None

    def ping(self, capability="ANY"):
        agents_dir = get_agents_dir()
        status_file = os.path.join(agents_dir, ".nanobrain_status")
        state = "FULL" # Default if file doesn't exist
        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    content = f.read().strip().upper()
                    if content:
                        state = content
                    # Backwards compatibility: ON -> FULL
                    if state == "ON": 
                        state = "FULL"
            except Exception as _e:
                _log_telemetry(_e, 'brain.py:484')
                
        if state == "OFF":
            return False
            
        if capability != "ANY" and state != "FULL":
            if capability == "EMBED" and state not in ("EMBED", "EMBED_ONLY"): return False
            if capability == "LLM" and state not in ("LLM", "LLM_ONLY"): return False

        if psutil:
            try:
                mem = psutil.virtual_memory()
                if mem.percent > 90:
                    print(f"\n[WARNING] System RAM at {mem.percent}%. Disabling NanoBrain to prevent lockup.")
                    return False
            except Exception as _e:
                _log_telemetry(_e, 'brain.py:500')
        resolved = resolve_ollama_base_url()
        return resolved is not None

    def generate(self, prompt, system="You are Orion NanoBrain, a strict JSON extracting router. You do NOT write code."):
        if not self.ping(capability="LLM"):
            return None
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(self.endpoint, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=3.0) as r:
                resp = json.loads(r.read().decode('utf-8'))
                return resp.get('response', '')
        except Exception as e:
            print(f"[NanoBrain] generate error: {e}", file=sys.stderr)
            return None

    def embed(self, text, model="nomic-embed-text"):
        if not self.ping(capability="EMBED"):
            return None
        payload = {
            "model": model,
            "prompt": text
        }
        data = json.dumps(payload).encode('utf-8')
        embed_endpoint = self.endpoint.replace("/api/generate", "/api/embeddings")
        req = urllib.request.Request(embed_endpoint, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                resp = json.loads(r.read().decode('utf-8'))
                return resp.get('embedding', None)
        except Exception:
            # Silently degrade if embedding model missing or timeout
            return None

    def vibe_check(self, text):
        prompt = f"Does this code use hardcoded colors or raw pixel values instead of theme variables?\n\nCODE: {text[:1000]}\n\nAnswer YES or NO."
        return self.generate(prompt, system="You are a binary linter. Answer ONLY with YES or NO.")

    def lessword_compress(self, text):
        system = "You are an English compression engine. You MUST output ONLY in English. Do not use any other languages. Use terse, telegraphic fragments."
        prompt = f"Convert this text to English Lessword Mode (terse, fragment sentences, 100% technical facts):\n\nTEXT: {text}\n\nENGLISH LESSWORD OUTPUT:"
        return self.generate(prompt, system=system)


    def draft_boilerplate(self, intent):
        # Requires Medium Intelligence
        block_msg = self.check_tier(2, "Boilerplate Drafting")
        if block_msg:
            return block_msg
            
        system = "You are a Senior Architect LLM. Generate standard boilerplate code for the given intent. Output ONLY the code, no markdown wrappers."
        prompt = f"Draft the boilerplate component for this intent:\n\n{intent}"
        code = self.generate(prompt, system=system)
        return code if code else "[DELEGATE_TO_CLOUD] Error: Generation failed. Fallback to Cloud Agent."

    def extract_triplets(self, text):
        # Requires High Intelligence
        block_msg = self.check_tier(3, "Complex Triplet Extraction")
        if block_msg:
            return block_msg
            
        system = "You are a Brainvibing Knowledge Extractor. Extract triplets in JSON format."
        prompt = f"Extract (Subject, Predicate, Object) from this text:\n{text}"
        res = self.generate(prompt, system=system)
        return res if res else "[DELEGATE_TO_CLOUD] Error: Extraction failed. Fallback to Cloud Agent."

# ============================================================================
# SECTION 2: VECTOR MATH & RAG DIAGNOSTICS
# ============================================================================

from core.db import pack_vector, unpack_vector, cosine_similarity
compute_cosine = cosine_similarity

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

        # Relevance: fraction of query tokens present in retrieved chunks
        query_overlap = len(query_words.intersection(chunk_words))
        relevance = query_overlap / max(len(query_words), 1)

        # Faithfulness: fraction of answer tokens grounded in retrieved chunks
        if generated_answer:
            answer_words = set(generated_answer.lower().split())
            answer_overlap = len(answer_words.intersection(chunk_words))
            faithfulness = answer_overlap / max(len(answer_words), 1)
        else:
            # Context Grounding / Coverage Density (retrieval-only mode)
            # Proportion of unique query terms supported by >= 2 independent chunk/sentence segments
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
                _log_telemetry(_e, "diagnostics.py:close")
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
# SECTION 3: COMPACTION, TOKEN SHRINK & DISTILLATION
# ============================================================================



ULTRA_PROTECTED_TERMS: Set[str] = {
    "db", "auth", "config", "impl", "fn", "req", "res", "ref", "param", "arg",
    "not", "no", "never", "none", "neither", "nor", "cannot", "without",
    "true", "false", "null", "if", "else", "return", "error", "fail", "pass",
    "except", "only", "always", "must"
}


class CorpusInformationCompactor:
    """Kompaktor berbasis Shannon Surprisal nyata menggunakan SQLite fts5vocab."""
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(get_persistence_db_path())
        self.conn: Optional[sqlite3.Connection] = None
        if os.path.exists(self.db_path):
            try:
                self.conn = connect_sqlite(self.db_path)
                self.conn.execute(
                    "CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts_vocab "
                    "USING fts5vocab(pages_fts, row);"
                )
            except Exception as _e:
                _log_telemetry(_e, "CorpusInformationCompactor:init")

    def _token_surprisal(self, tokens: List[str]) -> Dict[str, float]:
        local_counts = Counter(tokens)
        total_local = max(1, len(tokens))
        vocab_size = max(1, len(local_counts))
        scores = {
            t: -math.log2((cnt + 1.0) / (total_local + vocab_size))
            for t, cnt in local_counts.items()
        }
        if not self.conn or not tokens:
            return scores
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM pages;")
            total_docs = max(1, int(cur.fetchone()[0] or 1))
            unique_terms = list(set(tokens))
            stemmed_map = {t: re.sub(r'(?:ing|ed|es|s)$', '', t) for t in unique_terms if t}
            query_terms = list(set(unique_terms) | set(stemmed_map.values()))
            cur.execute(
                f"SELECT term, doc FROM pages_fts_vocab WHERE term IN ({','.join('?' for _ in query_terms)})",
                query_terms,
            )
            found = {}
            for term, df in cur.fetchall():
                found[term] = float(df)
            lam = 0.65
            for term in unique_terms:
                p_local = (local_counts[term] + 1.0) / (total_local + vocab_size)
                stem = stemmed_map.get(term, term)
                df = found.get(term) if term in found else found.get(stem)
                p_corpus = (df + 1.0) / (total_docs + 2.0) if df is not None else (1.0 / (total_docs + 2.0))
                p_interpolated = (lam * p_corpus) + ((1.0 - lam) * p_local)
                scores[term] = -math.log2(p_interpolated)
        except Exception as _e:
            _log_telemetry(_e, "CorpusInformationCompactor:surprisal")
        return scores

    def compact(self, text: str, keep_ratio: float = 0.5, preserve_code: bool = True) -> str:
        if keep_ratio >= 1.0 or not text.strip():
            return text
        guard = SyntaxAnchorGuard() if preserve_code else None
        work_text = guard.lock(text) if guard else text
        words = work_text.split()
        if len(words) <= 6:
            return text
        norm_tokens = [re.sub(r"[^\w]", "", w).lower() for w in words]
        surprisal_map = self._token_surprisal([t for t in norm_tokens if t])
        for t in surprisal_map:
            if t in ULTRA_PROTECTED_TERMS:
                surprisal_map[t] = max(surprisal_map[t], 25.0)
        ranked_vals = sorted(surprisal_map.values(), reverse=True)
        cutoff_idx = min(len(ranked_vals) - 1, max(0, int(len(ranked_vals) * keep_ratio)))
        threshold = ranked_vals[cutoff_idx] if ranked_vals else 0.0
        kept = [
            w for w, norm in zip(words, norm_tokens)
            if not norm
            or "\x00__orion_anchor_" in w
            or norm in ULTRA_PROTECTED_TERMS
            or (w.isupper() and len(w) >= 2)
            or surprisal_map.get(norm, 99.0) >= threshold
        ]
        result = " ".join(kept)
        return guard.unlock(result) if guard else result

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()



def shrink_json(text: str, max_items: int = 2) -> str:
    """
    Compresses JSON by collapsing long repetitive lists/arrays while preserving schemas and samples.
    """
    try:
        data = json.loads(text)
    except Exception as _e:
        _log_telemetry(_e, 'shrink.py:json_parse')
        return shrink_log(text)

    def _collapse(obj):
        if isinstance(obj, list):
            if len(obj) <= max_items:
                return [_collapse(item) for item in obj]
            # Capture schema keys if list of dicts
            keys = set()
            for item in obj[:10]:
                if isinstance(item, dict):
                    keys.update(item.keys())
            
            sample_head = [_collapse(item) for item in obj[:max_items]]
            summary_meta = {
                "__collapsed_items__": len(obj) - max_items,
                "__total_items__": len(obj),
            }
            if keys:
                summary_meta["__item_schema_keys__"] = sorted(list(keys))
            return sample_head + [summary_meta]
        elif isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                if isinstance(v, str) and len(v) > 500:
                    new_dict[k] = v[:150] + f"... [truncated {len(v) - 150} chars]"
                else:
                    new_dict[k] = _collapse(v)
            return new_dict
        return obj

    collapsed = _collapse(data)
    return json.dumps(collapsed, indent=2, ensure_ascii=False)


def shrink_csv(text: str, max_rows: int = 3) -> str:
    """
    Compresses CSV/TSV datasets into header, schema types, first N rows, and last M rows.
    """
    lines = text.strip().splitlines()
    if len(lines) <= (max_rows * 2) + 2:
        return text

    # Detect delimiter
    sample = "\n".join(lines[:5])
    try:
        dialect = csv.Sniffer().sniff(sample)
        delim = dialect.delimiter
    except Exception as _e:
        _log_telemetry(_e, 'shrink.py:csv_sniff')
        delim = "\t" if "\t" in lines[0] else ","

    reader = list(csv.reader(io.StringIO(text), delimiter=delim))
    if not reader:
        return text

    headers = reader[0]
    data_rows = reader[1:]
    total_rows = len(data_rows)

    if total_rows <= (max_rows * 2):
        return text

    # Infer column types from sample
    types = []
    if data_rows:
        sample_row = data_rows[0]
        for val in sample_row:
            val = val.strip()
            if val.isdigit():
                types.append("int")
            else:
                try:
                    float(val)
                    types.append("float")
                except ValueError:
                    types.append("str")

    out = io.StringIO()
    writer = csv.writer(out, delimiter=delim)
    writer.writerow(headers)
    if types and len(types) == len(headers):
        writer.writerow([f"<{t}>" for t in types])

    for row in data_rows[:max_rows]:
        writer.writerow(row)

    omitted_count = total_rows - (max_rows * 2)
    writer.writerow([f"... [omitted {omitted_count} rows | total rows: {total_rows}] ..."] + [""] * (len(headers) - 1))

    for row in data_rows[-max_rows:]:
        writer.writerow(row)

    return out.getvalue().strip()


def shrink_log(text: str, max_repeats: int = 2) -> str:
    """
    Collapses repeating log lines, strips non-essential timestamps, keeps stack traces.
    """
    lines = text.splitlines()
    if len(lines) <= 20:
        return text

    # Regex to extract core log content without timestamp/thread noise
    ts_pattern = re.compile(r"^\s*\[?\d{4}[-/]\d{2}[-/]\d{2}[ T]\d{2}:\d{2}:\d{2}[^\s\]]*\]?\s*")
    
    compressed_lines = []
    prev_core = None
    repeat_count = 0
    first_raw = None

    for line in lines:
        core = ts_pattern.sub("", line).strip()
        # Keep stack traces uncompressed
        is_trace = any(marker in line for marker in ["Traceback", "File \"", "Exception:", "Error:", "Caused by:"])
        
        if core == prev_core and not is_trace:
            repeat_count += 1
        else:
            if repeat_count > 0:
                if repeat_count < max_repeats:
                    for _ in range(repeat_count):
                        compressed_lines.append(first_raw)
                else:
                    compressed_lines.append(f"  ... [repeated {repeat_count} times: {prev_core[:100]}]")
            prev_core = core
            repeat_count = 0
            first_raw = line
            compressed_lines.append(line)

    if repeat_count > 0:
        if repeat_count < max_repeats:
            for _ in range(repeat_count):
                compressed_lines.append(first_raw)
        else:
            compressed_lines.append(f"  ... [repeated {repeat_count} times: {prev_core[:100]}]")

    # If log is still excessively long (> 150 lines), sample head and decisive tail
    if len(compressed_lines) > 150:
        head = compressed_lines[:40]
        tail = compressed_lines[-60:]
        omitted = len(compressed_lines) - 100
        return "\n".join(head + [f"\n--- [... omitted {omitted} lines of routine logs ...] ---\n"] + tail)

    return "\n".join(compressed_lines)


def shrink_ast_python(text: str) -> str:
    """
    Hollows Python AST: keeps classes, methods, signatures, docstrings, replaces bodies with '...'.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return shrink_ast_generic(text)

    class HollowingTransformer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            return self._hollow_body(node)

        def visit_AsyncFunctionDef(self, node):
            self.generic_visit(node)
            return self._hollow_body(node)

        def _hollow_body(self, node):
            new_body = []
            # Keep docstring if present
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                new_body.append(node.body[0])
            # Replace rest with Ellipsis (...)
            new_body.append(ast.Expr(value=ast.Constant(value=...)))
            node.body = new_body
            return node

    hollowed_tree = HollowingTransformer().visit(tree)
    try:
        return ast.unparse(hollowed_tree)
    except Exception as _e:
        _log_telemetry(_e, 'shrink.py:ast_unparse')
        return shrink_ast_generic(text)


def shrink_ast_generic(text: str) -> str:
    """
    Generic heuristic hollowing for Dart, TypeScript, Go, etc.
    Collapses multi-line function bodies '{ ... }' while preserving declarations.
    """
    lines = text.splitlines()
    if len(lines) <= 50:
        return text

    output = []
    in_block = 0
    skipped = 0

    decl_pattern = re.compile(r"^\s*(export\s+)?(class|interface|function|def|func|async|void|public|private|protected|static|override)")

    for line in lines:
        stripped = line.strip()
        delta = line.count('{') - line.count('}')
        new_in_block = max(0, in_block + delta)
        if decl_pattern.match(line) or in_block == 0 or new_in_block == 0:
            if skipped > 0:
                output.append(f"    ... [omitted {skipped} lines of implementation] ...")
                skipped = 0
            output.append(line)
        else:
            skipped += 1

        in_block = new_in_block

    if skipped > 0:
        output.append(f"    ... [omitted {skipped} lines of implementation] ...")

    return "\n".join(output)


def shrink_content(text: str, filename_hint: str = "", fmt: str = "auto") -> str:
    """
    Main dispatcher for shrinking content based on format or filename.
    """
    if not text or not text.strip():
        return text

    hint = filename_hint.lower()
    
    if fmt == "json" or (fmt == "auto" and (hint.endswith(".json") or text.strip().startswith(("{", "[")))):
        try:
            return shrink_json(text)
        except Exception as _e:
            _log_telemetry(_e, 'shrink.py:dispatch_json')

    if fmt == "csv" or (fmt == "auto" and (hint.endswith((".csv", ".tsv")))):
        return shrink_csv(text)

    if fmt in ("ast", "python") or (fmt == "auto" and hint.endswith(".py")):
        return shrink_ast_python(text)

    if fmt in ("ast", "python") or (fmt == "auto" and hint.endswith((".dart", ".ts", ".js", ".go", ".rs", ".java", ".cpp"))):
        return shrink_ast_generic(text)

    if fmt == "log" or (fmt == "auto" and (hint.endswith(".log") or "Traceback" in text or "Exception" in text)):
        return shrink_log(text)

    # Default fallback: check if log-like or text
    if any(m in text for m in ["Traceback", "Error:", "Exception:"]):
        return shrink_log(text)

    lines = text.splitlines()
    if len(lines) > 200:
        head = lines[:60]
        tail = lines[-60:]
        omitted = len(lines) - 120
        return "\n".join(head + [f"\n... [... omitted {omitted} lines ...] ...\n"] + tail)

    return text

def shrink_main(argv=None):
    parser = argparse.ArgumentParser(description="Orion Shrink Token Compressor")
    parser.add_argument("target", help="File to shrink or '-' for stdin")
    parser.add_argument("--format", dest="fmt", default="auto", choices=["auto", "json", "csv", "log", "ast", "python"])
    args = parser.parse_args(argv)

    if args.target == "-":
        content = sys.stdin.read()
        hint = ""
    elif os.path.exists(args.target):
        with open(args.target, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        hint = args.target
    else:
        print(f"File not found: {args.target}", file=sys.stderr)
        return 1

    compressed = shrink_content(content, filename_hint=hint, fmt=args.fmt)
    orig_len = len(content)
    comp_len = len(compressed)
    ratio = (1.0 - (comp_len / orig_len)) * 100.0 if orig_len > 0 else 0.0

    print(compressed)
    print(f"\n[ORION SHRINK] Size: {orig_len:,} chars -> {comp_len:,} chars ({ratio:.1f}% reduction)", file=sys.stderr)
    return 0

def select_best_distill_model(base_url: str, user_model: str = ""):
    """
    Selects best local distillation model: prioritizes small, fast models (0.5B - 3B).
    """
    if user_model:
        return user_model

    try:
        from core.capabilities import get_available_models
        installed = get_available_models(base_url or "http://127.0.0.1:11434")
    except Exception:
        installed = []
    if not installed:
        return "qwen2.5:0.5b"

    # Priority list for ultra-fast, lightweight local extraction
    preferred = [
        "qwen2.5:0.5b", "qwen2.5:1.5b", "llama3.2:1b", "llama3.2:3b",
        "qwen2.5-coder:1.5b", "qwen2.5-coder:0.5b", "phi3:mini", "mistral:latest"
    ]
    for pref in preferred:
        for model_name in installed:
            if model_name.startswith(pref) or pref in model_name:
                return model_name

    return installed[0]


def distill_via_ollama(text: str, base_url: str, focus: str = "", model_name: str = "") -> str:
    """
    Executes zero-cloud local distillation via Ollama API.
    """
    target_model = select_best_distill_model(base_url, model_name)
    focus_clause = f"Focus strictly on: {focus}." if focus else "Focus on root causes, errors, key entities, and metrics."
    
    prompt = (
        f"You are a technical data distiller for an AI coding agent.\n"
        f"{focus_clause}\n"
        f"Compress the input text into maximum 5 ultra-dense bullet points using Lessword format.\n"
        f"Omit all conversational filler, preambles, and pleasantries. Extract raw facts, file paths, line numbers, and errors.\n\n"
        f"INPUT TEXT:\n{text[:12000]}\n\n"
        f"DISTILLED EXTRACTION:"
    )

    payload = json.dumps({
        "model": target_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 250
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "Orion/1.0"}
    )

    with urllib.request.urlopen(req, timeout=15.0) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result.get("response", "").strip()


def heuristic_fallback_distill(text: str, focus: str = "") -> str:
    """
    Graceful offline fallback: performs heuristic deterministic distillation in pure Python.
    """
    lines = text.splitlines()
    
    # 1. Extract critical error & status frames
    error_markers = ["error:", "exception:", "failed:", "fatal:", "critical:", "traceback", "status:", "errno"]
    signal_lines = []
    for line in lines:
        lower = line.lower()
        if any(m in lower for m in error_markers):
            cleaned = line.strip()
            if cleaned and cleaned not in signal_lines:
                signal_lines.append(cleaned)
                if len(signal_lines) >= 5:
                    break

    # 2. Extract referenced paths & symbols
    path_regex = re.compile(r"([a-zA-Z0-9_./\\-]+\.[a-zA-Z0-9]{1,6}(?::\d+)?)")
    found_paths = set()
    for m in path_regex.finditer(text):
        p = m.group(1).replace("\\", "/")
        if not any(ign in p for ign in ["http://", "https://", "127.0.0.1"]):
            found_paths.add(p)
            if len(found_paths) >= 5:
                break

    # 3. Apply Layer 2 shrink
    shrunk_preview = shrink_content(text)
    preview_lines = [l for l in shrunk_preview.splitlines() if l.strip()][:4]

    out = ["[HEURISTIC EXTRACTION (Offline Fallback)]"]
    if focus:
        out.append(f"• Intent Scope: {focus}")
    if signal_lines:
        out.append("• Signals / Errors:")
        for s in signal_lines[:3]:
            out.append(f"  - {s[:120]}")
    if found_paths:
        out.append(f"• Referenced Paths: {', '.join(sorted(list(found_paths)))}")
    out.append("• Key Sample Lines:")
    for pl in preview_lines:
        out.append(f"  > {pl[:100]}")

    return "\n".join(out)


def distill_content(text: str, focus: str = "", model_name: str = "") -> str:
    """
    Unified entrypoint: tries local Ollama first, gracefully falls back to Layer 2 heuristic extraction.
    """
    base_url = resolve_ollama_base_url()
    if base_url:
        try:
            summary = distill_via_ollama(text, base_url, focus=focus, model_name=model_name)
            if summary:
                return summary
        except Exception as e:
            _log_telemetry(e, 'distill.py:call_ollama')
            print(f"[ORION DISTILL] Ollama call failed ({e}). Falling back to heuristic extraction...", file=sys.stderr)

    # Graceful Fallback
    print("[ORION DISTILL] Ollama offline or unreachable. Engaging Layer 2 heuristic fallback...", file=sys.stderr)
    return heuristic_fallback_distill(text, focus=focus)

def distill_main(argv=None):
    parser = argparse.ArgumentParser(description="Orion Distill Layer 3 Distillation")
    parser.add_argument("target", help="File or '-' for stdin")
    parser.add_argument("--focus", default="", help="Distillation focus")
    parser.add_argument("--model", dest="model_name", default="", help="Ollama model")
    args = parser.parse_args(argv)

    if args.target == "-":
        content = sys.stdin.read()
    elif os.path.exists(args.target):
        with open(args.target, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    else:
        print(f"File not found: {args.target}", file=sys.stderr)
        return 1

    summary = distill_content(content, focus=args.focus, model_name=args.model_name)
    print(summary)
    return 0


# ============================================================================
# SECTION 4: SURGICAL MEMORY COMPRESSION
# ============================================================================

ARCHIVE_DIR = os.path.join(WORKSPACE_DIR, '.orion', 'archive')
ARCHIVE_FILE = os.path.join(ARCHIVE_DIR, 'compressed_memory.md')
HANDOFF_FILE = os.path.join(WORKSPACE_DIR, '.orion', 'working', 'handoff.md')
BLUEPRINT_FILE = os.path.join(WORKSPACE_DIR, 'context', '00_Strategy', 'BLUEPRINT.md')
STRATEGY_MEMORY_FILE = os.path.join(WORKSPACE_DIR, 'context', '00_Strategy', 'MEMORY.md')
LEGACY_MEMORY_FILE = os.path.join(WORKSPACE_DIR, 'MEMORY.md')

FRONTMATTER_REGEX = re.compile(r"\A(---\r?\n.*?\r?\n---\r?\n)(.*)", re.DOTALL)

SENSITIVE_BASENAME_REGEX = re.compile(
    r"(?ix)^("
    r"\.env(\..+)?"
    r"|\.netrc"
    r"|credentials(\..+)?"
    r"|secrets?(\..+)?"
    r"|passwords?(\..+)?"
    r"|id_(rsa|dsa|ecdsa|ed25519)(\.pub)?"
    r"|authorized_keys"
    r"|known_hosts"
    r"|.*\.(pem|key|p12|pfx|crt|cer|jks|keystore|asc|gpg)"
    r")$"
)

SENSITIVE_PATH_COMPONENTS = frozenset({
    ".ssh", ".aws", ".gnupg", ".kube", ".docker",
    "credential", "credentials", "secret", "secrets",
})

def split_frontmatter(text: str):
    """Surgically detach YAML frontmatter before compression to prevent LLM destruction."""
    m = FRONTMATTER_REGEX.match(text)
    if m:
        return m.group(1), m.group(2)
    return "", text

def is_sensitive_path(path_str: str) -> bool:
    """Hard refusal check to protect secrets, credentials, and private keys."""
    p = os.path.normpath(path_str)
    basename = os.path.basename(p)
    if SENSITIVE_BASENAME_REGEX.match(basename):
        return True
    parts = set(p.lower().replace('\\', '/').split('/'))
    if parts & SENSITIVE_PATH_COMPONENTS:
        return True
    return False

# ============================================================================
# NATIVE ORION COMPACTOR & LESSWORD ENGINE (commands/brain.py)
# Pure Python 3.10+ Stdlib — Zero External Repo Fingerprints
# Implements GEMINI.md §2 & .agents/skills/lessword/SKILL.md Mechanically
# ============================================================================

LESSWORD_PHRASE_MAP: List[Tuple[re.Pattern, str]] = [
    # Pembuka percakapan & basa-basi (Ceremony & Staging)
    (re.compile(r"(?i)\b(?:sure|certainly|of course|i would be happy to|i'd be happy to|let me go ahead and|let's dive in|here is what you need to know|at its core)[,!.\s]*"), ""),
    (re.compile(r"(?i)\b(?:it might be worth|you could consider|it would be good to|please make sure to|make sure to|remember to)\s+"), ""),
    # Reduksi frasa bertele-tele menjadi kata kerja/hubung langsung
    (re.compile(r"(?i)\bin order to\b"), "to"),
    (re.compile(r"(?i)\bthe reason is because\b|\bdue to the fact that\b|\bas a result of\b"), "because"),
    (re.compile(r"(?i)\bimplement a solution for\b"), "fix"),
    (re.compile(r"(?i)\butilize\b|\butilizing\b"), "use"),
    (re.compile(r"(?i)\bfacilitate\b"), "help"),
    (re.compile(r"(?i)\bfor the purpose of\b"), "for"),
    (re.compile(r"(?i)\bin the event that\b"), "if"),
    (re.compile(r"(?i)\bwith regard to\b|\bwith respect to\b"), "on"),
    (re.compile(r"(?i)\bprior to\b"), "before"),
    (re.compile(r"(?i)\bsubsequent to\b"), "after"),
    (re.compile(r"(?i)\bis able to\b|\bhas the ability to\b"), "can"),
    (re.compile(r"(?i)\bextensive\b"), "big"),
    # Kata pengisi (Filler adverbs)
    (re.compile(r"(?i)\b(?:just|really|basically|actually|simply|essentially|generally|literally|definitely|honestly)\s+"), ""),
    (re.compile(r"(?i)\b(?:however|furthermore|additionally|in addition),?\s+"), ""),
]

LESSWORD_ULTRA_ABBREV: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"(?i)\bdatabase\b"), "DB"),
    (re.compile(r"(?i)\bauthentication\b"), "auth"),
    (re.compile(r"(?i)\bconfiguration\b"), "config"),
    (re.compile(r"(?i)\bimplementation\b"), "impl"),
    (re.compile(r"(?i)\bfunction\b"), "fn"),
    (re.compile(r"(?i)\brequest\b"), "req"),
    (re.compile(r"(?i)\bresponse\b"), "res"),
    (re.compile(r"(?i)\breference\b"), "ref"),
    (re.compile(r"(?i)\bparameter\b"), "param"),
    (re.compile(r"(?i)\bargument\b"), "arg"),
    (re.compile(r"(?i)\s+leads to\s+|\s+results in\s+|\s+causes\s+"), " -> "),
]

SAFETY_BOUNDARY_ESCAPE_RE = re.compile(
    r"(?is)\b(?:drop\s+table|delete\s+from|truncate\s+table|rm\s+-rf|git\s+reset\s+--hard|git\s+push\s+--force|cve-\d{4}-\d+|critical\s+vulnerability)\b"
    r"|\b(?:back\s*up|rollback|snapshot)\b.{1,200}\b(?:drop|delete|migrate|purge|destroy)\b"
)


class SyntaxAnchorGuard:
    """
    Pelindung payload verbatim sesuai aturan .agents/skills/lessword/references/lessword-compress.md:
    Mengisolasi code fences, inline backticks, URL, file paths, wikilinks, dan environment variables
    ke dalam slot memori sementara agar tidak pernah tersentuh oleh pemangkasan teks.
    """
    def __init__(self):
        self._slots: Dict[str, str] = {}
        self._seq: int = 0

    def _stash(self, match: re.Match) -> str:
        token = f"\x00__orion_anchor_{self._seq}__\x00"
        self._slots[token] = match.group(0)
        self._seq += 1
        return token

    def lock(self, text: str) -> str:
        # 1. Blok kode berpagar (```...``` atau ~~~...~~~)
        text = re.sub(r"(?:```[\s\S]*?```|~~~[\s\S]*?~~~)", self._stash, text)
        # 2. Inline code (`...`)
        text = re.sub(r"`[^`\n]+`", self._stash, text)
        # 3. Wikilinks [[...]] & Markdown links [...](...) & URL
        text = re.sub(r"\[\[[^\]]+\]\]|\[[^\]]+\]\([^)]+\)|https?://[^\s)\]>]+", self._stash, text)
        # 4. Path file eksplisit & baris nomor (misal: .agents/scripts/orion.py:42)
        text = re.sub(r"(?:\.?[a-zA-Z0-9_-]+/)+[a-zA-Z0-9_.-]+(?::\d+)?", self._stash, text)
        # 5. Environment variables & konstanta UPPER_SNAKE_CASE / akronim teknis (kecuali preposisi 2 huruf)
        text = re.sub(
            r"\$[A-Z_][A-Z0-9_]*|\b(?!(?:IN|ON|AT|TO|BY|OR|IF|IS|IT|AS|OF|DO|BE|WE|SO|AN)\b)[A-Z][A-Z0-9_]{1,}\b",
            self._stash,
            text,
        )
        return text

    def unlock(self, text: str) -> str:
        for token in reversed(list(self._slots.keys())):
            text = text.replace(token, self._slots[token])
        return text


STREAM_MAX_CHARS = 8000
STREAM_HEAD_LINES = 60
STREAM_TAIL_LINES = 40
STREAM_SALVAGE_MAX = 12
STREAM_SALVAGE_LINE = 300
STREAM_SPILL_KEEP = 40
STREAM_DIAGNOSTIC_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:err!|(?:error|errors|fail|failed|failure|failing|exception|traceback|panic|fatal"
    r"|denied|refused|timed?[ _-]?out|assert(?:ion)?|segfault|undefined reference|cannot find|not found|warning)"
    r"(?![A-Za-z0-9]))",
    re.IGNORECASE,
)


class OrionCompactor:
    """
    Mesin Kompresi Konteks & Memori Native .agents.
    Menyatukan protokol Lessword (lite, full, ultra), AST Hollowing,
    Payload Stream Shaping, dan Chronological Section Decay.
    """

    @staticmethod
    def requires_auto_clarity(text: str) -> bool:
        """Memeriksa apakah teks memuat peringatan keamanan atau operasi destruktif yang wajib jelas."""
        return bool(SAFETY_BOUNDARY_ESCAPE_RE.search(text))

    # -------------------------------------------------------------------------
    # TINGKAT 1: LITE (Lossless Cleanup — 0% Perubahan Semantik)
    # -------------------------------------------------------------------------
    @classmethod
    def run_lite(cls, text: str, elide: bool = True) -> str:
        if not text:
            return text
        # Bersihkan kode escape ANSI terminal
        clean = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", text)
        # Pangkas data URI base64 gambar yang membengkakkan konteks
        clean = re.sub(
            r"data:image/[a-zA-Z+]+;base64,[a-zA-Z0-9+/=]{120,}",
            "[IMAGE_DATA_REDACTED]",
            clean,
        )
        # Lipat baris berulang yang identik & hapus trailing spaces
        lines = [line.rstrip() for line in clean.splitlines()]
        out_lines: List[str] = []
        prev = None
        dup_count = 0
        for line in lines:
            if line and line == prev:
                dup_count += 1
                continue
            if dup_count > 0:
                out_lines.append(f"  ... [repeated {dup_count}x] ...")
                dup_count = 0
            out_lines.append(line)
            prev = line
        if dup_count > 0:
            out_lines.append(f"  ... [repeated {dup_count}x] ...")

        if elide and len(out_lines) > 100:
            head = out_lines[:35]
            tail = out_lines[-45:]
            omitted = len(out_lines) - 80
            out_lines = head + [f"\n--- [... {omitted} lines omitted by Stream Filter ...] ---\n"] + tail

        return re.sub(r"\n{3,}", "\n\n", "\n".join(out_lines)).strip()

    # -------------------------------------------------------------------------
    # TINGKAT 1.5: STREAM (Bounded Tool Output — Diagnostics Survive the Cut)
    # -------------------------------------------------------------------------
    @staticmethod
    def _spill_full_output(text: str) -> Optional[str]:
        """Persist the untrimmed output so the dropped middle is searchable instead of re-run."""
        try:
            spill_dir = os.path.join(ORION_DIR, "working", "spill")
            os.makedirs(spill_dir, exist_ok=True)
            digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:12]
            target = os.path.join(spill_dir, f"out-{digest}.txt")
            if not os.path.isfile(target):
                with open(target, "w", encoding="utf-8", errors="replace") as fh:
                    fh.write(text)
            stale = sorted(
                (os.path.join(spill_dir, n) for n in os.listdir(spill_dir) if n.endswith(".txt")),
                key=os.path.getmtime,
                reverse=True,
            )[STREAM_SPILL_KEEP:]
            for old in stale:
                os.remove(old)
            return os.path.relpath(target, WORKSPACE_DIR).replace("\\", "/")
        except OSError as _e:
            _log_telemetry(_e, "OrionCompactor:_spill_full_output")
            return None

    @classmethod
    def elide_output(
        cls,
        text: str,
        max_chars: int = STREAM_MAX_CHARS,
        head: int = STREAM_HEAD_LINES,
        tail: int = STREAM_TAIL_LINES,
        spill: bool = True,
    ) -> str:
        """Bound oversized output: keep the opening and closing lines, rescue diagnostic lines from the cut middle."""
        if not text or len(text) <= max_chars:
            return text
        recover = ""
        if spill:
            path = cls._spill_full_output(text)
            if path:
                recover = f" Full output: {path} (search it; do not re-run)."
        lines = text.splitlines()
        if len(lines) <= head + tail:
            keep = max_chars // 2
            dropped = len(text) - 2 * keep
            if dropped <= 0:
                return text
            return f"{text[:keep]}\n... [elided {dropped} chars from the middle.{recover}] ...\n{text[-keep:]}"

        middle = lines[head:len(lines) - tail]
        rescued: List[str] = []
        for line in middle:
            if len(rescued) >= STREAM_SALVAGE_MAX:
                break
            if STREAM_DIAGNOSTIC_RE.search(line):
                rescued.append(line if len(line) <= STREAM_SALVAGE_LINE else line[:STREAM_SALVAGE_LINE - 1] + "…")
        note = f"; {len(rescued)} diagnostic line(s) kept below" if rescued else ""
        marker = f"... [elided {len(middle)} lines; kept first {head}, last {tail}{note}.{recover}] ..."
        bounded = "\n".join(lines[:head] + [marker] + rescued + lines[len(lines) - tail:])
        return bounded if len(bounded) < len(text) else text

    @classmethod
    def run_stream(cls, text: str) -> str:
        """Lossless cleanup followed by diagnostic-preserving elision, for terminal and tool output."""
        return cls.elide_output(cls.run_lite(text, elide=False))

    # -------------------------------------------------------------------------
    # TINGKAT 2: FULL (Standar Default Lessword — ASD-STE100 Concise Prose)
    # -------------------------------------------------------------------------
    @classmethod
    def run_full(cls, text: str, check_safety_escape: bool = True) -> str:
        if not text:
            return text
        frontmatter, body = split_frontmatter(text)
        body = cls.run_lite(body)

        # Auto-Clarity Escape: jangan pangkas kalimat jika berisi operasi destruktif/keamanan
        if check_safety_escape and cls.requires_auto_clarity(body):
            return (frontmatter + body) if frontmatter else body

        guard = SyntaxAnchorGuard()
        locked = guard.lock(body)

        for pattern, replacement in LESSWORD_PHRASE_MAP:
            locked = pattern.sub(replacement, locked)

        # Hapus artikel (a, an, the) dengan tetap menjaga heading, tabel, dan kata negasi
        processed_lines: List[str] = []
        for line in locked.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or "|" in stripped:
                processed_lines.append(line)
                continue
            compact_line = re.sub(r"(?i)\b(?:a|an|the)\s+", "", line)
            compact_line = re.sub(r"[ \t]{2,}", " ", compact_line)
            processed_lines.append(compact_line)

        unlocked = guard.unlock("\n".join(processed_lines))
        return (frontmatter + unlocked) if frontmatter else unlocked

    # -------------------------------------------------------------------------
    # PAYLOAD STREAM SHAPER (Deteksi Otomatis Kode, Grep, Traceback, JSON, CSV)
    # -------------------------------------------------------------------------
    @classmethod
    def shape_structured_payload(cls, text: str, filename_hint: str = "") -> Tuple[str, str]:
        if not text:
            return text, "prose"
        if len(text) < 180 and not filename_hint:
            return text, "prose"

        lines = text.splitlines()
        hint = filename_hint.lower()

        # 1. Kode Sumber -> AST Structural Hollowing (.py, .ts, .dart, .rs, .go, .kt)
        code_sig_re = re.compile(r"^\s*(?:import |from |export |class |def |async def |function |pub fn |fn |struct |interface )")
        code_hits = sum(1 for l in lines[:50] if code_sig_re.match(l))
        if hint.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".dart", ".rs", ".go", ".kt", ".java", ".cpp", ".c", ".cs")) or code_hits >= 2:
            if hint.endswith(".py") or "def " in text:
                return shrink_ast_python(text), "ast_python"
            return shrink_ast_generic(text), "ast_polyglot"

        # 2. Output Pencarian Baris (`path:line:match` — bukan jam `12:30:00`)
        span_re = re.compile(r"^([^\s:]+):(\d+):(.*)$")
        span_hits = [l for l in lines if span_re.match(l.strip()) and not re.match(r"^\d{2}:\d{2}:\d{2}", l.strip())]
        if len(span_hits) >= 4 and len(span_hits) >= len(lines) * 0.4:
            kept = span_hits[:30]
            overflow = len(span_hits) - len(kept)
            if overflow > 0:
                files = sorted({span_re.match(l.strip()).group(1) for l in span_hits[30:] if span_re.match(l.strip())})
                kept.append(f"... [+{overflow} matches in {len(files)} files: {', '.join(files[:6])}] ...")
            return "\n".join(kept), "search_spans"

        # 3. Stack Trace / Error Frame Elision (Header + 10 first + 3 root-cause frames)
        is_traceback = "traceback (most recent call last)" in text.lower() or (
            any(lines[0].lower().startswith(p) for p in ("traceback", "exception:", "error:"))
        )
        if is_traceback and len(lines) > 16:
            elided_count = len(lines) - 14
            if elided_count > 0:
                shaped = [lines[0]] + lines[1:11] + [f"  ... [{elided_count} stack frames elided] ..."] + lines[-3:]
                return "\n".join(shaped), "error_trace"

        # 4. Struktur Data JSON & CSV
        trimmed = text.strip()
        if (hint.endswith(".json") or trimmed.startswith(("{", "["))) and len(trimmed) > 800:
            try:
                return shrink_json(trimmed, max_items=2), "json_schema"
            except Exception as _e:
                _log_telemetry(_e, "OrionCompactor:shrink_json")
        if hint.endswith((".csv", ".tsv")) and len(lines) > 12:
            return shrink_csv(text, max_rows=3), "csv_schema"

        # 5. Log Terminal Panjang
        if len(lines) > 65:
            return shrink_log(text), "log_stream"

        return text, "prose"

    # -------------------------------------------------------------------------
    # CHRONOLOGICAL SECTION DECAY (Pemadatan Memori & Handoff Berbasis Usia Seksi)
    # -------------------------------------------------------------------------
    @classmethod
    def decay_historical_sections(cls, text: str, fresh_keep: int = 2, mid_keep: int = 4) -> str:
        """
        Memadatkan seksi-seksi lama (`## ...`) pada dokumen memori/handoff/log:
          - 2 seksi terbaru : Dipertahankan 100% utuh (verbatim)
          - Seksi ke-3..4   : Dikompresi dengan mode Lessword Full
          - Seksi ke-5+     : Dipadatkan menjadi judul + 1 baris intisari (<=120 karakter)
        Seksi kritis (Resume Point, Anti-Goals, Fractal Shorthand) selalu dilindungi.
        """
        frontmatter, body = split_frontmatter(text)
        blocks = re.split(r"(?m)^(?=##\s+)", body)
        if len(blocks) <= fresh_keep + 1:
            return text

        preamble = blocks[0] if not blocks[0].startswith("## ") else ""
        sections = blocks[1:] if preamble else blocks

        protected_headers = ("resume point", "anti-goal", "fractal shorthand", "active state", "core guardrail")

        # Calculate chronological age distance across non-protected sections
        non_protected_indices = [
            i for i, sec in enumerate(sections)
            if not any(p in sec.splitlines()[0].lower() for p in protected_headers if sec.strip().splitlines())
        ]
        total_np = len(non_protected_indices)
        np_rank_map = {orig_idx: (total_np - 1 - rank) for rank, orig_idx in enumerate(non_protected_indices)}

        out_sections: List[str] = []

        for idx, sec in enumerate(sections):
            sec_lines = [l for l in sec.strip().splitlines() if l.strip()]
            if not sec_lines:
                continue

            header = sec_lines[0]
            if any(p in header.lower() for p in protected_headers):
                out_sections.append(sec.strip())
                continue
            age_distance = np_rank_map.get(idx, 0)

            if age_distance < fresh_keep:
                out_sections.append(sec.strip())
            elif age_distance < mid_keep:
                out_sections.append(cls.run_full(sec.strip()))
            else:
                lead = next((l.strip() for l in sec_lines[1:] if not l.strip().startswith("#")), "")
                if len(lead) > 120:
                    lead = lead[:117] + "..."
                dropped = max(0, len(sec_lines) - 2)
                summary = f"{header}\n- {lead} _[{dropped} historical lines archived]_" if lead else header
                out_sections.append(summary)

        combined = (preamble.rstrip() + "\n\n" if preamble.strip() else "") + "\n\n".join(out_sections)
        return (frontmatter + combined) if frontmatter else combined

    # -------------------------------------------------------------------------
    # TINGKAT 3: AGGRESSIVE (Payload Shaper + Chronological Decay + Lessword Full)
    # -------------------------------------------------------------------------
    @classmethod
    def run_aggressive(cls, text: str, filename_hint: str = "") -> Tuple[str, List[str]]:
        shaped, kind = cls.shape_structured_payload(text, filename_hint=filename_hint)
        if kind != "prose":
            return shaped, [f"shaper:{kind}"]

        steps = []
        current = text
        if current.count("\n## ") >= 3:
            current = cls.decay_historical_sections(current, fresh_keep=2, mid_keep=4)
            steps.append("chronological_decay")

        current = cls.run_full(current)
        steps.append("lessword_full")
        return current, steps

    # -------------------------------------------------------------------------
    # TINGKAT 4: ULTRA (Surprisal Pruning + Telegraphic Abbreviations)
    # -------------------------------------------------------------------------
    @classmethod
    def run_ultra(cls, text: str, filename_hint: str = "", ratio: float = 0.5) -> Tuple[str, List[str]]:
        shaped, kind = cls.shape_structured_payload(text, filename_hint=filename_hint)
        if kind in ("ast_python", "ast_polyglot", "json_schema", "csv_schema", "search_spans", "error_trace"):
            return shaped, [f"shaper:{kind}"]

        frontmatter, body = split_frontmatter(text)
        if body.count("\n## ") >= 3:
            body = cls.decay_historical_sections(body, fresh_keep=1, mid_keep=3)

        body = cls.run_full(body, check_safety_escape=True)
        if cls.requires_auto_clarity(body):
            return ((frontmatter + body) if frontmatter else body), ["safety_escape_bypass"]

        guard = SyntaxAnchorGuard()
        locked = guard.lock(body)

        # Terapkan singkatan Ultra sesuai spesifikasi .agents/skills/lessword/SKILL.md
        for pattern, abbrev in LESSWORD_ULTRA_ABBREV:
            locked = pattern.sub(abbrev, locked)

        # Pangkas token bersurprisal rendah melalui fts5vocab di .orion/orion.db (preserve_code=False karena sudah di-lock oleh guard di atas)
        with CorpusInformationCompactor() as compactor:
            pruned = compactor.compact(locked, keep_ratio=ratio, preserve_code=False)

        unlocked = guard.unlock(pruned)
        final_text = (frontmatter + unlocked) if frontmatter else unlocked
        return final_text, ["chronological_decay", "lessword_ultra_abbrev", "surprisal_fts5vocab"]

    # -------------------------------------------------------------------------
    # TINGKAT 5: PIPELINE (Rantai Deterministik Multi-Tahap — Default)
    # -------------------------------------------------------------------------
    @classmethod
    def run_pipeline(cls, text: str, filename_hint: str = "") -> Tuple[str, List[str]]:
        stages: List[str] = []
        current = cls.run_lite(text)
        stages.append("lite_clean")

        shaped, kind = cls.shape_structured_payload(current, filename_hint=filename_hint)
        if kind != "prose" and len(shaped) < len(current):
            current = shaped
            stages.append(f"shaper:{kind}")

        if current.count("\n## ") >= 3:
            decayed = cls.decay_historical_sections(current, fresh_keep=2, mid_keep=4)
            if len(decayed) < len(current):
                current = decayed
                stages.append("section_decay")

        if kind not in ("ast_python", "ast_polyglot", "json_schema", "csv_schema"):
            lw = cls.run_full(current)
            if len(lw) < len(current):
                current = lw
                stages.append("lessword_full")

        return current, stages

    # -------------------------------------------------------------------------
    # INTEGRITY VERIFICATION GATE (Anti-Regression & Zero-Corruption Check)
    # -------------------------------------------------------------------------
    @classmethod
    def compress(cls, text: str, level: str = "pipeline", filename_hint: str = "", ratio: float = 0.5) -> Dict[str, Any]:
        t_start = time.time()
        lvl = level.lower().strip()

        if lvl == "off":
            out, stages = text, []
        elif lvl == "lite":
            out, stages = cls.run_lite(text), ["lite_clean"]
        elif lvl == "stream":
            out, stages = cls.run_stream(text), ["lite_clean", "stream_elide"]
        elif lvl in ("full", "standard", "lessword"):
            out, stages = cls.run_full(text), ["lessword_full"]
        elif lvl == "aggressive":
            out, stages = cls.run_aggressive(text, filename_hint=filename_hint)
        elif lvl == "ultra":
            out, stages = cls.run_ultra(text, filename_hint=filename_hint, ratio=ratio)
        else:
            lvl = "pipeline"
            out, stages = cls.run_pipeline(text, filename_hint=filename_hint)

        orig_tokens = max(1, math.ceil(len(text) / 4.0))
        comp_tokens = max(1, math.ceil(len(out) / 4.0))
        delta_tokens = orig_tokens - comp_tokens

        # Gate 1: Pastikan pagar kode (```) tidak ada yang terpotong
        if lvl != "stream" and text.count("```") != out.count("```"):
            return {
                "output": text,
                "level": lvl,
                "status": "REVERTED_FENCE_MISMATCH",
                "original_tokens": orig_tokens,
                "compressed_tokens": orig_tokens,
                "savings_pct": 0.0,
                "stages": stages,
                "elapsed_ms": round((time.time() - t_start) * 1000.0, 2),
            }

        # Gate 2: Jika tidak ada penghematan nyata, kembalikan teks asli tanpa modifikasi
        if delta_tokens <= 0 or len(out) >= len(text):
            return {
                "output": text,
                "level": lvl,
                "status": "UNCHANGED_OPTIMAL",
                "original_tokens": orig_tokens,
                "compressed_tokens": orig_tokens,
                "savings_pct": 0.0,
                "stages": stages,
                "elapsed_ms": round((time.time() - t_start) * 1000.0, 2),
            }

        return {
            "output": out,
            "level": lvl,
            "status": "COMPRESSED",
            "original_tokens": orig_tokens,
            "compressed_tokens": comp_tokens,
            "savings_pct": round((delta_tokens / orig_tokens) * 100.0, 2),
            "stages": stages,
            "elapsed_ms": round((time.time() - t_start) * 1000.0, 2),
        }


def telegraphic_shrink(text: str) -> str:
    """Alias kompatibilitas ke OrionCompactor level full."""
    return OrionCompactor.compress(text, level="full")["output"]


def lessword_compress_text(text: str, level: str = "full") -> str:
    """Mesin utama Lessword yang kini dilindungi SyntaxAnchorGuard."""
    return OrionCompactor.compress(text, level=level)["output"]


lessword_compress = lessword_compress_text


def compact_target(target_path: str, ratio: float = 0.5, level: str = "pipeline") -> Tuple[str, str]:
    """Router file tunggal menggunakan OrionCompactor."""
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Target not found: {target_path}")
    with open(target_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    res = OrionCompactor.compress(content, level=level, filename_hint=target_path, ratio=ratio)
    return res["output"], "+".join(res["stages"]) or "unchanged"


def compactor_main(argv=None):
    parser = argparse.ArgumentParser(description="Native Orion Compactor & Lessword Engine")
    parser.add_argument("target", nargs="?", help="Text string or path to file")
    parser.add_argument("--text", type=str, help="Prose string to compact")
    parser.add_argument("--file", type=str, help="Path to text or markdown file to compact")
    parser.add_argument("--level", type=str, default="pipeline", choices=["lite", "stream", "full", "aggressive", "ultra", "pipeline", "off"], help="Compression level")
    parser.add_argument("--ratio", type=float, default=0.5, help="Retention ratio for ultra/surprisal pruning")
    parser.add_argument("--stdin", action="store_true", help="Read the text to compact from standard input")
    parser.add_argument("--index", type=str, help="Deprecated index argument (noop)")
    args = parser.parse_args(argv)

    target_file = args.file or (args.target if args.target and os.path.exists(args.target) else None)

    if target_file and os.path.isfile(target_file):
        with open(target_file, "r", encoding="utf-8", errors="replace") as f:
            orig = f.read()
        res = OrionCompactor.compress(orig, level=args.level, filename_hint=target_file, ratio=args.ratio)
        compacted = res["output"]
        orig_words = len(orig.split())
        comp_words = len(compacted.split())
        stages_str = "+".join(res["stages"]) or "unchanged"
        print(f"[COMPACTION SUMMARY: {stages_str}] Level: {res['level']} | Status: {res['status']} | Orig: {res['original_tokens']} tok ({orig_words} words) | Compact: {res['compressed_tokens']} tok ({comp_words} words) | Savings: {res['savings_pct']}% ({res['elapsed_ms']}ms)")
        print("--------------------------------------------------------------------------------")
        print(compacted)
        return 0

    input_text = ""
    if args.stdin:
        input_text = sys.stdin.read()
    elif args.text:
        input_text = args.text
    elif args.target and not os.path.exists(args.target):
        input_text = args.target

    if not input_text:
        parser.print_help()
        return 1

    res = OrionCompactor.compress(input_text, level=args.level, ratio=args.ratio)
    compacted = res["output"]
    orig_words = len(input_text.split())
    comp_words = len(compacted.split())
    stages_str = "+".join(res["stages"]) or "unchanged"
    print(f"[COMPACTION SUMMARY: {stages_str}] Level: {res['level']} | Status: {res['status']} | Orig: {res['original_tokens']} tok ({orig_words} words) | Compact: {res['compressed_tokens']} tok ({comp_words} words) | Savings: {res['savings_pct']}% ({res['elapsed_ms']}ms)")
    print("--------------------------------------------------------------------------------")
    print(compacted)
    return 0

def get_strategy_memory_file():

    if os.path.exists(STRATEGY_MEMORY_FILE):
        return STRATEGY_MEMORY_FILE
    if os.path.exists(LEGACY_MEMORY_FILE):
        return LEGACY_MEMORY_FILE
    return STRATEGY_MEMORY_FILE

def generate_fractal_shorthand(dry_run: bool = False):
    """
    Parses architectural details from BLUEPRINT.md and translates it into a
    highly compressed Fractal State Shorthand (DSL) for small models.
    """
    if not os.path.exists(BLUEPRINT_FILE):
        return False
        
    with open(BLUEPRINT_FILE, 'r', encoding='utf-8') as f:
        blueprint = f.read()
        
    shorthand = "[ARCH: "
    
    # Holographic Context Hash Generation (Idea 1)
    import hashlib
    state_hash = hashlib.sha256(blueprint.encode()).hexdigest()[:4].upper()
    shorthand = f"[STATE_HASH: 0x{state_hash}] [ARCH: "
    
    if "flutter" in blueprint.lower(): shorthand += "Flutter]"
    elif "react" in blueprint.lower(): shorthand += "React]"
    else: shorthand += "Unknown]"
    
    if "supabase" in blueprint.lower(): shorthand += " [DB: Supabase]"
    if "riverpod" in blueprint.lower(): shorthand += " [STATE: Riverpod]"
    
    shorthand += " [TIER: BUDGET]"
    
    if dry_run:
        print(f"[DRY RUN] Generated Fractal Shorthand: {shorthand}")
        return True

    updated = False
    # Inject into handoff
    if os.path.exists(HANDOFF_FILE):
        with open(HANDOFF_FILE, 'r', encoding='utf-8') as f:
            handoff = f.read()
            
        if "# FRACTAL SHORTHAND" in handoff:
            new_handoff = re.sub(r'(# FRACTAL SHORTHAND\r?\n).*?(?=\n\n)', r'\1' + shorthand, handoff, flags=re.DOTALL)
        else:
            new_handoff = f"# FRACTAL SHORTHAND\n{shorthand}\n\n" + handoff
            
        atomic_write_text(HANDOFF_FILE, new_handoff)
        updated = True

    # Inject into standard context memory file
    mem_file = get_strategy_memory_file()
    if os.path.exists(mem_file):
        with open(mem_file, 'r', encoding='utf-8') as f:
            mem_content = f.read()
        if "# FRACTAL SHORTHAND" in mem_content:
            new_mem = re.sub(r'(# FRACTAL SHORTHAND\r?\n).*?(?=\n\n)', r'\1' + shorthand, mem_content, flags=re.DOTALL)
        else:
            new_mem = f"# FRACTAL SHORTHAND\n{shorthand}\n\n" + mem_content
        if new_mem != mem_content:
            with open(mem_file, 'w', encoding='utf-8') as f:
                f.write(new_mem)
        updated = True

    if updated:
        print(f"[OK] Generated Fractal Shorthand: {shorthand}")
        return True
    return False

def compress_handoff(dry_run: bool = False):
    if not os.path.exists(HANDOFF_FILE):
        return False

    with open(HANDOFF_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Look for Offload entries to compress (anything between 3. Context Offloading and 4. Anti-Goals)
    offload_pattern = r'(## 3\. Context Offloading Entry.*?\n)(?=\n## 4\.|\n## \d+\.|$)'
    
    match = re.search(offload_pattern, content, re.DOTALL | re.IGNORECASE)
    if not match:
        return False

    offloaded_text = match.group(1).strip()
    
    if "placeholder" in offloaded_text.lower():
        return False

    def lessword_compress_section(m):
        text = m.group(0)
        compressed_text = lessword_compress_text(text)
        return f"## 3. Context Offloading Entry\n> [COMPRESSED: Lessword Token-Clipper Active]\n{compressed_text}\n\n"

    new_handoff_content = re.sub(
        r'(## 3\. Context Offloading Entry\n).*?(?=\n## 4\.|\n## \d+\.|$)',
        lessword_compress_section,
        content,
        flags=re.DOTALL | re.IGNORECASE
    )

    if content == new_handoff_content:
         return False

    if dry_run:
        print("[DRY RUN] Would compress handoff memory and archive offloaded section.")
        return True

    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        
    mode = 'a' if os.path.exists(ARCHIVE_FILE) else 'w'
    with open(ARCHIVE_FILE, mode, encoding='utf-8') as f:
        f.write(f"\n\n--- Compressed on {datetime.now()} ---\n{offloaded_text}")

    # Rewrite handoff
    atomic_write_text(HANDOFF_FILE, new_handoff_content)
        
    print(f"[OK] Handoff memory successfully compressed.")
    return True

def compress_tasks(dry_run: bool = False):
    tasks_dir = os.path.join(WORKSPACE_DIR, '.orion', 'working', 'tasks')
    if not os.path.exists(tasks_dir):
        return False
        
    if not os.path.exists(ARCHIVE_DIR):
        if not dry_run:
            os.makedirs(ARCHIVE_DIR, exist_ok=True)

    compressed = False
    for file in os.listdir(tasks_dir):
        if not file.endswith('.md'): continue
        path = os.path.join(tasks_dir, file)
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Target status indicators meaning the task is done
        is_done = bool(re.search(r'Status:\s*\[x\]', content, re.IGNORECASE) or re.search(r'Status:\s*DONE', content, re.IGNORECASE))
        if is_done:
            dest = os.path.join(ARCHIVE_DIR, file)
            if dry_run:
                print(f"[DRY RUN] Would archive completed task: {file}")
            else:
                shutil.move(path, dest)
                print(f"[OK] Archived completed task: {file}")
            compressed = True
    return compressed
            

def check_compression_eligibility():
    """
    IDE-4: Smart Memory Compression with Eligibility Rules.
    Checks orion.db to report which pages/nodes are eligible for compression
    and which are protected. Inspired by Cloudflare's compression eligibility.
    """
    db_path = os.path.join(WORKSPACE_DIR, '.orion', 'orion.db')
    if not os.path.exists(db_path):
        print("[SKIP] No orion.db found — eligibility check skipped.")
        return
    
    conn = connect_sqlite(db_path)
    cursor = conn.cursor()
    
    # Check if access_count column exists
    cursor.execute("PRAGMA table_info(pages)")
    cols = [r[1] for r in cursor.fetchall()]
    if 'access_count' not in cols:
        print("[SKIP] pages.access_count not yet migrated — skipping eligibility filter.")
        conn.close()
        return
    
    IMPORTANCE_THRESHOLD = 4
    MIN_ACCESS_COUNT = 2
    MIN_AGE_DAYS = 14
    
    # Find eligible pages
    cursor.execute("""
        SELECT path, access_count, importance, updated 
        FROM pages 
        WHERE (importance IS NULL OR importance < ?)
        AND (access_count IS NULL OR access_count < ?)
        AND (julianday('now') - julianday(COALESCE(updated, datetime('now')))) >= ?
        ORDER BY updated ASC
    """, (IMPORTANCE_THRESHOLD, MIN_ACCESS_COUNT, MIN_AGE_DAYS))
    
    eligible = cursor.fetchall()
    
    # Find protected pages
    cursor.execute("""
        SELECT path, access_count, importance 
        FROM pages 
        WHERE importance >= ? OR access_count >= ?
    """, (IMPORTANCE_THRESHOLD, MIN_ACCESS_COUNT))
    
    protected = cursor.fetchall()
    
    print(f"[ELIGIBILITY] {len(eligible)} pages eligible for compression, {len(protected)} protected.")
    
    if eligible:
        for path, ac, imp, updated in eligible[:5]:
            print(f"  📋 {path} (access={ac or 0}, importance={imp or 1})")
    
    if protected:
        for path, ac, imp in protected[:5]:
            print(f"  🛡️ {path} (access={ac or 0}, importance={imp or 1}) — PROTECTED")
    
    conn.close()


def compress_strategy_memory(dry_run: bool = False):
    mem_file = get_strategy_memory_file()
    if not os.path.exists(mem_file):
        return False
    with open(mem_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.splitlines()
    if len(lines) > 300:
        print(f"[NOTICE] {os.path.basename(mem_file)} has {len(lines)} lines (>300). Pruning archived entries.")
        milestone_match = re.search(r'(## ✅ Tactical Milestones\r?\n)(.*?)(?=\r?\n## |\Z)', content, re.DOTALL)
        if milestone_match:
            milestones = [m for m in milestone_match.group(2).strip().splitlines() if m.strip()]
            if len(milestones) > 5:
                to_archive = milestones[:-5]
                to_keep = milestones[-5:]
                if dry_run:
                    print(f"[DRY RUN] Would archive {len(to_archive)} completed milestones from {os.path.basename(mem_file)}.")
                    return True
                if not os.path.exists(ARCHIVE_DIR):
                    os.makedirs(ARCHIVE_DIR, exist_ok=True)
                with open(ARCHIVE_FILE, 'a', encoding='utf-8') as af:
                    af.write(f"\n\n--- Archived Milestones from MEMORY.md on {datetime.now()} ---\n" + "\n".join(to_archive))
                new_milestones_block = milestone_match.group(1) + "\n".join(to_keep) + "\n"
                content = content.replace(milestone_match.group(0), new_milestones_block)
                atomic_write_text(mem_file, content)
                print(f"[OK] Archived {len(to_archive)} completed milestones from {os.path.basename(mem_file)}.")
                return True
    return False

def compress_file(target_path: str, dry_run: bool = False) -> bool:
    """
    Compress a specific target markdown/text file into lessword format.
    Guarantees:
    - Rejects sensitive files (security policy)
    - Preserves frontmatter verbatim via split_frontmatter
    - Preserves code fences, URLs, and paths
    - Saves human-readable backup to <filename>.original.md
    """
    abs_path = os.path.abspath(target_path)
    if not os.path.exists(abs_path):
        print(f"[ERROR] Target file does not exist: {target_path}")
        return False
    if is_sensitive_path(abs_path):
        print(f"[REFUSED] Refusing to compress sensitive file (security policy): {os.path.basename(abs_path)}")
        return False
    if abs_path.endswith('.original.md'):
        print(f"[SKIP] Refusing to re-compress backup file: {os.path.basename(abs_path)}")
        return False
        
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}")
        return False
        
    compressed_content = lessword_compress_text(content)
    orig_words = len(content.split())
    comp_words = len(compressed_content.split())
    savings = (1 - (comp_words / orig_words)) * 100 if orig_words > 0 else 0

    if dry_run:
        print(f"[DRY RUN] Would compress {os.path.basename(abs_path)}: {orig_words} words -> {comp_words} words ({savings:.1f}% reduction).")
        return True

    backup_path = abs_path + ".original.md" if not abs_path.endswith('.md') else abs_path[:-3] + ".original.md"
    if not os.path.exists(backup_path):
        atomic_write_text(backup_path, content)
        print(f"[BACKUP] Original saved to: {os.path.basename(backup_path)}")
        
    atomic_write_text(abs_path, compressed_content)
        
    print(f"[OK] Compressed {os.path.basename(abs_path)}: {orig_words} words -> {comp_words} words ({savings:.1f}% reduction).")
    return True

def compress_memory(dry_run: bool = False):
    print(f"[CLEAN] Surgical Memory Compression starting... {'(DRY RUN)' if dry_run else ''}")
    check_compression_eligibility()
    generate_fractal_shorthand(dry_run=dry_run)
    strategy_compressed = compress_strategy_memory(dry_run=dry_run)
    handoff_compressed = compress_handoff(dry_run=dry_run)
    tasks_compressed = compress_tasks(dry_run=dry_run)
    
    if not strategy_compressed and not handoff_compressed and not tasks_compressed:
        print("[OK] No compressable context found. System memory is lean and efficient.")
    else:
        status_msg = "Memory compression simulated." if dry_run else f"Memory compression complete. Stale memories moved to {ARCHIVE_DIR}"
        print(f"[OK] {status_msg}")

def compress_main(argv=None):
    parser = argparse.ArgumentParser(description="Compress memory and markdown files into lessword format.")
    parser.add_argument("target", nargs="?", default=None, help="Specific file to compress")
    parser.add_argument("--file", type=str, default=None, help="Specific file to compress")
    parser.add_argument("--dry-run", action="store_true", help="Simulate compression without modifying files")
    args = parser.parse_args(argv)

    target_path = args.target or args.file
    if target_path:
        compress_file(target_path, dry_run=args.dry_run)
    else:
        compress_memory(dry_run=args.dry_run)
    return 0


# ============================================================================
# SECTION 5: MEMORY VIRTUALIZATION & GRAPH COMMUNITY CLUSTERING
# ============================================================================

from core.memory import (  # noqa: F401  (kernel memory primitives, re-exported for CLI gateway)
    HALF_LIFE_DAYS,
    LAMBDA_DECAY,
    ArchivalMemoryManager,
    CoreMemoryManager,
    GraphCommunityClusterer,
    MultiLayerMemoryManager,
    ObsidianVaultExporter,
    RecallMemoryManager,
    SecondBrainManager,
    _safe_stem,
    calculate_retrieval_score,
    cosine_similarity,
    louvain_clustering,
    pack_vector,
    unpack_vector,
)

def memory_main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Orion OS Virtual Memory Engine (VirtualMemoryHierarchy + DualLevelGraphRAG pattern)")
    subparsers = parser.add_subparsers(dest="command")

    # Core Memory
    core_parser = subparsers.add_parser("core", help="Manage in-context working Core Memory")
    core_sub = core_parser.add_subparsers(dest="subaction")
    core_sub.add_parser("get", help="Display Core Memory blocks")
    core_app = core_sub.add_parser("append", help="Append text to Core Memory")
    core_app.add_argument("section", choices=["human", "persona"], help="Memory section")
    core_app.add_argument("content", help="Content to append")
    core_rep = core_sub.add_parser("replace", help="Replace substring in Core Memory")
    core_rep.add_argument("section", choices=["human", "persona"], help="Memory section")
    core_rep.add_argument("old", help="Old text to replace")
    core_rep.add_argument("new", help="New replacement text")

    # Archival Memory
    arch_parser = subparsers.add_parser("archival", help="Deep persistent FTS5 Archival Memory")
    arch_sub = arch_parser.add_subparsers(dest="subaction")
    arch_ins = arch_sub.add_parser("insert", help="Store content in Archival Memory")
    arch_ins.add_argument("path", help="Key or virtual path")
    arch_ins.add_argument("content", help="Text content to index")
    arch_ins.add_argument("--category", default="archival", help="Category tag")
    arch_ins.add_argument("--pillar", default="core", help="Architecture pillar")
    arch_search = arch_sub.add_parser("search", help="Search Archival Memory via FTS5")
    arch_search.add_argument("query", help="Search query")
    arch_search.add_argument("--limit", type=int, default=5, help="Result limit")
    arch_search.add_argument("--json", action="store_true", help="JSON output")

    # Recall Memory
    # Recall Memory
    rec_parser = subparsers.add_parser("recall", help="Recall chronological operational events")
    rec_sub = rec_parser.add_subparsers(dest="subaction")
    rec_list = rec_sub.add_parser("list", help="List recent events")
    rec_list.add_argument("--limit", type=int, default=10, help="Event limit")
    rec_list.add_argument("--json", action="store_true", help="JSON output")
    rec_turns = rec_sub.add_parser("turns", help="List recent conversational turns")
    rec_turns.add_argument("--limit", type=int, default=10, help="Turn limit")
    rec_turns.add_argument("--json", action="store_true", help="JSON output")
    rec_record = rec_sub.add_parser("record-turn", help="Record a turn into recall turns")
    rec_record.add_argument("role", choices=["user", "agent", "system"], help="Speaker role")
    rec_record.add_argument("content", help="Turn text content")
    rec_record.add_argument("--tool-calls", default=None, help="Serialized tool calls")

    # Facts / Multi-Layer Memory
    facts_parser = subparsers.add_parser("facts", help="Manage multi-layer facts memory and history")
    facts_sub = facts_parser.add_subparsers(dest="subaction")
    facts_set = facts_sub.add_parser("set", help="Set a fact")
    facts_set.add_argument("key", help="Fact key")
    facts_set.add_argument("value", help="Fact value")
    facts_set.add_argument("--layer", choices=["user", "session", "persona"], default="session")
    facts_set.add_argument("--author", default="agent")
    facts_get = facts_sub.add_parser("get", help="Get active facts")
    facts_get.add_argument("--layer", choices=["user", "session", "persona", "all"], default="all")
    facts_hist = facts_sub.add_parser("history", help="Get fact mutation history")
    facts_hist.add_argument("key", help="Fact key")

    # Communities
    comm_parser = subparsers.add_parser("communities", help="Discover hierarchical graph communities")
    comm_parser.add_argument("--limit", type=int, default=10, help="Community limit")
    comm_parser.add_argument("--json", action="store_true", help="JSON output")

    # Export Obsidian Vault
    vault_parser = subparsers.add_parser("export-vault", help="Export Orion graph into an interactive Obsidian Vault")
    vault_parser.add_argument("--out", default=None, help="Target vault output directory (default: .orion/vault)")

    # Second Brain
    brain_parser = subparsers.add_parser("second-brain", help="Generate 4-note Second Brain briefing (00-Overview to 03-Status)")
    brain_parser.add_argument("--out", default=None, help="Target brain directory (default: .orion/working/brain)")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0

    if args.command == "core":
        mgr = CoreMemoryManager()
        if args.subaction == "get":
            print(json.dumps(mgr.get_all(), indent=2))
        elif args.subaction == "append":
            updated = mgr.append(args.section, args.content)
            print(f"[CORE MEMORY] Appended to '{args.section}'.")
            print(json.dumps(updated, indent=2))
        elif args.subaction == "replace":
            ok = mgr.replace(args.section, args.old, args.new)
            if ok:
                print(f"[CORE MEMORY] Successfully replaced text in '{args.section}'.")
            else:
                print(f"[FAIL] Target text not found in '{args.section}'.")
                sys.exit(1)
        else:
            print(mgr.format_prompt_block())

    elif args.command == "archival":
        arch = ArchivalMemoryManager()
        try:
            if args.subaction == "insert":
                ok = arch.insert(args.path, args.content, category=args.category, pillar=args.pillar)
                if ok:
                    print(f"[ARCHIVAL MEMORY] Indexed '{args.path}' in FTS5 graph.")
                else:
                    print(f"[ERROR] Failed to index archival item.")
                    sys.exit(1)
            elif args.subaction == "search":
                hits = arch.search(args.query, limit=args.limit)
                if args.json:
                    print(json.dumps(hits, indent=2))
                else:
                    print(f"\n🔍 Archival Memory Query: '{args.query}' ({len(hits)} hits)")
                    print("=" * 60)
                    for idx, h in enumerate(hits, 1):
                        print(f"[{idx}] {h['path']} (category: {h['category']}, rank: {h['rank']:.2f})")
                        print(f"    Snippet: {h['snippet']}")
            else:
                arch_parser.print_help()
        finally:
            arch.close()

    elif args.command == "recall":
        rec = RecallMemoryManager()
        try:
            if args.subaction == "turns":
                turns = rec.get_recent_turns(limit=args.limit)
                if args.json:
                    print(json.dumps(turns, indent=2))
                else:
                    print(f"\n💬 Recall Conversation Turns ({len(turns)} turns)")
                    print("=" * 60)
                    for t in turns:
                        print(f"[{t['role']}] {t['content'][:80]} (time: {t['created_at']})")
            elif args.subaction == "record-turn":
                rec.record_turn(args.role, args.content, tool_calls=args.tool_calls)
                print(f"[RECALL MEMORY] Recorded turn for role '{args.role}'.")
            else:
                events = rec.get_recent(limit=args.limit)
                if args.json:
                    print(json.dumps(events, indent=2))
                else:
                    print(f"\n⏱️ Recall Memory Timeline ({len(events)} events)")
                    print("=" * 60)
                    for e in events:
                        print(f"- [{e['timestamp']}] Event: {e['event_type']} (Exit Code: {e['exit_code']}, Load: {e['context_load']})")
        finally:
            rec.close()

    elif args.command == "facts":
        from core.memory import MultiLayerMemoryManager
        mlm = MultiLayerMemoryManager()
        try:
            if args.subaction == "set":
                mlm.set_fact(args.layer, args.key, args.value)
                print(f"[FACTS MEMORY] Set '{args.key}' in layer '{args.layer}'.")
            elif args.subaction == "get":
                layer = None if args.layer == "all" else args.layer
                facts = mlm.get_facts(layer=layer)
                print(json.dumps(facts, indent=2))
            elif args.subaction == "history":
                hist = mlm.get_history(args.key)
                print(json.dumps(hist, indent=2))
            else:
                facts_parser.print_help()
        finally:
            mlm.close()

    elif args.command == "communities":
        clusterer = GraphCommunityClusterer()
        comms = clusterer.detect_communities(max_communities=args.limit)
        if args.json:
            print(json.dumps(comms, indent=2))
        else:
            print(f"\n🌐 Knowledge Graph Communities (DualLevelGraphRAG Louvain Clustering)")
            print("=" * 60)
            print(f"Discovered {len(comms)} topological communities:\n")
            for c in comms:
                print(f"[Community #{c['community_id']:02d}] Size: {c['size']} | Type: {c['dominant_type']}")
                print(f"  Summary : {c['summary']}")
                print(f"  Entities: {', '.join(c['top_entities'])}\n")

    elif args.command == "export-vault":
        exporter = ObsidianVaultExporter()
        res = exporter.export_vault(args.out)
        print(f"\n🔮 Orion Obsidian Vault Generated Successfully!")
        print(f"Directory: {res['vault_dir']}")
        print(f"Notes Created: {res['total_notes']} ({res['nodes_exported']} nodes, {res['communities_exported']} communities)")
        print(f"Open this directory in Obsidian to explore the graph visualizer.")

    elif args.command == "second-brain":
        sb = SecondBrainManager(args.out)
        notes = sb.build_second_brain()
        print(f"\n🧠 Second Brain Protocol Generated (4 High-Density Briefing Notes):")
        for k, v in notes.items():
            print(f"  - [{k.upper()}]: {v}")

    else:
        parser.print_help()



# ============================================================================
# SECTION 6: RULE MATRIX COMPILATION & MATRIX QUERY
# ============================================================================

def parse_markdown_to_dict(md_content):
    """
    Very basic heuristic parser: 
    Converts Markdown headings to dict keys, bullets to lists.
    """
    matrix = {}
    current_section = "global"
    matrix[current_section] = []
    
    for line in md_content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Match headings ## 1. Section
        header_match = re.match(r'^#+\s*(.+)$', line)
        if header_match:
            current_section = header_match.group(1).strip()
            matrix[current_section] = []
            continue
            
        # Match bullets
        if line.startswith('- ') or line.startswith('* '):
            matrix[current_section].append(line[2:].strip())
        elif line.startswith('> '):
            matrix[current_section].append("CONSTRAINT: " + line[2:].strip())
        else:
            # Append to last item if exists, else append as new
            if matrix[current_section]:
                matrix[current_section][-1] += " " + line
            else:
                matrix[current_section].append(line)
                
    # Remove empty sections
    return {k: v for k, v in matrix.items() if v}

def compile_skill_routes():
    """
    Extracts skill metadata (name, description, triggers, references) from
    .agents/skills/*/SKILL.md into a compact .orion/matrix/skill_routes.json.
    """
    skills_dir = os.path.join(BASE_DIR, "skills")
    if not os.path.exists(skills_dir):
        return

    routes = []
    
    # Pre-defined high-precision triggers from JIT Knowledge Routing table
    JIT_TRIGGERS = {
        "ai-engineer": ["ai engineering", "llm drift", "probabilistic traits", "model drift", "ai engineer", "prompt injection", "evals"],
        "api-contract": ["api contract", "zod", "schemas", "request validation", "api schema", "openapi", "api safety"],
        "app-lifecycle": ["new project", "init", "scaffold", "legacy migration", "brownfield", "app builder", "feature sunset", "sunset code", "dead code purge"],
        "brain-graph": ["brain graph", "knowledge base", "ingest", "lint", "cross-reference", "triplet", "knowledge extraction", "orion"],
        "code-review": ["code review", "pr review", "diff audit", "security check", "pull request"],
        "cost-optimizer": ["cost analysis", "token budget", "llm costs", "performance", "latency", "speed optimization", "token reduction"],
        "data-logic": ["data immutability", "state management", "transformers", "dto", "unidirectional flow"],
        "frontend-experience": ["frontend", "debugging", "errors", "crashes", "runtime issues", "ux audit", "component lifecycle"],
        "integrity-sentinel": ["security audit", "qa", "testing", "bugs", "validation", "audit ledger", "audit vectors", "pre-completion"],
        "lessword": ["token reduction", "compression", "lessword", "be brief", "lessword mode", "/lessword"],
        "meta-agent-admin": ["meta-agent-admin", "/meta-agent-admin", "audit .agents", "ecosystem audit", "foundation review", "template health", "system mod", "rules"],
        "palette": ["accessibility", "a11y", "micro-interactions", "web ux", "aria", "semantic html"],
        "project-architect": ["system architecture", "database schema", "blueprint", "backend logic", "api server", "cache", "architectural standards"],
        "project-operator": ["deployment", "build", "release", "ci/cd", "devops", "pre-flight", "chaos engineering"],
        "saas-strategist": ["business strategy", "growth", "idea viability", "planning", "monetization"],
        "self-evolve": ["agent self-learning", "reflection", "pattern synthesis", "harness", "autoharness", "/learn", "temporal pulse"],
        "session-offload": ["session end", "handoff", "context eviction", "/session-offload", "auto-context"],
        "strict-tdd": ["test-driven development", "tdd", "writing tests", "red-green-refactor", "unit test", "strict-tdd"],
        "systematic-debugging": ["debugging", "systematic debugging", "scientific debugging", "root-cause", "reproduction"],
        "ui-finish": ["frontend ui", "layout", "aesthetics", "animations", "visual craft", "design token", "ui polish"],
        "worker-delegate": ["worker delegation", "sub-agent", "task splitting", "parallel worker", "delegate"]
    }

    for skill_name in sorted(os.listdir(skills_dir)):
        if skill_name == "internal":
            continue
        skill_path = os.path.join(skills_dir, skill_name, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue

        try:
            with open(skill_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue

        desc = ""
        from core.scanner import parse_frontmatter as _parse_fm
        fm, _ = _parse_fm(content)
        raw_desc = fm.get("description", "")
        if raw_desc:
            desc = " ".join(str(raw_desc).split())

        # Collect references
        ref_dir = os.path.join(skills_dir, skill_name, "references")
        references = []
        if os.path.isdir(ref_dir):
            for ref_file in sorted(os.listdir(ref_dir)):
                if ref_file.endswith(".md"):
                    references.append(os.path.join(".agents", "skills", skill_name, "references", ref_file).replace("\\", "/"))

        triggers = list(JIT_TRIGGERS.get(skill_name, []))
        desc_lower = desc.lower()
        if "use when" in desc_lower:
            when_part = desc_lower.split("use when", 1)[1]
            words = [w.strip(" .,()") for w in when_part.split() if len(w) > 3 and w not in triggers]
            triggers = list(dict.fromkeys(triggers + words[:8]))

        routes.append({
            "name": skill_name,
            "skill_path": os.path.join(".agents", "skills", skill_name, "SKILL.md").replace("\\", "/"),
            "description": desc[:150],
            "triggers": triggers,
            "references": references
        })

    out_file = os.path.join(MATRIX_DIR, "skill_routes.json")
    atomic_write_text(out_file, json.dumps(routes, indent=2))

    print(f"[OK] Compiled {len(routes)} skill routes into {out_file}")


def compile_all():
    if not os.path.exists(MATRIX_DIR):
        os.makedirs(MATRIX_DIR)
        
    rule_files = []
    for root, dirs, files in os.walk(RULES_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if f.endswith('.md') and not f.startswith('_'):
                rule_files.append(os.path.join(root, f))

    count = 0
    
    for rule_file in rule_files:
        filename = os.path.basename(rule_file)
        with open(rule_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        yaml_dict = parse_markdown_to_dict(content)
        
        rel = os.path.relpath(rule_file, RULES_DIR)
        out_name = rel.replace('\\', '__').replace('/', '__').replace('.md', '.json')
        out_path = os.path.join(MATRIX_DIR, out_name)
        
        atomic_write_text(out_path, json.dumps(yaml_dict, indent=2))
            
        count += 1
        
    print(f"[OK] Compiled {count} Markdown rules into JSON Matrices at {MATRIX_DIR}")
    compile_skill_routes()

def compile_rules_main(argv=None):
    compile_all()
    return 0

def query_matrix(keywords):
    workspace = get_workspace_dir()
    matrix_dir = os.path.join(workspace, ".orion", "matrix")
    
    if not os.path.exists(matrix_dir):
        print(f"Matrix directory not found at {matrix_dir}.")
        return
        
    results = {}
    for filename in os.listdir(matrix_dir):
        if not filename.endswith(".json"):
            continue
            
        filepath = os.path.join(matrix_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            file_results = {}
            for key, rules in data.items():
                if key == "global": continue
                
                # Check if keyword in key or any rule
                match = False
                for kw in keywords:
                    kw_lower = kw.lower()
                    if kw_lower in key.lower():
                        match = True
                        break
                    
                    if isinstance(rules, list):
                        for rule in rules:
                            if kw_lower in rule.lower():
                                match = True
                                break
                    elif isinstance(rules, str):
                        if kw_lower in rules.lower():
                            match = True
                    if match:
                        break
                            
                if match:
                    file_results[key] = rules
                    
            if file_results:
                results[filename] = file_results
        except Exception as e:
            print(f"Error parsing {filename}: {e}", file=sys.stderr)
            
    if results:
        print(json.dumps(results, indent=2))
    else:
        print("{}")

def matrix_query_main(argv=None):
    if argv:
        query_matrix(argv)
    else:
        print("Usage: orion.py matrix <keyword1> <keyword2> ...")
    return 0


# ============================================================================
# SECTION 7: RAW FILE INGESTION & CONTRADICTION RESOLUTION
# ============================================================================

def process_raw_files():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_dir = os.path.dirname(os.path.dirname(script_dir))
    project_root = os.path.dirname(agents_dir)
    
    raw_dir = os.path.join(project_root, "context", "raw")
    wiki_dir = os.path.join(project_root, ".orion", "sources", "wiki")
    
    if not os.path.exists(raw_dir):
        print(f"[INFO] No context/raw/ directory found at {raw_dir}")
        return
        
    os.makedirs(wiki_dir, exist_ok=True)
    
    files = [f for f in os.listdir(raw_dir) if os.path.isfile(os.path.join(raw_dir, f))]
    if not files:
        print("[INFO] No raw files to ingest.")
        return
        
    processed_count = 0
    error_count = 0
    for f in files:
        if f.startswith('.'):
            continue
            
        raw_path = os.path.join(raw_dir, f)
        base_name = os.path.splitext(f)[0]
        
        # Clean up filename for wiki standard
        safe_name = re.sub(r'[^A-Za-z0-9_-]', '_', base_name).strip('_')
        if not safe_name:
            safe_name = f"ingest_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
        wiki_path = os.path.join(wiki_dir, f"{safe_name}.md")
        
        try:
            with open(raw_path, 'r', encoding='utf-8', errors='replace') as infile:
                content = infile.read()
        except Exception as e:
            print(f"[ERROR] Could not read {f}: {e}")
            error_count += 1
            continue
            
        keywords = extract_keywords(content)
        tags_str = ", ".join([f'"{k}"' for k in keywords]) if keywords else ""
        inline_tags = " ".join([f"#{k}" for k in keywords])
        
        # Structure the markdown
        structured = f"""---
title: {safe_name.replace('_', ' ').title()}
ingested_at: {datetime.now().isoformat()}
source: context/raw/{f}
tags: [{tags_str}]
---

# {safe_name.replace('_', ' ').title()}

> **Auto-Ingested Document**
> Extracted Tags: {inline_tags}

## Raw Content
{content}
"""
        try:
            atomic_write_text(wiki_path, structured)
            processed_count += 1
            print(f"[SUCCESS] Ingested '{f}' -> '.orion/sources/wiki/{safe_name}.md'")
        except Exception as e:
            print(f"[ERROR] Could not write or remove {f}: {e}")
            error_count += 1
            
    if error_count > 0:
        print(f"\n[FAIL] Processed {processed_count} raw files with {error_count} error(s).")
        sys.exit(1)
    else:
        print(f"\n[DONE] Processed {processed_count} raw files.")

def raw_ingest_main(argv=None):
    process_raw_files()
    return 0

STRUCTURAL_RELATIONS = (
    "mentions", "imports", "defines", "defines_map",
    "routes_to", "executes", "inherits", "related_to",
    "REFERENCES", "CONTAINS", "DEPENDS_ON", "USES", "CALLS"
)

def detect_contradictions():
    """Scan edges for predicate collisions: same source+relation, different target."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Purge legacy false-positive contradictions caused by multi-target structural relations
    rel_placeholders = ",".join("?" for _ in STRUCTURAL_RELATIONS)
    cursor.execute(f"""
        DELETE FROM contradictions 
        WHERE edge_a_relation IN ({rel_placeholders}) OR edge_b_relation IN ({rel_placeholders})
    """, STRUCTURAL_RELATIONS + STRUCTURAL_RELATIONS)
    conn.commit()

    # Check if canonical relations table exists and has rows
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='relations'")
    has_relations = bool(cursor.fetchone())
    use_canonical = False
    if has_relations:
        cursor.execute("SELECT COUNT(*) FROM relations")
        if cursor.fetchone()[0] > 0:
            use_canonical = True

    if use_canonical:
        cursor.execute(f"""
            SELECT r1.subject_id, r1.predicate, r1.object_id, r2.object_id
            FROM relations r1
            JOIN relations r2 ON r1.subject_id = r2.subject_id 
                AND r1.predicate = r2.predicate 
                AND r1.object_id != r2.object_id
            WHERE r1.object_id < r2.object_id
                AND r1.predicate NOT IN ({rel_placeholders})
        """, STRUCTURAL_RELATIONS)
    else:
        # Find edges where same source_id + exclusive relation points to different targets
        cursor.execute(f"""
            SELECT e1.source_id, e1.relation, e1.target_id, e2.target_id
            FROM edges e1
            JOIN edges e2 ON e1.source_id = e2.source_id 
                AND e1.relation = e2.relation 
                AND e1.target_id != e2.target_id
            WHERE e1.target_id < e2.target_id
                AND e1.relation NOT IN ({rel_placeholders})
        """, STRUCTURAL_RELATIONS)
    
    collisions = cursor.fetchall()
    
    if not collisions:
        print("[OK] No predicate collisions detected in the graph.")
        conn.close()
        return
    
    print(f"[DETECT] Found {len(collisions)} potential contradictions:\n")
    
    new_count = 0
    for src, rel, target_a, target_b in collisions:
        # Check if this contradiction is already recorded
        cursor.execute("""
            SELECT id FROM contradictions 
            WHERE edge_a_source = ? AND edge_a_relation = ? 
            AND edge_a_target = ? AND edge_b_target = ?
        """, (src, rel, target_a, target_b))
        
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO contradictions 
                (edge_a_source, edge_a_target, edge_a_relation, edge_b_source, edge_b_target, edge_b_relation)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (src, target_a, rel, src, target_b, rel))
            new_count += 1
            print(f"  [NEW] ({src}) --[{rel}]--> ({target_a}) vs ({target_b})")
        else:
            print(f"  [KNOWN] ({src}) --[{rel}]--> ({target_a}) vs ({target_b})")
    
    conn.commit()
    conn.close()
    print(f"\n[DETECT] {new_count} new contradictions recorded, {len(collisions) - new_count} already known.")


def list_unresolved():
    """List all unresolved contradictions."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, edge_a_source, edge_a_relation, edge_a_target, edge_b_target, detected_at
        FROM contradictions 
        WHERE resolution = 'unresolved'
        ORDER BY detected_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("[OK] No unresolved contradictions.")
        return
    
    print(f"[LIST] {len(rows)} unresolved contradictions:\n")
    for cid, src, rel, ta, tb, detected in rows:
        print(f"  #{cid}: ({src}) --[{rel}]--> ({ta}) vs ({tb})  [detected: {detected}]")


def resolve(contradiction_id, resolution, evidence=""):
    """Resolve a contradiction by ID."""
    if resolution not in ('a_wins', 'b_wins', 'merged'):
        print(f"[ERROR] Invalid resolution: {resolution}. Must be: a_wins, b_wins, merged")
        sys.exit(1)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get the contradiction
    cursor.execute("SELECT * FROM contradictions WHERE id = ?", (contradiction_id,))
    row = cursor.fetchone()
    if not row:
        print(f"[ERROR] Contradiction #{contradiction_id} not found.")
        conn.close()
        sys.exit(1)
    
    # Update resolution
    cursor.execute("""
        UPDATE contradictions 
        SET resolution = ?, evidence = ?, resolved_at = datetime('now')
        WHERE id = ?
    """, (resolution, evidence, contradiction_id))
    
    # Adjust confidence scores
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='relations'")
    has_relations = bool(cursor.fetchone())

    if has_relations:
        if resolution == 'a_wins':
            cursor.execute("""
                UPDATE relations SET weight = MIN(weight * 1.2, 2.0)
                WHERE subject_id = ? AND object_id = ? AND predicate = ?
            """, (row[1], row[2], row[3]))
            cursor.execute("""
                UPDATE relations SET weight = MAX(weight * 0.5, 0.1)
                WHERE subject_id = ? AND object_id = ? AND predicate = ?
            """, (row[4], row[5], row[6]))
        elif resolution == 'b_wins':
            cursor.execute("""
                UPDATE relations SET weight = MAX(weight * 0.5, 0.1)
                WHERE subject_id = ? AND object_id = ? AND predicate = ?
            """, (row[1], row[2], row[3]))
            cursor.execute("""
                UPDATE relations SET weight = MIN(weight * 1.2, 2.0)
                WHERE subject_id = ? AND object_id = ? AND predicate = ?
            """, (row[4], row[5], row[6]))
    else:
        if resolution == 'a_wins':
            cursor.execute("""
                UPDATE edges SET confidence = MIN(confidence * 1.2, 2.0) 
                WHERE source_id = ? AND target_id = ? AND relation = ?
            """, (row[1], row[2], row[3]))
            cursor.execute("""
                UPDATE edges SET confidence = MAX(confidence * 0.5, 0.1) 
                WHERE source_id = ? AND target_id = ? AND relation = ?
            """, (row[4], row[5], row[6]))
        elif resolution == 'b_wins':
            cursor.execute("""
                UPDATE edges SET confidence = MAX(confidence * 0.5, 0.1) 
                WHERE source_id = ? AND target_id = ? AND relation = ?
            """, (row[1], row[2], row[3]))
            cursor.execute("""
                UPDATE edges SET confidence = MIN(confidence * 1.2, 2.0) 
                WHERE source_id = ? AND target_id = ? AND relation = ?
            """, (row[4], row[5], row[6]))
    
    conn.commit()
    conn.close()
    print(f"[RESOLVED] Contradiction #{contradiction_id} → {resolution}")


def contradict_main(argv=None):
    if not argv:
        print("Usage: orion.py contradict <detect|list|resolve> [...]")
        return 1
    action = argv[0].lower()
    if action == 'detect':
        detect_contradictions()
    elif action == 'list':
        list_unresolved()
    elif action == 'resolve':
        if len(argv) < 3:
            print("Usage: orion.py contradict resolve <ID> <a_wins|b_wins|merged> [evidence]")
            return 1
        cid = int(argv[1])
        res = argv[2]
        evidence = " ".join(argv[3:]) if len(argv) > 3 else ""
        resolve(cid, res, evidence)
    else:
        print(f"Unknown contradict action: {action}")
        return 1
    return 0


# ============================================================================
# SECTION 8: ORION OPERATIONS, GRAPH INGESTION & TRIPLETS
# ============================================================================

# WORKSPACE_DIR and ORION_DIR are already canonically imported from core.paths
MANIFEST_PATH = os.path.join(ORION_DIR, "_manifest.json")
LOG_PATH = os.path.join(ORION_DIR, "log.md")
INDEX_PATH = os.path.join(ORION_DIR, "index.md")
DB_PATH = os.path.join(ORION_DIR, "orion.db")
DIRS = [
    "sources", "facts", "relations", "rules", "schemas",
    "working", "working/audit", "working/brain", "episodic",
    "matrix", "vault", "archive"
]

def normalize_path(p: str) -> str:
    return p.replace(chr(92), '/')

_DB_INITIALIZED = False
_CACHED_NANOBRAIN = None

def get_cached_nanobrain():
    global _CACHED_NANOBRAIN
    if _CACHED_NANOBRAIN is None:
        try:
            import sys
            script_dir = os.path.dirname(os.path.abspath(__file__))
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
            from brain import NanoBrain
            _CACHED_NANOBRAIN = NanoBrain()
        except Exception:
            _CACHED_NANOBRAIN = False
    return _CACHED_NANOBRAIN if _CACHED_NANOBRAIN is not False else None


def get_db():
    global _DB_INITIALIZED
    if not _DB_INITIALIZED:
        init_db()
        _DB_INITIALIZED = True
    return connect_sqlite(DB_PATH)

def init_db():
    conn = connect_sqlite(DB_PATH)
    c = conn.cursor()
    c.execute('PRAGMA temp_store=MEMORY;')
    c.execute('PRAGMA mmap_size=67108864;') # 64MB mmap
    c.execute('PRAGMA cache_size=-16000;') # 16MB buffer pinning (hybrid RAM graph)
    c.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            path TEXT PRIMARY KEY,
            sha256 TEXT,
            category TEXT,
            pillar TEXT,
            updated TEXT,
            access_count INTEGER DEFAULT 0,
            last_accessed TEXT,
            importance REAL DEFAULT 1.0
        )
    ''')
    c.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
            path,
            content,
            tokenize='porter'
        )
    ''')
    # 2. Canonical Entities and Relations schemas (OrionGraphStore)
    c.execute('''
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            description TEXT DEFAULT '',
            source_path TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    c.execute('''
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
        )
    ''')

    # Unify nodes & edges into canonical entities & relations with backward-compatible SQL VIEWs
    try:
        c.execute("SELECT type FROM sqlite_master WHERE name='nodes'")
        n_type = c.fetchone()
        if n_type and n_type[0] == 'table':
            c.execute("INSERT OR IGNORE INTO entities (name, type, description, source_path) SELECT name, type, name, source_path FROM nodes")
            c.execute("DROP TABLE nodes")
    except Exception as _e:
        _log_telemetry(_e, 'init_db:drop_nodes_table')

    c.execute('''
        CREATE VIEW IF NOT EXISTS nodes AS
        SELECT name AS id, type, name, source_path FROM entities;
    ''')

    try:
        c.execute("SELECT type FROM sqlite_master WHERE name='edges'")
        e_type = c.fetchone()
        if e_type and e_type[0] == 'table':
            c.execute("INSERT OR IGNORE INTO relations (subject_id, predicate, object_id, weight, source_path) SELECT source_id, relation, target_id, confidence, source_path FROM edges")
            c.execute("DROP TABLE edges")
    except Exception as _e:
        _log_telemetry(_e, 'init_db:drop_edges_table')

    c.execute('''
        CREATE VIEW IF NOT EXISTS edges AS
        SELECT subject_id AS source_id, object_id AS target_id, predicate AS relation, weight AS confidence, source_path FROM relations;
    ''')

    # Triggers for backward compatibility on views
    c.execute('''
        CREATE TRIGGER IF NOT EXISTS edges_view_insert INSTEAD OF INSERT ON edges BEGIN
            INSERT OR IGNORE INTO entities (name, type, description, source_path) VALUES (NEW.source_id, 'Entity', NEW.source_id, NEW.source_path);
            INSERT OR IGNORE INTO entities (name, type, description, source_path) VALUES (NEW.target_id, 'Entity', NEW.target_id, NEW.source_path);
            INSERT INTO relations (subject_id, predicate, object_id, weight, source_path)
            VALUES (NEW.source_id, NEW.relation, NEW.target_id, NEW.confidence, NEW.source_path)
            ON CONFLICT(subject_id, predicate, object_id) DO UPDATE SET
                weight = excluded.weight,
                source_path = excluded.source_path;
        END;
    ''')
    c.execute('''
        CREATE TRIGGER IF NOT EXISTS edges_view_update INSTEAD OF UPDATE ON edges BEGIN
            UPDATE relations
            SET weight = NEW.confidence, source_path = NEW.source_path
            WHERE subject_id = OLD.source_id AND predicate = OLD.relation AND object_id = OLD.target_id;
        END;
    ''')
    c.execute('''
        CREATE TRIGGER IF NOT EXISTS edges_view_delete INSTEAD OF DELETE ON edges BEGIN
            DELETE FROM relations
            WHERE subject_id = OLD.source_id AND predicate = OLD.relation AND object_id = OLD.target_id;
        END;
    ''')
    c.execute('''
        CREATE TRIGGER IF NOT EXISTS nodes_view_insert INSTEAD OF INSERT ON nodes BEGIN
            INSERT OR IGNORE INTO entities (name, type, description, source_path)
            VALUES (NEW.name, NEW.type, NEW.name, NEW.source_path);
        END;
    ''')
    c.execute('''
        CREATE TRIGGER IF NOT EXISTS nodes_view_delete INSTEAD OF DELETE ON nodes BEGIN
            DELETE FROM entities WHERE name = OLD.name OR name = OLD.id;
        END;
    ''')
    
    # Defensive column auto-migration for legacy databases
    try:
        c.execute("PRAGMA table_info(pages);")
        existing_page_cols = {row[1] for row in c.fetchall()}
        cols_to_add = {
            "access_count": "ALTER TABLE pages ADD COLUMN access_count INTEGER DEFAULT 0;",
            "last_accessed": "ALTER TABLE pages ADD COLUMN last_accessed TEXT;",
            "importance": "ALTER TABLE pages ADD COLUMN importance REAL DEFAULT 1.0;",
            "category": "ALTER TABLE pages ADD COLUMN category TEXT;",
            "pillar": "ALTER TABLE pages ADD COLUMN pillar TEXT;",
            "updated": "ALTER TABLE pages ADD COLUMN updated TEXT;",
        }
        for col, stmt in cols_to_add.items():
            if col not in existing_page_cols:
                c.execute(stmt)
    except Exception as _e:
        _log_telemetry(_e, 'orion_ops.py:146')

    # Drop legacy duplicate page_embeddings table
    c.execute("DROP TABLE IF EXISTS page_embeddings;")
    
    # [DORMANT SCAFFOLDING] 
    # The 'telemetry' and 'contradictions' (created in contradict.py) tables are dormant structural schemas. 
    # They are provided as foundations awaiting activation by specific downstream SaaS projects.
    c.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            exit_code INTEGER,
            context_load INTEGER
        )
    ''')
    c.execute('''
                CREATE TABLE IF NOT EXISTS contradictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_a_source TEXT,
            edge_a_target TEXT,
            edge_a_relation TEXT,
            edge_b_source TEXT,
            edge_b_target TEXT,
            edge_b_relation TEXT,
            resolution TEXT DEFAULT 'unresolved',
            evidence TEXT DEFAULT '',
            detected_at TEXT DEFAULT (datetime('now')),
            resolved_at TEXT
        );''')
    c.execute('''CREATE TABLE IF NOT EXISTS archival_vectors (
            id TEXT PRIMARY KEY,
            content TEXT,
            embedding BLOB,
            created_at REAL
        )
    ''')

    conn.commit()
    conn.close()

def init_companion_dbs():
    """Initialize all runtime schemas in canonical `.orion/orion.db`."""
    try:
        from core.db import SovereignTracer
        from commands.state_machine import StateGraph
        from core.orion_graph import OrionGraphStore
        from core.memory import RecallMemoryManager, MultiLayerMemoryManager

        SovereignTracer(DB_PATH).conn.close()
        StateGraph(db_path=DB_PATH).close()
        OrionGraphStore(DB_PATH).close()
        MultiLayerMemoryManager(DB_PATH).close()
        rm = RecallMemoryManager(DB_PATH)
        rm._init_turns(rm._get_connection())
        with RAGDiagnosticJudge(DB_PATH):
            pass
        with CorpusInformationCompactor(DB_PATH):
            pass
    except Exception as _e:
        _log_telemetry(_e, 'orion_ops:init_companion_dbs')

def record_db_telemetry(event_type: str, exit_code: int = 0, context_load: int = 0):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO telemetry (timestamp, event_type, exit_code, context_load)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().isoformat(), event_type, exit_code, context_load))
    c.execute('DELETE FROM telemetry WHERE id NOT IN (SELECT id FROM telemetry ORDER BY id DESC LIMIT 1000)')
    conn.commit()
    conn.close()


RAW_EXTS = [".dart", ".ts", ".js", ".py", ".go", ".rs", ".swift", ".java"]
try:
    ecosystems_dir = os.path.join(WORKSPACE_DIR, ".agents", "canons", "ecosystems")
    if os.path.exists(ecosystems_dir):
        import glob
        for eco_file in glob.glob(os.path.join(ecosystems_dir, "*", "ecosystem.json")):
            with open(eco_file, "r", encoding="utf-8") as f:
                eco_data = json.load(f)
                if "extensions" in eco_data:
                    # Append unique extensions
                    for ext in eco_data["extensions"]:
                        if ext not in RAW_EXTS:
                            RAW_EXTS.append(ext)
except Exception as _e:
    _log_telemetry(_e, 'orion_ops.py:223')

# === BOOTSTRAP ===
def bootstrap():
    if not os.path.exists(ORION_DIR):
        os.makedirs(ORION_DIR)
        
    for d in DIRS:
        path = os.path.join(ORION_DIR, d)
        if not os.path.exists(path):
            os.makedirs(path)
            
    # Initialize SQLite DB for Orion Graph & companion databases
    init_db()
    init_companion_dbs()
            
    # Create empty index and log
    for f in ["index.md", "log.md"]:
        path = os.path.join(ORION_DIR, f)
        if not os.path.exists(path):
            atomic_write_text(path, f"# {f.split('.')[0].capitalize()}\n")
                
    # Copy template if available (mock implementation)
    schema_path = os.path.join(ORION_DIR, "_schema.md")
    if not os.path.exists(schema_path):
        atomic_write_text(schema_path, "# Orion Schema\nAutonomy Level: balanced\n")
            
    # Seed essential files
    session_history_path = os.path.join(ORION_DIR, "episodic", "session_history.md")
    if not os.path.exists(session_history_path):
        atomic_write_text(session_history_path, "# Session History\n\n*Chronological log of agent sessions and key architectural decisions.*\n")
            
    handoff_path = os.path.join(ORION_DIR, "working", "handoff.md")
    if not os.path.exists(handoff_path):
        atomic_write_text(handoff_path, "# SESSION HANDOFF\n\n## 1. Resume Point\n\n## 2. Technical State\n\n## 3. Metrics, Cost & Token Savings\n\n## 4. Anti-Goals\n")

    # Seed Omni-Buffer context.json
    context_json_path = os.path.join(ORION_DIR, "working", "context.json")
    if not os.path.exists(context_json_path):
        buffer_state = {
            "active_document": "",
            "cursor_line": "1",
            "evolution_overdue": False,
            "drift_warnings": []
        }
        atomic_write_text(context_json_path, json.dumps(buffer_state, indent=4))
            
    # Simple manifest
    manifest_path = os.path.join(ORION_DIR, "_manifest.json")
    if not os.path.exists(manifest_path):
        manifest = {
            "scanned_at": datetime.now().isoformat(),
            "status": "bootstrapped",
            "layers": {"infrastructure": [], "context": [], "project_docs": [], "raw": []}
        }
        atomic_write_text(manifest_path, json.dumps(manifest, indent=2))

    print("Orion bootstrapped successfully in .orion/")


# === INGEST ===
def compute_sha256(content: bytes) -> str:
    normalized = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest()

def parse_frontmatter(content: str) -> dict:
    from core.scanner import parse_frontmatter as _parse_fm
    return _parse_fm(content)[0]

def classify_file(filepath: str, content: str) -> tuple:
    filepath_normalized = filepath.replace("\\", "/")
    
    category = "project-doc"
    confidence = "authoritative"
    pillar = "cross-cutting"
    
    _, ext = os.path.splitext(filepath_normalized.lower())
    if ext in RAW_EXTS:
        category = "raw-source"
        confidence = "raw"
        pillar = "tech"
        return category, confidence, pillar
    elif ext in [".yaml", ".json"]:
        category = "config"
        confidence = "authoritative"
        pillar = "infrastructure"
        return category, confidence, pillar
        
    if "rules/" in filepath_normalized:
        category = "rule"
        confidence = "authoritative"
        pillar = "infrastructure"
        if "flutter" in filepath_normalized:
            pillar = "tech"
    elif "skills/" in filepath_normalized:
        category = "skill"
        confidence = "authoritative"
        pillar = "tech"
    elif "workflows/" in filepath_normalized:
        category = "workflow"
        confidence = "authoritative"
        pillar = "infrastructure"
    elif "canons/" in filepath_normalized:
        category = "canon"
        confidence = "canonical"
        pillar = "cross-cutting"
    elif "context/" in filepath_normalized or filepath_normalized.endswith("CONTEXT.md"):
        category = "context-master" if filepath_normalized.endswith("CONTEXT.md") else "context-pillar"
        confidence = "authoritative"
        pillar = "tech"
        
    return category, confidence, pillar

def prune_orphans() -> int:
    if not os.path.exists(MANIFEST_PATH):
        return 0
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
            manifest = json.load(mf)
            
        pruned_count = 0
        db_conn = None
        try:
            db_conn = get_db()
            db_c = db_conn.cursor()
        except Exception as _e:
            _log_telemetry(_e, 'orion_ops.py:353')

        for layer in list(manifest.get("layers", {}).keys()):
            valid_entries = []
            for entry in manifest["layers"][layer]:
                original_path = entry.get("filepath")
                orion_file = entry.get("orion_file")
                
                # Cek jika file asli masih ada di sistem (kecuali jika pathnya memang dihapus)
                if original_path and not os.path.exists(original_path):
                    pruned_count += 1
                    print(f"[PRUNE] Pruning orphan from orion: {original_path}")
                    if orion_file:
                        full_wiki_path = os.path.join(ORION_DIR, orion_file.replace("/", os.sep))
                        if os.path.exists(full_wiki_path):
                            os.remove(full_wiki_path)
                        
                        if db_conn:
                            try:
                                norm_path = normalize_path(full_wiki_path)
                                rel_orig = os.path.relpath(original_path).replace("\\", "/") if original_path else ""
                                norm_orig = normalize_path(original_path) if original_path else ""
                                paths_to_delete = list({p for p in (full_wiki_path, norm_path, original_path, rel_orig, norm_orig) if p})
                                placeholders = ",".join("?" for _ in paths_to_delete)
                                db_c.execute(f'DELETE FROM edges WHERE source_id IN (SELECT id FROM nodes WHERE source_path IN ({placeholders}))', paths_to_delete)
                                db_c.execute(f'DELETE FROM nodes WHERE source_path IN ({placeholders})', paths_to_delete)
                                db_c.execute(f'DELETE FROM pages WHERE path IN ({placeholders})', paths_to_delete)
                                db_c.execute(f'DELETE FROM pages_fts WHERE path IN ({placeholders})', paths_to_delete)
                                db_c.execute(f'DELETE FROM edges WHERE source_id IN ({placeholders})', paths_to_delete)
                            except Exception as e:
                                print(f"DB cleanup error for {original_path}: {e}")
                else:
                    valid_entries.append(entry)
            manifest["layers"][layer] = valid_entries
            
        if db_conn:
            db_conn.commit()
            db_conn.close()
            
        if pruned_count > 0:
            atomic_write_text(MANIFEST_PATH, json.dumps(manifest, indent=2))
        return pruned_count
    except Exception as e:
        print(f"Failed during orphan pruning: {e}")
        return 0

def ingest_file(filepath: str, autonomy_level="balanced", manifest=None, log_lines=None, conn=None, embed: bool = False, commit: bool = True) -> bool:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False

    basename = os.path.basename(filepath)
    # Exclude non-knowledge artifacts: tests, sidecars, backups
    if basename.startswith("test_") or basename.endswith("_test.py") or basename.endswith(".test.py") or basename.endswith(".sidecar.json") or basename.endswith(".orion_mut_bak"):
        return False
        
    own_conn = False
    if conn is None:
        conn = get_db()
        own_conn = True

    try:
        with open(filepath, "rb") as f:
            raw_bytes = f.read()
        sha = compute_sha256(raw_bytes)
        
        try:
            content_str = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content_str = raw_bytes.decode("latin-1")
            
        existing_frontmatter = parse_frontmatter(content_str)
        category, confidence, pillar = classify_file(filepath, content_str)
        
        name, ext = os.path.splitext(basename)
        
        target_path = os.path.relpath(filepath).replace("\\", "/")
        
        is_updated = True
        action_type = "NEW"
        
        c = conn.cursor()
        c.execute('SELECT sha256 FROM pages WHERE path = ?', (target_path,))
        row = c.fetchone()
        if row:
            if row[0] == sha:
                print(f"Skipping {filepath} (Already matches hash)")
                return False
            action_type = "EXTEND"

        # Autonomy Matrix Guard
        if autonomy_level == "strict":
            c.execute(
                "SELECT COUNT(*) FROM contradictions WHERE (edge_a_source = ? OR edge_b_source = ?) AND resolution = 'unresolved'",
                (target_path, target_path),
            )
            unresolved = c.fetchone()[0]
            if unresolved > 0:
                print(f"[STRICT AUTONOMY] Ingest rejected for {target_path}: {unresolved} unresolved contradiction(s) found.")
                return False
            
        updated_date = datetime.now().strftime("%Y-%m-%d")
        created_date = existing_frontmatter.get("created", updated_date)
        
        wiki_fm = {
            "type": "source-summary",
            "source-category": category,
            "sources": [os.path.relpath(filepath).replace("\\", "/")],
            "source_sha256": sha,
            "pillar": existing_frontmatter.get("pillar", pillar),
            "confidence": confidence,
            "created": created_date,
            "updated": updated_date
        }
        
        fm_lines = ["---"]
        for k, v in wiki_fm.items():
            if isinstance(v, list):
                fm_lines.append(f"{k}: [{', '.join(v)}]")
            else:
                fm_lines.append(f"{k}: {v}")
        fm_lines.append("---")
        fm_text = "\n".join(fm_lines)
        
        pointer_body = f"\n> **Original Source**: `{filepath}`\n"
        
        if ext.lower() in RAW_EXTS:
            try:
                # Add agents/scripts to sys.path to find utils
                import sys
                script_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                from core.scanner import generate_ast_summary
                ast_summary = generate_ast_summary(filepath, content_str)
                skeleton_lines = ast_summary.split("\n") if ast_summary else ["[AST Skipping: Not structurally parsed]"]
                triplets = []
                
                # Auto-extract basic structural triplets
                import re
                file_basename = os.path.basename(filepath)
                if ext.lower() == ".py":
                    try:
                        from core.scanner import extract_python_edges_ast
                        triplets.extend(extract_python_edges_ast(content_str, file_basename))
                    except ImportError:
                        pass
                elif ext.lower() in [".js", ".ts", ".dart"]:
                    for match in re.finditer(r'^\s*import\s+.*?(?:from\s+)?[\'"](.*?)[\'"]', content_str, re.MULTILINE):
                        triplets.append((file_basename, "imports", match.group(1)))
                    for match in re.finditer(r'^\s*class\s+([a-zA-Z0-9_]+)(?:\s+extends\s+([a-zA-Z0-9_]+))?', content_str, re.MULTILINE):
                        cls_name = match.group(1)
                        triplets.append((file_basename, "defines", cls_name))
                        if match.group(2):
                            triplets.append((cls_name, "inherits", match.group(2)))
            except Exception as e:
                skeleton_lines = [f"Error generating AST summary: {e}"]
                triplets = []
            
            skeleton_text = "\n".join(skeleton_lines) if skeleton_lines else "*No class or function signatures found.*"
            pointer_body += f"\n###  Structural Skeleton\n\n```\n{skeleton_text}\n```\n"
        elif ext.lower() in [".yaml", ".json"]:
            deps_list = []
            metadata = {}
            if ext.lower() == ".json":
                try:
                    data = json.loads(content_str)
                    metadata["name"] = data.get("name", "Unknown")
                    metadata["version"] = data.get("version", "Unknown")
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})
                    for dep, ver in deps.items():
                        deps_list.append(f"- `{dep}`: `{ver}`")
                    for dep, ver in dev_deps.items():
                        deps_list.append(f"- `{dep}`: `{ver}` (dev)")
                except Exception as _e:
                    _log_telemetry(_e, 'orion_ops.py:513')
            elif ext.lower() == ".yaml":
                try:
                    in_deps = False
                    in_dev_deps = False
                    for line in content_str.splitlines():
                        line_stripped = line.strip()
                        if line_stripped.startswith("name:"):
                            metadata["name"] = line_stripped.split(":", 1)[1].strip()
                        elif line_stripped.startswith("version:"):
                            metadata["version"] = line_stripped.split(":", 1)[1].strip()
                        elif line_stripped == "dependencies:":
                            in_deps = True
                            in_dev_deps = False
                        elif line_stripped == "dev_dependencies:":
                            in_deps = False
                            in_dev_deps = True
                        elif line.startswith("  ") and not line.startswith("    "):
                            if ":" in line_stripped:
                                k, v = line_stripped.split(":", 1)
                                k = k.strip()
                                v = v.strip()
                                if in_deps:
                                    deps_list.append(f"- `{k}`: `{v}`")
                                elif in_dev_deps:
                                    deps_list.append(f"- `{k}`: `{v}` (dev)")
                        elif not line.startswith(" ") and line_stripped:
                            in_deps = False
                            in_dev_deps = False
                except Exception as _e:
                    _log_telemetry(_e, 'orion_ops.py:543')
            
            meta_text = "\n".join(f"- **{k.capitalize()}**: `{v}`" for k, v in metadata.items())
            deps_text = "\n".join(deps_list) if deps_list else "*No dependencies parsed.*"
            pointer_body += f"\n###  Metadata\n{meta_text}\n\n###  Dependencies\n{deps_text}\n"
        else:
            pointer_body += f"> *Content body excluded from Graph to prevent storage bloat.*\n"
        
        log_entry = f"- [{updated_date}] [{action_type}] Ingested {filepath}\n"
        if log_lines is not None:
            log_lines.append(log_entry)
        else:
            with open(LOG_PATH, "a", encoding="utf-8") as lf:
                lf.write(log_entry)
                
            with open(LOG_PATH, "r", encoding="utf-8") as lf:
                lines = lf.readlines()
            if len(lines) > 500:
                atomic_write_text(LOG_PATH, "".join(lines[-500:]))
            
        # Orion SQLite Sync
        try:
            try:
                c = conn.cursor()
                
                c.execute('''
                    INSERT INTO pages (path, sha256, category, pillar, updated) 
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(path) DO UPDATE SET
                        sha256 = excluded.sha256,
                        category = excluded.category,
                        pillar = excluded.pillar,
                        updated = excluded.updated
                ''', (target_path, sha, category, existing_frontmatter.get("pillar", pillar), updated_date))
                
                fts_body = (fm_text + "\n\n" + content_str) if ext.lower() == ".md" else (fm_text + "\n" + pointer_body)
                c.execute('DELETE FROM pages_fts WHERE path = ?', (target_path,))
                c.execute('''
                    INSERT INTO pages_fts (path, content) VALUES (?, ?)
                ''', (target_path, fts_body))
                
                c.execute('DELETE FROM edges WHERE source_id = ?', (target_path,))
                
                # --- SQL-Backed WikiLinks Extraction ---
                if ext.lower() == '.md':
                    import re
                    text_no_code = re.sub(r'```.*?```', '', content_str, flags=re.DOTALL)
                    pattern = r'\[\[(.*?)\]\]'
                    wiki_links = re.findall(pattern, text_no_code)
                    if wiki_links:
                        c.execute('''
                            INSERT OR IGNORE INTO nodes (id, type, name, source_path) 
                            VALUES (?, ?, ?, ?)
                        ''', (target_path, 'File', os.path.basename(target_path), target_path))
                        for link in wiki_links:
                            parts = link.split('|')
                            name = parts[0].strip()
                            relation = parts[1].strip() if len(parts) > 1 else "mentions"
                            c.execute('''
                                INSERT OR IGNORE INTO nodes (id, type, name, source_path) 
                                VALUES (?, ?, ?, ?)
                            ''', (name, 'WikiNode', name, target_path))
                            c.execute('''
                                INSERT OR IGNORE INTO edges (source_id, target_id, relation, confidence, source_path)
                                VALUES (?, ?, ?, 1.0, ?)
                            ''', (target_path, name, relation, target_path))
                # --- Structural Triplets ---
                if ext.lower() in RAW_EXTS and 'triplets' in locals() and triplets:
                    c.execute('''
                        INSERT OR IGNORE INTO nodes (id, type, name, source_path) 
                        VALUES (?, ?, ?, ?)
                    ''', (target_path, 'File', os.path.basename(target_path), target_path))
                    for caller, rel, callee in triplets:
                        c.execute('''
                            INSERT OR IGNORE INTO nodes (id, type, name, source_path) 
                            VALUES (?, ?, ?, ?)
                        ''', (callee, 'AST_Element', callee, target_path))
                        c.execute('''
                            INSERT OR IGNORE INTO edges (source_id, target_id, relation, confidence, source_path)
                            VALUES (?, ?, ?, 1.0, ?)
                        ''', (target_path, callee, rel, target_path))
                
                # Vector Embedding (Graceful Degradation: EMBED capability, opt-in for bulk ingest)
                if embed:
                    try:
                        nb = get_cached_nanobrain()
                        if nb and nb.ping(capability="EMBED"):
                            embed_text = (fm_text + "\n\n" + content_str)[:3000] if ext.lower() == ".md" else (fm_text + "\n" + pointer_body)[:2000]
                            emb = nb.embed(embed_text)
                            if emb:
                                try:
                                    import time
                                    c.execute('''
                                        INSERT INTO archival_vectors (id, content, embedding, created_at)
                                        VALUES (?, ?, ?, ?)
                                        ON CONFLICT(id) DO UPDATE SET content = excluded.content, embedding = excluded.embedding, created_at = excluded.created_at
                                    ''', (target_path, embed_text[:500], pack_vector(emb), time.time()))
                                except Exception as _ave:
                                    _log_telemetry(_ave, 'orion_ops.py:archival_vectors')
                    except Exception as _e:
                        # Silently degrade to pure lexical FTS5 when local embedding engine is unavailable
                        _log_telemetry(_e, 'orion_ops.py:638')

                if commit:
                    conn.commit()
            finally:
                if own_conn:
                    conn.close()
        except Exception as db_e:
            print(f"Warning: Failed to sync to orion.db: {db_e}")
            
        is_local_manifest = manifest is None
        if is_local_manifest:
            manifest = {}
            if os.path.exists(MANIFEST_PATH):
                try:
                    with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
                        manifest = json.load(mf)
                except Exception as e:
                    print(f"Warning: Failed to load manifest: {e}")
                    
        if "layers" not in manifest:
            manifest["layers"] = {"infrastructure": [], "context": [], "project_docs": [], "raw": []}
            
        layer_key = "infrastructure"
        if category in ["context-master", "context-pillar", "memory", "handoff"]:
            layer_key = "context"
        elif category in ["project-doc"]:
            layer_key = "project_docs"
        elif category in ["raw-source"]:
            layer_key = "raw"
            
        manifest_entry = {
            "filepath": filepath.replace("\\", "/"),
            "orion_file": filepath.replace("\\", "/"),
            "sha256": sha,
            "category": category,
            "updated": updated_date
        }
        
        manifest["layers"][layer_key] = [e for e in manifest["layers"][layer_key] if e["filepath"] != manifest_entry["filepath"]]
        manifest["layers"][layer_key].append(manifest_entry)
        manifest["status"] = "active"
        manifest["scanned_at"] = datetime.now().isoformat()
        
        if is_local_manifest:
            atomic_write_text(MANIFEST_PATH, json.dumps(manifest, indent=2))
            
        print(f"Ingested: {filepath} -> {target_path} [{action_type}]")
        return target_path
    except Exception as e:
        print(f"Failed to ingest {filepath}: {e}")
        return None

def rebuild_index():
    if not os.path.exists(MANIFEST_PATH):
        return
        
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
            manifest = json.load(mf)
            
        index_lines = [
            "# Orion Index",
            f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "##  Infrastructure Layer"
        ]
        
        infra = manifest.get("layers", {}).get("infrastructure", [])
        if infra:
            for item in sorted(infra, key=lambda x: x["filepath"]):
                index_lines.append(f"- [{item['filepath']}]({item['orion_file']}) (Type: `{item['category']}`)")
        else:
            index_lines.append("- *No files ingested yet*")
            
        index_lines.extend([
            "",
            "##  Context Layer"
        ])
        
        context = manifest.get("layers", {}).get("context", [])
        if context:
            for item in sorted(context, key=lambda x: x["filepath"]):
                index_lines.append(f"- [{item['filepath']}]({item['orion_file']}) (Type: `{item['category']}`)")
        else:
            index_lines.append("- *No files ingested yet*")
            
        index_lines.extend([
            "",
            "##  Project Docs Layer"
        ])
        
        docs = manifest.get("layers", {}).get("project_docs", [])
        if docs:
            for item in sorted(docs, key=lambda x: x["filepath"]):
                index_lines.append(f"- [{item['filepath']}]({item['orion_file']}) (Type: `{item['category']}`)")
        else:
            index_lines.append("- *No files ingested yet*")
            
        index_lines.extend([
            "",
            "##  Raw/Source Layer"
        ])
        
        raw_files = manifest.get("layers", {}).get("raw", [])
        if raw_files:
            for item in sorted(raw_files, key=lambda x: x["filepath"]):
                index_lines.append(f"- [{item['filepath']}]({item['orion_file']}) (Type: `{item['category']}`)")
        else:
            index_lines.append("- *No source files ingested yet*")
            
        atomic_write_text(INDEX_PATH, "\n".join(index_lines) + "\n")
            
        print("Orion Index rebuilt successfully.")
    except Exception as e:
        print(f"Failed to rebuild index: {e}")


def get_smart_ignore_dirs(target_path):
    ignores = {".git", ".orion", "__pycache__", "node_modules", "build", ".dart_tool", ".idea", ".vscode", ".gradle", "target", "venv", "env", "archive", "docs", "templates", "tests", "evals", "scratch", ".scratch", "test"}
    if os.path.isfile(target_path):
        target_path = os.path.dirname(target_path)
    curr = os.path.abspath(target_path)
    while curr:
        g = os.path.join(curr, ".gitignore")
        if os.path.exists(g):
            try:
                with open(g, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "*" in line or "?" in line:
                                continue
                            if "/" not in line:
                                ignores.add(line)
                            elif line.endswith("/") and line.count("/") == 1:
                                ignores.add(line.replace("/", ""))
                            elif line.startswith("/") and line.endswith("/") and line.count("/") == 2:
                                ignores.add(line.replace("/", ""))
            except Exception as _e:
                _log_telemetry(_e, 'orion_ops.py:779')
            break
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return ignores

def ingest_main(paths, autonomy, embed=False):
    lock_file = os.path.join(WORKSPACE_DIR, '.orion', 'working', '.auto_sync_lock')
    shared_conn = get_db()
    try:
        pruned = prune_orphans()
            
        ingested_files = []
        valid_exts = tuple([".md"] + RAW_EXTS + [".yaml", ".json"])
        manifest = {}
        if os.path.exists(MANIFEST_PATH):
            try:
                with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
                    manifest = json.load(mf)
            except Exception as _e:
                _log_telemetry(_e, 'orion_ops.py:798')
                
        log_lines = []
        if os.path.exists(LOG_PATH):
            try:
                with open(LOG_PATH, "r", encoding="utf-8") as lf:
                    log_lines = lf.readlines()
            except Exception as _e:
                _log_telemetry(_e, 'orion_ops.py:806')

        missing_paths = []
        for path in paths:
            ignore_dirs = get_smart_ignore_dirs(path)
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    dirs[:] = [d for d in dirs if d not in ignore_dirs]
                        
                    for f in files:
                        if f.lower().endswith(valid_exts):
                            full_path = os.path.join(root, f)
                            target_path = ingest_file(full_path, autonomy, manifest=manifest, log_lines=log_lines, conn=shared_conn, embed=embed, commit=False)
                            if target_path:
                                ingested_files.append((full_path, target_path))
            elif os.path.isfile(path):
                target_path = ingest_file(path, autonomy, manifest=manifest, log_lines=log_lines, conn=shared_conn, embed=embed, commit=False)
                if target_path:
                    ingested_files.append((path, target_path))
            else:
                import glob
                matched = glob.glob(path, recursive=True)
                if matched:
                    for g in matched:
                        if os.path.isfile(g) and g.lower().endswith(valid_exts):
                            if '.orion' not in g.replace('\\', '/').split('/'):
                                target_path = ingest_file(g, autonomy, manifest=manifest, log_lines=log_lines, conn=shared_conn, embed=embed, commit=False)
                                if target_path:
                                    ingested_files.append((g, target_path))
                elif not any(ch in path for ch in ['*', '?', '[']):
                    print(f"[ERROR] Target path not found: {path}")
                    missing_paths.append(path)

        if missing_paths:
            print(f"\n[FAIL] Ingestion aborted. {len(missing_paths)} requested target path(s) not found.")
            sys.exit(1)

        if shared_conn:
            try:
                shared_conn.commit()
            except Exception as _ce:
                _log_telemetry(_ce, "brain.py:batch_commit")
                            
        if len(ingested_files) > 0:
            atomic_write_text(MANIFEST_PATH, json.dumps(manifest, indent=2))
            atomic_write_text(LOG_PATH, "".join(log_lines[-500:]))
        elif os.path.exists(MANIFEST_PATH):
            try:
                os.utime(MANIFEST_PATH, None)
            except Exception as _e:
                _log_telemetry(_e, "brain.py:utime_manifest")

        if len(ingested_files) > 0 or pruned > 0:
            _recompute_canonical_communities()
            rebuild_index()
            record_db_telemetry("ingest", exit_code=0, context_load=len(ingested_files))
            print(f"\nBatch execution complete. Processed: {len(ingested_files)} | Pruned: {pruned}")
            
            # --- AUTO-COMPILE HOOK ---
            print("\n[AUTO-COMPILE] Triggering Matrix Compilation for zero-drift...")
            try:
                compile_all()
                compile_skill_routes()
            except Exception as e:
                print(f"[ERROR] Failed to auto-compile rules: {e}")
                
            # Note: linkify is decoupled from ingest to keep ingestion strictly read-only on source markdown.
            # Run `python .agents/scripts/orion.py linkify` manually if source wikilinking is explicitly desired.
                
            print(f"\n[TRIPLET_REQUEST] {len(ingested_files)} files need graph triplet extraction.")
            print("⚡ RECOMMENDED TIER: BUDGET — Ingest/deploy operations are batch tasks. Switch to Budget model.")
            print("Files:")
            for i, (orig, target) in enumerate(ingested_files, 1):
                rel_target = os.path.relpath(target, WORKSPACE_DIR).replace("\\", "/")
                rel_orig = os.path.relpath(orig, WORKSPACE_DIR).replace("\\", "/")
                print(f"{i}. {rel_target} (source: {rel_orig})")
                print("[ACTION] Read each source file, extract 3-5 triplets and format as JSON list of dicts with keys: `s` (subject), `p` (predicate), `o` (object), `src` (source path).")
                print("then run: python .agents/scripts/orion.py orion_ops inject_triplets '<json>'")
                
        else:
            print("No new or updated markdown files found to ingest. Graph is up to date.")
            print("⚡ RECOMMENDED TIER: BUDGET — Ingest/deploy operations are batch tasks. Switch to Budget model.")
    finally:
        if shared_conn:
            try:
                shared_conn.close()
            except Exception as _e:
                _log_telemetry(_e, "brain.py:shared_conn_close")
        if lock_file:
            try:
                atomic_write_text(lock_file, f"{time.time()}:0")
            except Exception as _e:
                _log_telemetry(_e, "brain.py:lock_cooldown_set")

# === RESOLVER ===
def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        return None
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def find_target_file(query):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT path FROM pages WHERE path LIKE ? ORDER BY length(path) ASC, path ASC', (f'%{query}%',))
        row = c.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception as e:
        import sys
        print(f"[DEBUG DB] find_target_file: {e}", file=sys.stderr)
    return None

def extract_links(content):
    # Matches [[Page Name]] or [[Page Name|relation]]
    pattern = r'\[\[(.*?)\]\]'
    links = re.findall(pattern, content)
    parsed_links = []
    for link in links:
        parts = link.split('|')
        name = parts[0].strip()
        relation = parts[1].strip() if len(parts) > 1 else "mentions"
        parsed_links.append((name, relation))
    return parsed_links

def get_file_summary(filepath):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT category, pillar FROM pages WHERE path = ?', (filepath,))
        row = c.fetchone()
        conn.close()
        if row:
            summary = f"Category: {row[0]}"
            if len(row) > 1 and row[1]:
                summary += f" | Pillar: {row[1]}"
            return summary
    except Exception as e:
        import sys
        print(f"[DEBUG DB] get_file_summary: {e}", file=sys.stderr)
    return "Not ingested."

def find_backlinks(target_name):
    backlinks = []
    try:
        conn = get_db()
        c = conn.cursor()
        # Query canonical relations first
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='relations'")
        if c.fetchone():
            c.execute('SELECT subject_id FROM relations WHERE object_id = ? OR object_id = ?', (target_name, f"{target_name}.md"))
            for row in c.fetchall():
                basename = os.path.basename(row[0]).replace('.md', '')
                if basename not in backlinks and basename != target_name:
                    backlinks.append(basename)

        # Fallback/merge with legacy edges table if present
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='edges'")
        if c.fetchone():
            c.execute('SELECT source_id FROM edges WHERE target_id = ? OR target_id = ?', (target_name, f"{target_name}.md"))
            for row in c.fetchall():
                basename = os.path.basename(row[0]).replace('.md', '')
                if basename not in backlinks and basename != target_name:
                    backlinks.append(basename)
        conn.close()
    except Exception as e:
        _log_telemetry(e, "brain.py:find_backlinks")
    return backlinks

def resolve_wiki(query):
    target_file = find_target_file(query)
    if not target_file:
        print(f" [ORION] No nodes found matching '{query}'.")
        return

    print(f" [ORION GRAPH RESOLVER] Node: {os.path.basename(target_file)}")
    print("=" * 60)
    
    norm = target_file.replace("\\", "/")
    if "skills/" in norm:
        try:
            parts = norm.split("skills/")[1].split("/")
            if parts:
                sk_name = parts[0]
                from core.harness.engine import HarnessEngine
                HarnessEngine.record_skill_event(sk_name, "use")
        except Exception as _ste:
            _log_telemetry(_ste, "orion_ops:skill_telemetry")

    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    print(" CONTENT:")
    # Print up to 1500 chars to avoid overwhelming the LLM
    print(content[:1500] + ("\n...[TRUNCATED]" if len(content) > 1500 else ""))
    print("-" * 60)
    
    links = extract_links(content)
    if links:
        print(" FORWARD LINKS (Outbound):")
        for name, rel in links:
            linked_file = find_target_file(name)
            summary = get_file_summary(linked_file) if linked_file else "Not ingested."
            print(f"  -> [[{name}]] ({rel}) : {summary}")
    else:
        print(" FORWARD LINKS: None.")
        
    print("-" * 60)
    target_basename = os.path.basename(target_file).replace('.md', '')
    backlinks = find_backlinks(target_basename)
    
    if backlinks:
        print(" BACKLINKS (Inbound / Dependencies):")
        for bl in backlinks:
            bl_file = find_target_file(bl)
            summary = get_file_summary(bl_file) if bl_file else ""
            print(f"  <- [[{bl}]] : {summary}")
    else:
        print(" BACKLINKS: None.")
        
    print("=" * 60)
    print(" EXECUTION PATH (AST Edges):")
    try:
        conn = get_db()
        c = conn.cursor()
        
        # --- ACCESS COUNT INCREMENT ---
        try:
            c.execute("UPDATE pages SET access_count = IFNULL(access_count, 0) + 1, last_accessed = datetime('now') WHERE path = ?", (target_file,))
            conn.commit()
        except Exception as _e:
            _log_telemetry(_e, 'orion_ops.py:1000')
            
        # 1. File-to-file AST links
        c.execute('SELECT target_id, relation FROM edges WHERE source_id = ?', (target_file,))
        rows = c.fetchall()
        has_ast = False
        if rows:
            has_ast = True
            for target_id, relation in rows:
                print(f"  [{relation}] -> {target_id}")
        
        # 2. Graph Entity Triplets
        c.execute('SELECT id FROM nodes WHERE source_path = ?', (target_file,))
        entities = [r[0] for r in c.fetchall()]
        has_graph = False
        if entities:
            placeholders = ",".join("?" for _ in entities)
            c.execute(f'SELECT source_id, target_id, relation FROM edges WHERE source_id IN ({placeholders})', entities)
            edges_rows = c.fetchall()
            if edges_rows:
                print(" GRAPH TRIPLETS (Semantic Knowledge):")
                has_graph = True
                for ent, target_id, relation in edges_rows:
                    print(f"  ({ent}) -[{relation}]-> ({target_id})")
                        
        if not has_ast and not has_graph:
            print("  No downstream execution path or graph triplets found.")
            
        print("-" * 60)
        print(" RELATED NODES (via FTS5 BM25):")
        keywords = re.findall(r'\b[a-zA-Z0-9_]+\b', target_basename.lower())
        valid_kws = [kw for kw in keywords if len(kw) > 2]
        query_str = build_fts_query_or(valid_kws)
        if query_str:
            c.execute('SELECT path FROM pages_fts WHERE pages_fts MATCH ? AND path != ? ORDER BY rank LIMIT 3', (query_str, target_file))
            fts_rows = c.fetchall()
            if fts_rows:
                for row in fts_rows:
                    print(f"  ~ {os.path.basename(row[0])}")
            else:
                print("  No related nodes found via text match.")
        else:
            print("  No related nodes found via text match.")
            
        conn.close()
    except Exception as e:
        print(f"  [DB Error] {e}")
        
    print("=" * 60)
    print(" Graph Neighborhood Resolved. Use this context to answer the user.")

def inject_triplets(json_data):
    try:
        import sqlite3
        if os.path.exists(json_data):
            with open(json_data, "r", encoding="utf-8") as f:
                json_data = f.read()
        triplets = json.loads(json_data)
        if not triplets:
            print("[INFO] No triplets provided.")
            return
            
        conn = get_db()
        c = conn.cursor()
        
        # Collect unique sources to clear stale triplets first
        unique_sources = set()
        for t in triplets:
            src = t.get("src") or t.get("source_path") or t.get("file")
            if src:
                unique_sources.add(src)
                
        for src in unique_sources:
            try:
                # Delete only relations originating from this source
                c.execute('DELETE FROM relations WHERE source_path = ?', (src,))
            except Exception as e:
                print(f"[WARNING] Failed to clear stale relations for {src}: {e}")
        
        count = 0
        for t in triplets:
            sub = (t.get("s") or t.get("subject") or t.get("source") or "").strip()
            pred = (t.get("p") or t.get("predicate") or t.get("relation") or "").strip()
            obj = (t.get("o") or t.get("object") or t.get("target") or "").strip()
            src = (t.get("src") or t.get("source_path") or t.get("file") or "Unknown").strip()
            desc = (t.get("desc") or t.get("description") or t.get("context") or "").strip()
            if sub and pred and obj:
                c.execute(
                    "INSERT OR IGNORE INTO entities (name, type, description, source_path) VALUES (?, 'Entity', ?, ?)",
                    (sub, desc or sub, src),
                )
                if desc:
                    c.execute("UPDATE entities SET description = ? WHERE name = ? AND (description = '' OR description = name)", (desc, sub))
                c.execute(
                    "INSERT OR IGNORE INTO entities (name, type, description, source_path) VALUES (?, 'Entity', ?, ?)",
                    (obj, obj, src),
                )
                c.execute(
                    """
                    INSERT INTO relations (subject_id, predicate, object_id, weight, provenance, source_path)
                    VALUES (?, ?, ?, 1.0, 'EXTRACTED', ?)
                    ON CONFLICT(subject_id, predicate, object_id) DO UPDATE SET
                        weight = excluded.weight,
                        source_path = excluded.source_path
                    """,
                    (sub, pred, obj, src),
                )
                count += 1
                
        conn.commit()
        conn.close()
        if count == 0:
            print(f"[FAIL] 0 triplets injected from {len(triplets)} item(s). Check keys (expected 's'/'subject', 'p'/'predicate', 'o'/'object').")
            sys.exit(1)
        else:
            print(f"[SUCCESS] Injected {count} triplets into orion.db.")
        
        # --- IDE-1: Contradiction Engine (In-Process) ---
        try:
            detect_contradictions()
        except Exception as _ce:
            _log_telemetry(_ce, "orion_ops:contradict_detect")
            
    except Exception as e:
        print(f"[ERROR] Failed to inject triplets: {e}")
        sys.exit(1)




def _recompute_canonical_communities():
    """Batch recomputation of Louvain communities across canonical graph."""
    try:
        from core.orion_graph import OrionGraphStore
        store = OrionGraphStore(DB_PATH)
        try:
            store.compute_louvain_communities()
        finally:
            store.close()
    except Exception as exc:
        _log_telemetry(exc, "orion_ops.py:_recompute_canonical_communities")

# === CLI ===

def orion_ops_main(argv=None):
    parser = argparse.ArgumentParser(description="Orion Operations System")
    subparsers = parser.add_subparsers(dest="subcommand")

    parser_init = subparsers.add_parser("init", help="Bootstrap the orion directory structure")

    parser_ingest = subparsers.add_parser("ingest", help="Ingest files into the orion")
    parser_ingest.add_argument("paths", nargs="+", help="Paths or files to ingest")
    parser_ingest.add_argument("--autonomy", default="balanced", choices=["balanced", "high", "strict"])
    parser_ingest.add_argument("--embed", action="store_true", default=False, help="Generate vector embeddings via Ollama during ingestion")

    parser_resolve = subparsers.add_parser("resolve", help="Resolve orion nodes for context routing")
    parser_resolve.add_argument("node", help="Node name to resolve")

    parser_inject = subparsers.add_parser("inject_triplets", help="Inject graph triplets (JSON array)")
    parser_inject.add_argument("json_data", help="JSON string containing triplets")

    parser_gc = subparsers.add_parser("gc", help="Garbage collect stale caches and vacuum database")

    args = parser.parse_args(argv)

    if args.subcommand == "init":
        bootstrap()
    elif args.subcommand == "ingest":
        ingest_main(args.paths, args.autonomy, embed=args.embed)
    elif args.subcommand == "resolve":
        resolve_wiki(args.node)
    elif args.subcommand == "inject_triplets":
        inject_triplets(args.json_data)
    elif args.subcommand == "gc":
        gc_main()
    else:
        parser.print_help()
        return 1
    return 0


# ============================================================================
# SECTION 9: CONTEXT RETRIEVAL & BRAIN SYNC
# ============================================================================

def extract_keywords(text):
    stop_words = {'i', 'need', 'to', 'build', 'the', 'a', 'an', 'and', 'or', 'for', 'with', 'on', 'in', 'of', 'how', 'do', 'what', 'create', 'make', 'update', 'fix'}
    words = re.findall(r'\b[a-zA-Z0-9_]+\b', text.lower())
    base_keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Semantic Expansion via NanoBrain
    try:
        nb = NanoBrain()
        if nb.ping():
            sys_prompt = "You are a synonym generator. Output exactly 3 comma-separated technical synonyms for the intent. NO other text. Example: 'login' -> 'auth,authentication,session'"
            prompt = f"Intent: {text}\nSynonyms:"
            expansion = nb.generate(prompt, system=sys_prompt)
            if expansion:
                expanded_words = [w.strip().lower() for w in expansion.split(",") if w.strip()]
                # Filter out hallucinated sentences
                expanded_words = [w for w in expanded_words if len(w.split()) == 1 and w.isalpha()]
                return sorted(list(set(base_keywords + expanded_words)))
    except Exception as _e:
        _log_telemetry(_e, 'brain.py:600')
        
    return sorted(base_keywords)

def search_files(directory, keywords):
    matches = []
    if not os.path.exists(directory):
        return matches
    
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith('.md'):
                continue
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    score = sum(1 for kw in keywords if kw in content)
                    if score > 0:
                        if any(kw in file.lower() for kw in keywords):
                            score += 3
                        matches.append((score, filepath))
            except Exception as _e:
                _log_telemetry(_e, 'brain.py:623')
                
    matches.sort(reverse=True, key=lambda x: x[0])
    return [m[1] for m in matches[:3]]

def get_ast_block(filepath, tag_name):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(f'<{tag_name}>(.*?)</{tag_name}>', content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    except Exception as _e:
        _log_telemetry(_e, 'brain.py:636')
    return None

def _resolve_neighbor_target(cursor, target_id, workspace_dir, neighbor_files):
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

    # 2. Check SQLite pages index (e.g. wikilinks or symbol names mapping to markdown files)
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
        _log_telemetry(_e, 'brain.py:670')

def sync(intent, delta=False):
    print(f" BRAIN ENGINE ENGAGED: Syncing context for intent: '{intent}'")
    keywords = extract_keywords(intent)
    print(f" Extracted Tokens: {keywords}")
    
    agents_dir = get_agents_dir()
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
            _log_telemetry(_e, 'brain.py:698')

    if query_str and query_str in cache_data and not delta:
        print(f"  [CACHE HIT] Loaded semantic routes for '{query_str}' from RAM cache.")
        rules = cache_data[query_str]
    elif not delta:
        # Generate Intent Embedding
        query_embedding = None
        try:
            temp_nb = NanoBrain()
            if temp_nb.ping(capability="EMBED"):
                query_embedding = temp_nb.embed(intent)
                if query_embedding:
                    print("  [VECTOR SEARCH] Active. Embedding generated.")
        except Exception as _e:
            _log_telemetry(_e, 'brain.py:713')

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
                                    _log_telemetry(_ve, "brain.py:rrf_vec")
                            vec_hits.sort(key=lambda x: x[1], reverse=True)
                            for rank_idx, (path, _) in enumerate(vec_hits[:15], start=1):
                                scored_paths[path] = scored_paths.get(path, 0.0) + (1.2 / (RRF_K + rank_idx))
                    except Exception as _e:
                        _log_telemetry(_e, "brain.py:archival_vectors")

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
                                
                # Resolve final top 3 paths (Cross-Encoder Re-Ranking on High-Capacity hardware)
                if temp_nb and getattr(temp_nb, 'use_cross_encoder', False):
                    candidate_pool = sorted(scored_paths.keys(), key=lambda k: scored_paths[k], reverse=True)[:5]
                    final_paths = cross_encoder_rerank(intent, candidate_pool, nanobrain=temp_nb)[:3]
                    print(f"  [CROSS-ENCODER] Re-ranked {len(final_paths)} candidate paths via TitanBrain profile.")
                else:
                    final_paths = sorted(scored_paths.keys(), key=lambda k: scored_paths[k], reverse=True)[:3]

                retrieval_chunks = []
                for path in final_paths:
                    try:
                        with open(path, "r", encoding="utf-8", errors="replace") as retrieved_file:
                            retrieval_chunks.append(retrieved_file.read(12000))
                    except OSError as _e:
                        _log_telemetry(_e, f"brain.py:retrieval:{path}")
                try:
                    with RAGDiagnosticJudge(db_path) as judge:
                        judge.evaluate_retrieval(intent, retrieval_chunks)
                except Exception as _re:
                    _log_telemetry(_re, "brain.py:evaluate_retrieval")

                for path in final_paths:
                    if "archive/" in path.replace("\\", "/").lower():
                        normalized_path = path.replace("\\", "/")
                        parts = normalized_path.split("archive/")
                        rel_path = parts[1] if len(parts) > 1 else os.path.basename(path)
                        if os.path.exists(path):
                            print(f"  [AMNESIA RECALL] JIT Read-Only Access to asset '{rel_path}' from archive!")
                        rules.append(path)
                    else:
                        rules.append(path)
                        
                    # --- IDE-4: Smart Memory Compression ---
                    try:
                        c.execute("UPDATE pages SET access_count = IFNULL(access_count, 0) + 1, last_accessed = datetime('now') WHERE path = ?", (path,))
                        conn.commit()
                    except Exception as _e:
                        _log_telemetry(_e, 'brain.py:786')

                # --- 1-Hop Graph Traversal (Knowledge Graph Expansion) ---
                try:
                    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='relations'")
                    has_relations = bool(c.fetchone())
                    if has_relations and final_paths:
                        for seed_path in final_paths:
                            seed_clean = seed_path.replace("\\", "/")
                            seed_base = os.path.basename(seed_path)
                            seed_stem = os.path.splitext(seed_base)[0]

                            # 1. Outgoing relations (seed -> target)
                            c.execute('''
                                SELECT subject_id, predicate, object_id, weight 
                                FROM relations 
                                WHERE subject_id = ? OR subject_id = ? OR subject_id LIKE ? OR source_path = ?
                                LIMIT 8
                            ''', (seed_path, seed_clean, f"%{seed_base}", seed_path))
                            for src, rel, tgt, conf in c.fetchall():
                                hop_triplets.append((os.path.basename(src), rel, tgt))
                                _resolve_neighbor_target(c, tgt, workspace_dir, neighbor_files)

                            # 2. Incoming relations (source -> seed)
                            c.execute('''
                                SELECT subject_id, predicate, object_id, weight 
                                FROM relations 
                                WHERE object_id = ? OR object_id = ? OR object_id = ? OR object_id LIKE ?
                                LIMIT 8
                            ''', (seed_path, seed_clean, seed_stem, f"%{seed_base}"))
                            for src, rel, tgt, conf in c.fetchall():
                                hop_triplets.append((os.path.basename(src), rel, os.path.basename(tgt)))
                                _resolve_neighbor_target(c, src, workspace_dir, neighbor_files)

                            # 3. Canonical entities traversal
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

                                # 1. Outgoing edges (seed -> target)
                                c.execute('''
                                    SELECT source_id, relation, target_id, confidence 
                                    FROM edges 
                                    WHERE source_id = ? OR source_id = ? OR source_id LIKE ?
                                    LIMIT 8
                                ''', (seed_path, seed_clean, f"%{seed_base}"))
                                for src, rel, tgt, conf in c.fetchall():
                                    hop_triplets.append((os.path.basename(src), rel, tgt))
                                    _resolve_neighbor_target(c, tgt, workspace_dir, neighbor_files)

                                # 2. Incoming edges (source -> seed)
                                c.execute('''
                                    SELECT source_id, relation, target_id, confidence 
                                    FROM edges 
                                    WHERE target_id = ? OR target_id = ? OR target_id = ? OR target_id LIKE ?
                                    LIMIT 8
                                ''', (seed_path, seed_clean, seed_stem, f"%{seed_base}"))
                                for src, rel, tgt, conf in c.fetchall():
                                    hop_triplets.append((os.path.basename(src), rel, os.path.basename(tgt)))
                                    _resolve_neighbor_target(c, src, workspace_dir, neighbor_files)

                                # 3. Entity Triplets from defined symbols
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
                            _log_telemetry(_ste, "brain:skill_telemetry")

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
        # --- Brainvibing Injection (RULES_INDEX.md line-by-line) ---
        rules_index_path = os.path.join(agents_dir, "rules", "RULES_INDEX.md")
        if os.path.exists(rules_index_path):
            with open(rules_index_path, "r", encoding="utf-8") as f:
                rules_content = f.read()
                
            print("\n##  Standard Operating Procedures (Micro-Rules)")
            matches = []
            nb = None
            try:
                temp_nb = NanoBrain()
                if temp_nb.ping():
                    nb = temp_nb
            except Exception as _e:
                _log_telemetry(_e, 'brain.py:885')
                
            for line in rules_content.split('\n'):
                if not line.strip() or line.startswith('#'):
                    continue
                line_lower = line.lower()
                
                # Global rules always apply
                if "global" in line_lower:
                    matches.append(line.strip())
                    continue
                    
                # Fast lexical matching against intent keywords (avoids sequential LLM loop hangs)
                is_match = any(kw in line_lower for kw in keywords) if keywords else False
                if is_match:
                    matches.append(line.strip())
                    
            if matches:
                for m in matches[:5]:
                    print(f"  {m}")
            else:
                print("  No specific standards matched. Proceeding with global baseline.")
        # ---------------------------------------------------------
    
    if (skills or rules) and not delta:
        print("\n##  Motor Cortex (Rules & Skills)")
        for r in (rules + skills)[:5]:
            rel_path = os.path.relpath(r, workspace_dir)
            print(f"- [Mandatory Execution Protocol]: {rel_path}")
            
            # Apply NanoBrain compression ONLY to .md rules/skills
            if r.endswith('.md'):
                try:
                    with open(r, "r", encoding="utf-8") as f:
                        content = f.read()
                    if len(content) < 4000: # Limit size to prevent 0.5b timeout
                        if nb and nb.ping():
                            compressed = nb.lessword_compress(content)
                            if compressed and len(compressed) > 10:
                                print(f"  [COMPRESSED CONTEXT]: {compressed.replace(chr(10), ' ')}")
                except Exception as _e:
                    _log_telemetry(_e, 'brain.py:939')

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
            # Sync legacy nodes/edges if communities table is empty
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
            _log_telemetry(_e, 'brain.py:dual_level_graph_rag')

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
            _log_telemetry(_e, 'brain.py:974')
            
    if wiki_nodes:
        print("\n##  Hippocampus (Orion Knowledge)")
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
            _log_telemetry(_e, 'brain.py:995')
            
    if wiki_hits:
        print("\n##  Deep RAG (Orion Graph Hits)")
        print(f"  Found potential nodes: {', '.join(wiki_hits[:3])}")
        top_node = wiki_hits[0]
        print(f"  [AUTO-RAG]: Resolving primary node '{top_node}' automatically...\n")
        try:
            import subprocess
            ops_script = os.path.join(agents_dir, "scripts", "orion.py")
            # We output directly instead of capturing so it prints immediately in sync stream
            resolve_wiki(top_node)
        except Exception as e:
            print(f"  [ERROR] Could not execute Auto-RAG: {e}")
    # -----------------------------------
    
    # --- NanoBrain Active Ping ---
    if nb and nb.ping(capability="LLM"):
        print("\n## [NanoBrain] NanoBrain (Ollama) is ONLINE (LLM Active)")
        print("  [CAPABILITY]: You can use `python .agents/scripts/orion.py brain nanobrain vibe_check <text>` for instant UI aesthetic validation without consuming major tokens.")
    else:
        print("\n## [NanoBrain] [WARNING] NanoBrain LLM features disabled — (Status OFF or EMBED)")
            
    # --- Working Memory (Holographic Handoff) ---
    handoff_path = os.path.join(orion_dir, "working", "handoff.md")
    if os.path.exists(handoff_path):
        print("\n##  Working Memory (Session Handoff)")
        try:
            with open(handoff_path, "r", encoding="utf-8") as f:
                handoff_content = f.read()
            print("  [ACTIVE HANDOFF DETECTED]:")
            for line in handoff_content.splitlines():
                print(f"    {line}")
                
            # Auto-Archive with freshness check
            import datetime, shutil, time
            episodic_dir = os.path.join(orion_dir, "episodic")
            if not os.path.exists(episodic_dir): os.makedirs(episodic_dir)
            
            mtime = os.path.getmtime(handoff_path)
            age_hours = (time.time() - mtime) / 3600
            
            archive_marker = os.path.join(episodic_dir, ".last_archived_mtime")
            last_mtime = 0
            if os.path.exists(archive_marker):
                try:
                    with open(archive_marker, "r") as mf:
                        last_mtime = float(mf.read().strip())
                except Exception as _e:
                    _log_telemetry(_e, 'brain.py:1044')
            
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
    # --------------------------------------------

    # --- Semantic Facts Memory (Tier 1 - Multi-Layer Semantic Facts) ---
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
        _log_telemetry(_e, 'brain.py:sync_facts')

    if saas_nodes:
        print("\n##  Working Memory (SaaS State)")
        for s in saas_nodes:
            rel_path = os.path.relpath(s, workspace_dir)
            print(f"- [Active State]: {rel_path}")
            if get_ast_block(s, 'saas-state'):
                print("  [DATA-NODE]: Extracted semantic state successfully.")
    
    if not (skills or rules or wiki_nodes or saas_nodes):
        print("\n[WARNING]: No contextual nodes found for these tokens. AI must rely on zero-shot reasoning.")
        
    try:
        pass
        record_db_telemetry("brain_sync", exit_code=0, context_load=len(rules + skills))
    except Exception as _e:
        _log_telemetry(_e, 'brain.py:1080')

    print("\n---\n[DIRECTIVE] Read the above files with `view_file` BEFORE modifying code. Adhere to rules. Proceed.")

def page_context(keywords):
    agents_dir = get_agents_dir()
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
                if not file.endswith(".md"): continue
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    chunks = re.split(r'\n(?=#+ )', content)
                    try:
                        for chunk in chunks:
                            chunk_lower = chunk.lower()
                            if any(kw.lower() in chunk_lower for kw in keywords):
                                header_match = re.match(r'(#+ .*?)\n', chunk)
                                header = header_match.group(1) if header_match else f"Excerpt from {file}"
                                
                                # Ephemeral Lessword Compilation
                                chunk_dict = parse_markdown_to_dict(chunk.strip())
                                dense_json = json.dumps(chunk_dict, indent=2)
                                relevant_chunks.append(f"### Source: {file} | {header}\n```json\n{dense_json}\n```\n")
                    except Exception as e:
                        # Fallback if parsing fails
                        for chunk in chunks:
                            chunk_lower = chunk.lower()
                            if any(kw.lower() in chunk_lower for kw in keywords):
                                header_match = re.match(r'(#+ .*?)\n', chunk)
                                header = header_match.group(1) if header_match else f"Excerpt from {file}"
                                relevant_chunks.append(f"### Source: {file} | {header}\n{chunk.strip()}\n")
                except Exception as _e:
                    _log_telemetry(_e, 'brain.py:1130')
                    
    atomic_write_text(page_path, "# Ephemeral Pager Context\n\n" + "\n---\n".join(relevant_chunks))
        
    print(f"Paging complete. {len(relevant_chunks)} chunks swapped into {os.path.relpath(page_path, workspace_dir)}")

def export_vault():
    result = ObsidianVaultExporter().export_vault()
    if result.get("status") != "SUCCESS":
        print(f"[ERROR] Obsidian vault export failed: {result.get('message', 'unknown error')}")
        return 1

    print(f"[SUCCESS] Obsidian vault exported to {result['vault_dir']}")
    print(
        f"[STATUS] notes={result['total_notes']} "
        f"nodes={result['nodes_exported']} "
        f"communities={result['communities_exported']}"
    )
    return 0


def gc_main(argv=None):
    """Garbage collects orphaned caches, stale test backups, loose vault mirrors, and vacuums SQLite."""
    print("🧹 ORION GARBAGE COLLECTOR ENGAGED...")
    cleaned_items = 0
    reclaimed_bytes = 0

    workspace_dir = WORKSPACE_DIR

    # 1. Sweep .orion_mut_bak files across workspace
    for root, dirs, files in os.walk(workspace_dir):
        if any(ignored in root for ignored in [".git", "node_modules", ".dart_tool"]):
            continue
        for f in files:
            if f.endswith(".orion_mut_bak"):
                p = os.path.join(root, f)
                try:
                    reclaimed_bytes += os.path.getsize(p)
                    os.remove(p)
                    cleaned_items += 1
                except Exception as e:
                    _log_telemetry(e, "brain.py:gc_mut_bak")

    # 2. Clean stale vault / export nodes if they exist
    for d in (
        os.path.join(ORION_DIR, "vault", "nodes"),
        os.path.join(ORION_DIR, "vault", "communities"),
        os.path.join(ORION_DIR, "export", "vault", "nodes"),
        os.path.join(ORION_DIR, "export", "vault", "communities"),
    ):
        if os.path.exists(d):
            try:
                for f in os.listdir(d):
                    fp = os.path.join(d, f)
                    if os.path.isfile(fp):
                        reclaimed_bytes += os.path.getsize(fp)
                        os.remove(fp)
                        cleaned_items += 1
                try:
                    os.rmdir(d)
                except Exception as _re:
                    _log_telemetry(_re, "brain.py:gc_rmdir")
            except Exception as e:
                _log_telemetry(e, "brain.py:gc_vault")

    # Clean empty export directories
    for exp_parent in (
        os.path.join(ORION_DIR, "export", "vault"),
        os.path.join(ORION_DIR, "export"),
    ):
        if os.path.exists(exp_parent):
            try:
                os.rmdir(exp_parent)
            except Exception as _re:
                _log_telemetry(_re, "brain.py:gc_rmdir_parent")

    # 3. Clean temporary files in .orion/working/
    working_dir = os.path.join(ORION_DIR, "working")
    if os.path.exists(working_dir):
        for f in os.listdir(working_dir):
            if f.endswith((".tmp", ".lock", ".bak")):
                fp = os.path.join(working_dir, f)
                try:
                    reclaimed_bytes += os.path.getsize(fp)
                    os.remove(fp)
                    cleaned_items += 1
                except Exception as e:
                    _log_telemetry(e, "brain.py:gc_working")

    # 4. Prune rolling FIFO tables & orphaned AST cache in orion.db
    if os.path.exists(DB_PATH):
        try:
            conn = connect_sqlite(DB_PATH)
            cur = conn.cursor()

            # FIFO limit on telemetry (1000 events)
            try:
                cur.execute("SELECT COUNT(*) FROM telemetry")
                t_cnt = cur.fetchone()[0]
                if t_cnt > 1000:
                    cur.execute("DELETE FROM telemetry WHERE id NOT IN (SELECT id FROM telemetry ORDER BY id DESC LIMIT 1000)")
                    cleaned_items += (t_cnt - 1000)
            except Exception as _te:
                _log_telemetry(_te, "brain.py:gc_telemetry")

            # FIFO limit on recall_turns (200 turns)
            try:
                cur.execute("SELECT COUNT(*) FROM recall_turns")
                r_cnt = cur.fetchone()[0]
                if r_cnt > 200:
                    cur.execute("DELETE FROM recall_turns WHERE id NOT IN (SELECT id FROM recall_turns ORDER BY id DESC LIMIT 200)")
                    cleaned_items += (r_cnt - 200)
            except Exception as _re:
                _log_telemetry(_re, "brain.py:gc_recall")

            # FIFO limit on spans (500 spans)
            try:
                cur.execute("SELECT COUNT(*) FROM spans")
                s_cnt = cur.fetchone()[0]
                if s_cnt > 500:
                    cur.execute("DELETE FROM spans WHERE span_id NOT IN (SELECT span_id FROM spans ORDER BY start_time DESC LIMIT 500)")
                    cleaned_items += (s_cnt - 500)
            except Exception as _se:
                _log_telemetry(_se, "brain.py:gc_spans")

            # Evict orphaned AST symbol cache entries for deleted/moved files
            try:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ast_symbol_cache'")
                if cur.fetchone():
                    cur.execute("SELECT path FROM ast_symbol_cache")
                    stale_paths = [r[0] for r in cur.fetchall() if not os.path.exists(r[0])]
                    for sp in stale_paths:
                        cur.execute("DELETE FROM ast_symbol_cache WHERE path = ?", (sp,))
                        cleaned_items += 1
            except Exception as _ae:
                _log_telemetry(_ae, "brain.py:gc_ast_cache")

            conn.commit()

            # Vacuum and optimize
            conn.execute("VACUUM")
            conn.execute("PRAGMA optimize")
            conn.close()
            print(" [PASS] SQLite orion.db vacuumed, optimized, and pruned.")
        except Exception as e:
            _log_telemetry(e, "brain.py:gc_vacuum")

    # Record GC timestamp
    last_gc_file = os.path.join(ORION_DIR, "working", ".last_gc")
    try:
        atomic_write_text(last_gc_file, str(time.time()))
    except Exception as _ge:
        _log_telemetry(_ge, "brain.py:gc_timestamp")

    # 5. Measure and assert clean stats
    file_count = 0
    total_bytes = 0
    if os.path.exists(ORION_DIR):
        for root, _, files in os.walk(ORION_DIR):
            file_count += len(files)
            for f in files:
                total_bytes += os.path.getsize(os.path.join(root, f))

    print(f" [PASS] Cleaned {cleaned_items} orphaned items ({reclaimed_bytes / 1024:.1f} KB reclaimed).")
    print(f" [STATUS] Active .orion files: {file_count} ({total_bytes / (1024*1024):.2f} MB).")
    if file_count <= 50:
        print(" [PASS] .orion storage is lean (<= 50 files).")
    else:
        print(f" [WARN] .orion file count ({file_count}) exceeds lean threshold (50).")
    return 0


# ============================================================================
# SECTION 10: UNIFIED CLI DISPATCHER
# ============================================================================

def main():
    argv = sys.argv[1:]
    if not argv:
        print("Orion Brain & Unified Knowledge Engine")
        print("Usage: orion.py brain <subcommand> [args...]")
        print("Subcommands:")
        print("  sync <intent> [--delta]   - Sync brain context graph")
        print("  autoscale                 - Auto-scale profile & hardware detection")
        print("  nanobrain <action>        - Local LLM coprocessor operations")
        print("  page <keywords...>        - Ephemeral context pager")
        print("  export-vault              - Export knowledge graph to Obsidian vault")
        print("  gc                        - Garbage collect caches and vacuum orion.db")
        print("  init                      - Bootstrap orion structure")
        print("  ingest <paths...>         - Ingest files into brain graph")
        print("  resolve <node>            - Resolve node context & backlinks")
        print("  inject_triplets <json>    - Inject semantic graph triplets")
        print("  compile                   - Compile markdown rules to JSON matrices")
        print("  matrix <keywords...>      - Query compiled rule matrices")
        print("  compress                  - Surgical memory compression")
        print("  shrink <file>             - Layer 2 token shrinker")
        print("  distill <file>            - Layer 3 semantic distillation")
        print("  compact <file|text>       - Corpus surprisal compactor")
        print("  contradict <action>       - Contradiction resolution engine")
        print("  raw-ingest                - Ingest context/raw/ files")
        print("  diagnostics               - RAG relevance & faithfulness diagnostics")
        print("  memory                    - Multi-layer memory status")
        return 0

    cmd = argv[0].lower()
    sub_args = argv[1:]

    # Strip redundant command prefix if forwarded by orion.py
    if cmd in ("orion_ops", "orion") and sub_args:
        cmd = sub_args[0].lower()
        sub_args = sub_args[1:]

    if cmd in ("sync", "context"):
        delta = "--delta" in sub_args
        intent_tokens = [a for a in sub_args if a != "--delta"]
        intent = " ".join(intent_tokens) if intent_tokens else "latest context sync"
        return sync(intent, delta)
    elif cmd in ("autoscale", "hardware"):
        hw = detect_hardware()
        print(f" Detected RAM: {hw['ram_gb']:.1f} GB")
        print(f" Detected GPU VRAM: {hw['vram_gb']:.1f} GB ({hw['gpu_name'] or 'No dedicated GPU'})")
        sim = "--simulate-ideal" in sub_args
        if sim:
            print(" [SIMULATION] Simulating Ideal PC (>24GB RAM & >=12GB VRAM)...")
        profile = apply_auto_scale_profile(hw, force_high_capacity=sim)
        print(f" Auto-Scale Tier: {profile['tier']}")
        print(f" Selected Model: {profile['model']}")
        print(f" NanoBrain Status: {profile['status']}")
        print(f" Daily Mutation Cap: {profile['daily_mutation_cap']}")
        print(f" Cross-Encoder Re-Ranking: {'ENABLED' if profile['use_cross_encoder'] else 'DISABLED'}")
        return 0
    elif cmd == "nanobrain":
        agents_dir = get_agents_dir()
        status_file = os.path.join(agents_dir, ".nanobrain_status")
        action = sub_args[0] if sub_args else "status"
        text = sub_args[1] if len(sub_args) > 1 else ""

        if action == "on":
            atomic_write_text(status_file, "FULL")
            print("NanoBrain mode set to FULL (Ollama LLM + Embeddings enabled)")
        elif action == "off":
            atomic_write_text(status_file, "OFF")
            print("NanoBrain disabled completely (Pure Python mode)")
        elif action == "embed_only":
            atomic_write_text(status_file, "EMBED_ONLY")
            print("NanoBrain mode set to EMBED_ONLY")
        elif action == "llm_only":
            atomic_write_text(status_file, "LLM_ONLY")
            print("NanoBrain mode set to LLM_ONLY")
        elif action == "status":
            st = "OFF"
            if os.path.exists(status_file):
                with open(status_file, "r", encoding="utf-8") as f: st = f.read().strip()
            print(f"Current NanoBrain Status: {st}")
        else:
            nb = NanoBrain()
            if action == "vibe_check":
                print(nb.vibe_check(text))
            elif action == "extract":
                print(nb.extract_triplets(text))
            elif action == "compress":
                print(nb.lessword_compress(text))
            elif action == "draft":
                print(nb.draft_boilerplate(text))
            else:
                print(f"Unknown nanobrain action: {action}")
                return 1
        return 0
    elif cmd == "page":
        if not sub_args:
            print("Usage: orion.py brain page <keyword1> <keyword2> ...")
            return 1
        page_context(sub_args)
        return 0
    elif cmd == "export-vault":
        if any(h in sub_args for h in ("-h", "--help")):
            print("Export Orion graph into an Obsidian vault")
            return 0
        return export_vault()
    elif cmd in ("gc", "clean"):
        return gc_main(sub_args)
    elif cmd in ("init", "ingest", "resolve", "inject_triplets"):
        return orion_ops_main([cmd] + sub_args)
    elif cmd in ("orion_ops", "orion"):
        return orion_ops_main(sub_args)
    elif cmd in ("compile", "compile_rules"):
        return compile_rules_main(sub_args)
    elif cmd in ("matrix", "matrix-query", "matrix_query"):
        return matrix_query_main(sub_args)
    elif cmd in ("compress", "compress_memory"):
        return compress_main(sub_args)
    elif cmd == "shrink":
        return shrink_main(sub_args)
    elif cmd == "distill":
        return distill_main(sub_args)
    elif cmd in ("compact", "compactor"):
        return compactor_main(sub_args)
    elif cmd in ("contradict", "contradictions"):
        return contradict_main(sub_args)
    elif cmd in ("raw_ingest", "raw-ingest"):
        return raw_ingest_main(sub_args)
    elif cmd == "diagnostics":
        return diagnostics_main(sub_args)
    elif cmd == "memory":
        return memory_main(sub_args)
    else:
        # Default fallback to sync
        return sync(" ".join(argv), delta=False)

if __name__ == "__main__":
    sys.exit(main() or 0)
