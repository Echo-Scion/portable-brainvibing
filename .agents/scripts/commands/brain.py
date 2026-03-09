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
from core.capabilities import (
    parse_model_parameters_b,
    enqueue_cloud_handoff,
    clear_cloud_handoff,
    save_neuro_symbolic_cache,
)

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
        import uuid
        abs_path = os.path.abspath(str(filepath))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        temp_file = f"{abs_path}.tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(temp_file, abs_path)
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
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

    try:
        from core.capabilities import detect_hardware as _kernel_detect_hw
        hw = _kernel_detect_hw()
        ram_gb = hw.get("memory_gb", 0.0)
    except Exception as _e:
        _log_telemetry(_e, 'brain.py:detect_hardware_cap')
        ram_gb = 16.0

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

    # Accommodate 16GB RAM systems (OS hardware reserved leaves ~15.5-15.8GB)
    is_high_capacity = (ram_gb >= 22.0 or (ram_gb >= 15.0 and vram_gb >= 6.0))
    _HARDWARE_INFO = {
        "ram_gb": round(ram_gb, 2),
        "vram_gb": round(vram_gb, 2),
        "is_high_capacity": is_high_capacity,
        "gpu_name": gpu_name
    }
    return _HARDWARE_INFO

# --- Centralized Local AI URL Resolution (Dual-Stack Fallback + Self-Heal) ---

def resolve_ollama_base_url(force_refresh=False):
    """
    Resolves reachable local AI base URL via centralized capabilities across all providers.
    """
    try:
        from core.capabilities import resolve_local_ai_endpoint
        local_ai = resolve_local_ai_endpoint(force_refresh=force_refresh)
        if local_ai and local_ai.get("base_url"):
            url = local_ai["base_url"]
            if local_ai.get("api_format") == "openai":
                os.environ["ORION_LLM_URL"] = url + "/v1/chat/completions"
            else:
                os.environ["ORION_LLM_URL"] = url + "/api/generate"
            return url
        return None
    except Exception as _e:
        _log_telemetry(_e, "brain.py:resolve_ollama_base_url")
        return None

def get_available_ollama_models(base_url=None):
    try:
        from core.capabilities import get_available_models
        models = get_available_models(base_url=base_url)
        if models:
            return models
    except Exception as _e:
        _log_telemetry(_e, "brain.py:get_available_ollama_models")

    if not base_url:
        return []

    # Fallback to direct probe if capabilities import fails
    api_format = "openai" if any(p in base_url for p in (":8080", ":1234", ":8000")) else "ollama"
    if api_format == "openai":
        try:
            req = urllib.request.Request(f"{base_url.rstrip('/')}/v1/models", method="GET")
            with urllib.request.urlopen(req, timeout=2) as r:
                data = json.loads(r.read().decode('utf-8'))
                return [m.get("id", "") for m in data.get("data", []) if m.get("id")]
        except Exception:
            pass

    try:
        req = urllib.request.Request(f"{base_url.rstrip('/')}/api/tags", method="GET")
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
        self.provider_info = None
        self.api_format = "ollama"
        self.base_url = None
        try:
            from core.capabilities import resolve_local_ai_endpoint
            self.provider_info = resolve_local_ai_endpoint()
            if self.provider_info:
                self.base_url = self.provider_info.get("base_url")
                self.api_format = self.provider_info.get("api_format", "ollama")
        except Exception:
            pass

        if not self.base_url:
            self.base_url = resolve_ollama_base_url()

        if self.base_url:
            if self.api_format == "openai":
                self.endpoint = self.base_url.rstrip("/") + "/v1/chat/completions"
            else:
                self.endpoint = self.base_url.rstrip("/") + "/api/generate"
        else:
            self.endpoint = os.environ.get("ORION_LLM_URL", "http://127.0.0.1:11434/api/generate")
            if any(p in self.endpoint for p in (":8080", ":1234", ":8000")) or "/v1" in self.endpoint:
                self.api_format = "openai"

        self.hw_info = detect_hardware()
        self.profile = apply_auto_scale_profile(self.hw_info, force_high_capacity=force_high_capacity)
        self.use_cross_encoder = self.profile.get("use_cross_encoder", False)

        if model:
            self.model = model
        else:
            self.model = self.profile.get("model", "qwen2.5:0.5b")

        model_b = parse_model_parameters_b(self.model)
        if self.profile.get("tier") == "TITAN_HIGH_CAPACITY" or model_b >= 27.0:
            self.tier_level = 3
            self.tier_name = "high_intelligence"
        elif model_b >= 6.5:
            self.tier_level = 2
            self.tier_name = "medium_intelligence"
        else:
            self.tier_level = 1  # 1: Low, 2: Medium, 3: High
            self.tier_name = "low_intelligence"

        agents_dir = get_agents_dir()
        manifest_path = os.path.join(agents_dir, ".project_manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
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
            enqueue_cloud_handoff(
                f"TIER_REQUIRED_{feature_name.upper().replace(' ', '_')}",
                {"required_level": required_level, "feature": feature_name, "current_tier": self.tier_name},
                reason=f"tier_level_{self.tier_level}_below_{required_level}",
            )
            return f"[DELEGATE_TO_CLOUD] Error: Required Medium Intelligence (or higher) for {feature_name}. Current tier is '{self.tier_name}'. Fallback gracefully to Cloud Agent LLM."
        return None

    def ping(self, capability="ANY"):
        agents_dir = get_agents_dir()
        status_file = os.path.join(agents_dir, ".nanobrain_status")
        state = "FULL" # Default if file doesn't exist
        if os.path.exists(status_file):
            try:
                with open(status_file, "r", encoding="utf-8") as f:
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

    def generate(self, prompt, system="You are Orion NanoBrain, a strict JSON extracting router. You do NOT write code.", timeout=20.0, format_json=False):
        if not self.ping(capability="LLM"):
            return None
        # Strict Guard: never allow generative prompts to be sent to embedding-only models
        embed_keywords = ["embed", "bge", "nomic-embed", "minilm", "mxbai", "rerank"]
        if any(k in self.model.lower() for k in embed_keywords):
            print(f"[NanoBrain] Model '{self.model}' is an embedding-only model. Delegating to Cloud Handoff.", file=sys.stderr)
            return None

        try:
            from core.capabilities import generate_completion
            res = generate_completion(prompt, model=self.model, system_prompt=system, host=self.base_url, timeout_sec=timeout)
            if res:
                return res
        except Exception as _ce:
            _log_telemetry(_ce, "brain.py:generate_via_capabilities")

        # Fallback to direct call on self.endpoint (only if Ollama format)
        if self.api_format == "openai":
            return None

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {"temperature": 0.1}
        }
        if format_json:
            payload["format"] = "json"
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(self.endpoint, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                resp = json.loads(r.read().decode('utf-8'))
                return resp.get('response', '')
        except Exception as e:
            print(f"[NanoBrain] generate error: {e}", file=sys.stderr)
            return None

    def embed(self, text, model="nomic-embed-text"):
        if not self.ping(capability="EMBED"):
            return None
        try:
            from core.capabilities import get_embedding
            emb = get_embedding(text, model=model, host=self.base_url, timeout_sec=10.0)
            if emb:
                return emb
        except Exception as _ee:
            _log_telemetry(_ee, "brain.py:embed_via_capabilities")

        if self.api_format == "openai":
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
        # Tier-2 (Ollama LLM >= 6.5B) extracts JSON triplets with strict schema;
        # If Ollama is offline or generation fails, gracefully delegate to Cloud Agent (Tier-2).
        block_msg = self.check_tier(2, "Triplet Extraction")
        if block_msg:
            return block_msg
        if not self.ping(capability="LLM"):
            return "[DELEGATE_TO_CLOUD]"
        system = (
            "Extract 3 to 5 architectural knowledge triplets from the text. "
            "Respond ONLY with a valid JSON array of objects: "
            "[{\"s\": \"SubjectEntity\", \"p\": \"PREDICATE_VERB\", \"o\": \"ObjectEntity\"}]"
        )
        prompt = f"Extract semantic triplets from:\n\n{text[:4000]}"
        res = self.generate(prompt, system=system, timeout=25.0, format_json=True)
        return res if res else "[DELEGATE_TO_CLOUD] Error: Extraction failed. Fallback to Cloud Agent."

# ============================================================================
# SECTION 2: VECTOR MATH & RAG DIAGNOSTICS
# Delegated to commands/rag.py
# ============================================================================
from commands.rag import (  # noqa: F401
    extract_keywords,
    compute_cosine,
    RAGDiagnosticJudge,
    diagnostics_main,
)

# ============================================================================
# SECTION 3 & 4: COMPACTION, TOKEN SHRINK & DISTILLATION
# Delegated to commands/compact.py
# ============================================================================
from commands.compact import (  # noqa: F401
    ULTRA_PROTECTED_TERMS,
    CorpusInformationCompactor,
    shrink_json,
    shrink_csv,
    shrink_log,
    shrink_ast_python,
    shrink_ast_generic,
    shrink_content,
    shrink_main,
    select_best_distill_model,
    distill_via_ollama,
    heuristic_fallback_distill,
    distill_content,
    distill_main,
    split_frontmatter,
    is_sensitive_path,
    LESSWORD_PHRASE_MAP,
    LESSWORD_ULTRA_ABBREV,
    SAFETY_BOUNDARY_ESCAPE_RE,
    SyntaxAnchorGuard,
    OrionCompactor,
    telegraphic_shrink,
    lessword_compress_text,
    compact_target,
    compactor_main,
    get_strategy_memory_file,
    generate_fractal_shorthand,
    compress_handoff,
    compress_tasks,
    check_compression_eligibility,
    compress_strategy_memory,
    compress_file,
    compress_memory,
    compress_main,
    STREAM_MAX_CHARS,
    STREAM_HEAD_LINES,
    STREAM_TAIL_LINES,
    STREAM_SALVAGE_MAX,
    STREAM_SALVAGE_LINE,
    STREAM_SPILL_KEEP,
    STREAM_DIAGNOSTIC_RE,
)

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
            stopwords = {
                "when", "user", "code", "files", "using", "across", "before", "after",
                "with", "from", "into", "that", "this", "your", "make", "task", "tasks",
                "tool", "tools", "file", "data", "system", "project", "run", "running",
                "check", "checking", "needs", "need", "should", "could", "would", "about"
            }
            words = [
                w.strip(" .,();:\"'[]") for w in when_part.split()
                if len(w) >= 5 and w.strip(" .,();:\"'[]") not in triggers and w.strip(" .,();:\"'[]") not in stopwords
            ]
            triggers = list(dict.fromkeys(triggers + words[:6]))

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
    "working", "working/audit", "working/brain", "episodic",
    "matrix"
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
            VALUES (COALESCE(NEW.id, NEW.name), NEW.type, NEW.name, NEW.source_path);
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

    try:
        OrionGraphStore(DB_PATH).init_schema()
        backfill_conn = connect_sqlite(DB_PATH)
        bc = backfill_conn.cursor()
        bc.execute("""
            INSERT INTO entities_fts(rowid, name, type, description, source_path)
            SELECT id, name, type, description, source_path FROM entities
            WHERE id NOT IN (SELECT rowid FROM entities_fts);
        """)
        bc.execute("""
            INSERT INTO relations_fts(rowid, subject_id, predicate, object_id)
            SELECT id, subject_id, predicate, object_id FROM relations
            WHERE id NOT IN (SELECT rowid FROM relations_fts);
        """)
        backfill_conn.commit()
        backfill_conn.close()
    except Exception as _fe:
        _log_telemetry(_fe, "brain.py:init_schema_backfill")

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

    fm = {}
    if content and ("---" in content[:200] or "epistemic_status" in content[:400]):
        try:
            fm = parse_frontmatter(content)
        except Exception as _fme:
            _log_telemetry(_fme, 'brain.py:classify_file:parse_frontmatter')

    epistemic = str(fm.get("epistemic_status", "")).upper()
    needs_review = fm.get("needs_human_review", False)
    
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
        category = "context-master" if (filepath_normalized.endswith("CONTEXT.md") or any(m in filepath_normalized for m in ["BLUEPRINT.md", "ROADMAP.md", "STYLE_GUIDE.md", "ARCHITECTURE.md"])) else "context-pillar"
        if "00_Strategy" in filepath_normalized:
            pillar = "strategy"
        elif "01_Product" in filepath_normalized:
            pillar = "product"
        elif "02_Creative" in filepath_normalized:
            pillar = "creative"
        elif "03_Tech" in filepath_normalized:
            pillar = "tech"
        else:
            pillar = "tech"

    # Epistemic Confidence Calibration
    if epistemic == "HYPOTHESIS_DRAFT" or needs_review:
        confidence = "hypothesis"
    elif epistemic == "SDK_INFERRED":
        confidence = "inferred"
    elif epistemic == "AST_VERIFIED":
        confidence = "authoritative"
        
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
                                db_c.execute(f'DELETE FROM archival_vectors WHERE id IN ({placeholders})', paths_to_delete)
                                db_c.execute(f'DELETE FROM relations WHERE source_path IN ({placeholders})', paths_to_delete)
                                db_c.execute(f'DELETE FROM entities WHERE source_path IN ({placeholders})', paths_to_delete)
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
                c.execute('DELETE FROM relations WHERE source_path = ? OR subject_id = ?', (target_path, target_path))
                
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
                            raw_rel = parts[1].strip() if len(parts) > 1 else "mentions"
                            # Enforce strict predicate whitelist to prevent second-order prompt injection
                            if re.match(r'^[A-Za-z0-9_-]{1,32}$', raw_rel):
                                relation = raw_rel
                            else:
                                relation = "mentions"
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
                    file_bname = os.path.basename(target_path)
                    for caller, rel, callee in triplets:
                        src_node = target_path if (not caller or caller == file_bname) else caller
                        if src_node != target_path:
                            c.execute('''
                                INSERT OR IGNORE INTO nodes (id, type, name, source_path) 
                                VALUES (?, ?, ?, ?)
                            ''', (src_node, 'AST_Element', src_node, target_path))
                        c.execute('''
                            INSERT OR IGNORE INTO nodes (id, type, name, source_path) 
                            VALUES (?, ?, ?, ?)
                        ''', (callee, 'AST_Element', callee, target_path))
                        c.execute('''
                            INSERT OR IGNORE INTO edges (source_id, target_id, relation, confidence, source_path)
                            VALUES (?, ?, ?, 1.0, ?)
                        ''', (src_node, callee, rel, target_path))
                
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
                
            # Tier-1 / Tier-2 Hybrid Triplet Extraction
            nb = NanoBrain()
            auto_extracted = 0
            pending_files = []
            if nb.ping(capability="LLM"):
                print(f"\n[NEURAL COPROCESSOR] Attempting automated triplet extraction via Ollama ({nb.model})...")
                for orig, target in ingested_files:
                    try:
                        with open(target, "r", encoding="utf-8", errors="ignore") as tf:
                            t_content = tf.read()
                        raw_triplets = nb.extract_triplets(t_content)
                        if raw_triplets and not raw_triplets.startswith("[DELEGATE_TO_CLOUD]"):
                            t_parsed = json.loads(raw_triplets)
                            t_list = t_parsed if isinstance(t_parsed, list) else (t_parsed.get("triplets", []) if isinstance(t_parsed, dict) else [])
                            valid_triplets = [
                                item for item in t_list
                                if isinstance(item, dict)
                                and str(item.get("s", "")).strip()
                                and str(item.get("p", "")).strip()
                                and str(item.get("o", "")).strip()
                            ]
                            if valid_triplets:
                                rel_src = os.path.relpath(orig, WORKSPACE_DIR).replace("\\", "/")
                                for item in valid_triplets:
                                    item["src"] = rel_src
                                inject_triplets(json.dumps(valid_triplets))
                                auto_extracted += 1
                                continue
                    except Exception as _te:
                        _log_telemetry(_te, "brain.py:auto_extract_triplets")
                    pending_files.append((orig, target))
            else:
                pending_files = ingested_files

            if auto_extracted > 0:
                print(f"[NEURAL COPROCESSOR] Successfully auto-extracted & injected triplets for {auto_extracted}/{len(ingested_files)} files.")

            if pending_files:
                print(f"\n[TRIPLET_REQUEST] {len(pending_files)} files need graph triplet extraction.")
                pending_payload = {
                    "files": [
                        {
                            "target": os.path.relpath(t, WORKSPACE_DIR).replace("\\", "/"),
                            "source": os.path.relpath(o, WORKSPACE_DIR).replace("\\", "/"),
                        }
                        for o, t in pending_files
                    ]
                }
                enqueue_cloud_handoff(
                    "EXTRACT_GRAPH_TRIPLETS",
                    pending_payload,
                    reason="local_model_cannot_extract_triplets",
                )
            print("⚡ RECOMMENDED TIER: BUDGET — Ingest/deploy operations are batch tasks. Switch to Budget model.")
            print("Files:")
            for i, (orig, target) in enumerate(pending_files, 1):
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
        parsed_raw = json.loads(json_data)
        if isinstance(parsed_raw, dict):
            triplets = parsed_raw.get("triplets", [])
        elif isinstance(parsed_raw, list):
            triplets = parsed_raw
        else:
            triplets = []

        if not triplets:
            print("[INFO] No triplets provided.")
            return
            
        conn = get_db()
        c = conn.cursor()
        
        # Collect unique sources to clear stale triplets first
        unique_sources = set()
        for t in triplets:
            if not isinstance(t, dict):
                continue
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
        # Automatically recompute canonical communities after triplet ingestion
        try:
            _recompute_canonical_communities()
        except Exception as _recomp_err:
            _log_telemetry(_recomp_err, "brain.py:inject_triplets_recompute_communities")
        conn.close()
        if count == 0:
            print(f"[FAIL] 0 triplets injected from {len(triplets)} item(s). Check keys (expected 's'/'subject', 'p'/'predicate', 'o'/'object').")
            sys.exit(1)
        else:
            print(f"[SUCCESS] Injected {count} triplets into orion.db.")
            clear_cloud_handoff("EXTRACT_GRAPH_TRIPLETS")
        
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
# SECTION 9: CONTEXT RETRIEVAL, BRAIN SYNC & OBSIDIAN VAULT
# Delegated to commands/rag.py and commands/vault.py
# ============================================================================
from commands.rag import (  # noqa: F401
    extract_keywords,
    search_files,
    get_ast_block,
    _resolve_neighbor_target,
    sync,
    page_context,
)
from commands.vault import (  # noqa: F401
    export_vault,
    build_second_brain,
    clean_vault_mirrors,
    vault_main,
)


def gc_main(argv=None):
    """Garbage collects orphaned caches, stale test backups, loose vault mirrors, and vacuums SQLite."""
    print("🧹 ORION GARBAGE COLLECTOR ENGAGED...")
    cleaned_items = 0
    reclaimed_bytes = 0

    deep_purge = False
    if argv:
        deep_purge = any(a in argv for a in ("--deep", "--purge-bundles", "--all"))

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

    # 2. Clean stale vault / export nodes only if deep_purge requested or explicitly orphaned
    gc_dirs = [
        os.path.join(ORION_DIR, "vault", "nodes"),
        os.path.join(ORION_DIR, "vault", "communities"),
    ]
    if deep_purge:
        gc_dirs.extend([
            os.path.join(ORION_DIR, "export", "vault", "nodes"),
            os.path.join(ORION_DIR, "export", "vault", "communities"),
            os.path.join(ORION_DIR, "export", "vault"),
            os.path.join(ORION_DIR, "bundles", "audit"),
            os.path.join(ORION_DIR, "bundles", "full_bundles"),
            os.path.join(ORION_DIR, "bundles", "full"),
            os.path.join(ORION_DIR, "bundles", "arch"),
            os.path.join(ORION_DIR, "bundles", "hybrid"),
        ])

    for d in gc_dirs:
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

    # Clean empty export directory if deep_purge
    if deep_purge:
        exp_parent = os.path.join(ORION_DIR, "export")
        if os.path.exists(exp_parent):
            try:
                if not os.listdir(exp_parent):
                    os.rmdir(exp_parent)
            except Exception as _re:
                _log_telemetry(_re, "brain.py:gc_rmdir_parent")

        bundles_parent = os.path.join(ORION_DIR, "bundles")
        if os.path.exists(bundles_parent):
            try:
                if not os.listdir(bundles_parent):
                    os.rmdir(bundles_parent)
            except Exception as _re:
                _log_telemetry(_re, "brain.py:gc_rmdir_bundles")

    # 2b. Sweep empty legacy/redundant directories in .orion
    legacy_empty_dirs = [
        "sources", "facts", "relations", "rules", "schemas",
        "vault", "archive", "audit_export"
    ]
    for led in legacy_empty_dirs:
        led_path = os.path.join(ORION_DIR, led)
        if os.path.exists(led_path) and os.path.isdir(led_path):
            try:
                entries = os.listdir(led_path)
                if not entries:
                    os.rmdir(led_path)
                    cleaned_items += 1
                elif all(os.path.isfile(os.path.join(led_path, x)) and x.endswith((".tmp", ".bak")) for x in entries):
                    for x in entries:
                        os.remove(os.path.join(led_path, x))
                        cleaned_items += 1
                    os.rmdir(led_path)
                    cleaned_items += 1
            except Exception as _led_err:
                _log_telemetry(_led_err, f"brain.py:gc_legacy_dir:{led}")

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
                    cur.execute("SELECT filepath FROM ast_symbol_cache")
                    stale_paths = [r[0] for r in cur.fetchall() if not os.path.exists(r[0])]
                    for sp in stale_paths:
                        cur.execute("DELETE FROM ast_symbol_cache WHERE filepath = ?", (sp,))
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

    # 4b. Trim trajectory log to rolling 1000 events
    traj_file = os.path.join(ORION_DIR, "working", "trajectory.jsonl")
    if os.path.exists(traj_file):
        try:
            with open(traj_file, "r", encoding="utf-8") as tf:
                t_lines = tf.readlines()
            if len(t_lines) > 1000:
                with open(traj_file, "w", encoding="utf-8") as tf:
                    tf.writelines(t_lines[-1000:])
                cleaned_items += (len(t_lines) - 1000)
        except Exception as _tr_err:
            _log_telemetry(_tr_err, "brain.py:gc_trajectory")

    # 4c. Prune vector embeddings memory
    try:
        from core.memory import ArchivalMemoryManager
        with ArchivalMemoryManager() as amm:
            if hasattr(amm, "prune_vectors"):
                pruned_vecs = amm.prune_vectors(max_rows=5000)
                if pruned_vecs:
                    cleaned_items += pruned_vecs
    except Exception as _amm_err:
        _log_telemetry(_amm_err, "brain.py:gc_vectors")

    # Record GC timestamp
    last_gc_file = os.path.join(ORION_DIR, "working", ".last_gc")
    try:
        atomic_write_text(last_gc_file, str(time.time()))
    except Exception as _ge:
        _log_telemetry(_ge, "brain.py:gc_timestamp")

    # 5. Measure and assert clean stats (excluding user exports and bundles from internal working SLA)
    file_count = 0
    total_bytes = 0
    internal_file_count = 0
    if os.path.exists(ORION_DIR):
        for root, _, files in os.walk(ORION_DIR):
            is_export_or_bundle = any(p in root.replace("\\", "/") for p in ("/export", "/bundles"))
            file_count += len(files)
            if not is_export_or_bundle:
                internal_file_count += len(files)
            for f in files:
                total_bytes += os.path.getsize(os.path.join(root, f))

    print(f" [PASS] Cleaned {cleaned_items} orphaned items ({reclaimed_bytes / 1024:.1f} KB reclaimed).")
    print(f" [STATUS] Active .orion files: {file_count} ({total_bytes / (1024*1024):.2f} MB), Internal working files: {internal_file_count}.")
    if internal_file_count <= 50:
        print(" [PASS] .orion internal working storage is lean (<= 50 files).")
    else:
        print(f" [WARN] .orion internal working file count ({internal_file_count}) exceeds lean threshold (50).")
    return 0


# ============================================================================
# SECTION 9.5: CLOUD AGENT HANDOFF DISPATCHER
# ============================================================================

def handoff_main(sub_args: List[str]) -> int:
    """
    Subcommand handler for 'orion brain handoff [list|show|resolve|clear]'.
    Facilitates Cloud Agent / IDE LLM handoff resolution for offline or high-capacity tasks.
    """
    handoff_file = os.path.join(ORION_DIR, "working", "cloud_handoff_queue.json")
    action = sub_args[0].lower() if sub_args else "list"

    if action in ("list", "status", "ls"):
        if not os.path.exists(handoff_file):
            print("[CLOUD HANDOFF] Queue file does not exist. Zero pending handoffs.")
            return 0
        try:
            with open(handoff_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            tasks = data.get("tasks", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
            pending = [t for t in tasks if t.get("status") == "pending"]
            if not pending:
                print("[CLOUD HANDOFF] Zero pending handoffs. Queue is clean.")
                return 0
            print(f"[CLOUD HANDOFF] Found {len(pending)} pending handoff task(s):")
            for idx, t in enumerate(pending, 1):
                tid = t.get("id", f"handoff_{idx}")
                ttype = t.get("task_type", "UNKNOWN")
                reason = t.get("reason", "unknown")
                created = t.get("created_at", "")
                print(f" {idx}. [{ttype}] ID: {tid} | Reason: {reason} | Created: {created}")
                preview = json.dumps(t.get("payload", {}))[:120]
                print(f"    Payload: {preview}...")
            print("\nTo inspect a task:")
            print("  python .agents/scripts/orion.py brain handoff show <task_id>")
            print("To resolve a task with Cloud Agent LLM output:")
            print("  python .agents/scripts/orion.py brain handoff resolve <task_type_or_id> '<json_result>'")
            print("To clear handoffs:")
            print("  python .agents/scripts/orion.py brain handoff clear [task_type]")
            return 0
        except Exception as e:
            print(f"[ERROR] Failed to read cloud handoff queue: {e}")
            return 1

    elif action == "show":
        if len(sub_args) < 2:
            print("Usage: orion brain handoff show <task_id_or_type>")
            return 1
        target = sub_args[1].lower()
        if not os.path.exists(handoff_file):
            print("[ERROR] No handoffs found.")
            return 1
        try:
            with open(handoff_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            tasks = data.get("tasks", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
            matched = [t for t in tasks if t.get("id", "").lower() == target or t.get("task_type", "").lower() == target]
            if not matched:
                print(f"[ERROR] No task matching '{target}' found.")
                return 1
            print(json.dumps(matched[0], indent=2))
            return 0
        except Exception as e:
            print(f"[ERROR] Failed to show task: {e}")
            return 1

    elif action == "resolve":
        if len(sub_args) < 3:
            print("Usage: orion brain handoff resolve <task_type_or_id> '<json_result_or_->'")
            return 1
        target_ref = sub_args[1]
        raw_json = sub_args[2]
        if raw_json == "-":
            raw_json = sys.stdin.read().strip()
        try:
            parsed_result = json.loads(raw_json)
        except Exception as e:
            print(f"[ERROR] Invalid JSON payload provided for resolution: {e}")
            return 1

        matched_type = target_ref
        cache_key = None
        if os.path.exists(handoff_file):
            try:
                with open(handoff_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                tasks = data.get("tasks", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                for t in tasks:
                    if t.get("id") == target_ref or t.get("task_type") == target_ref:
                        matched_type = t.get("task_type", target_ref)
                        cache_key = t.get("payload", {}).get("cache_key")
                        break
            except Exception:
                pass

        if cache_key:
            save_neuro_symbolic_cache(cache_key, parsed_result)

        if matched_type == "PACK_TAXONOMY":
            try:
                from utils.packer import ProjectTaxonomy, save_taxonomy_cache
                tree_hash = parsed_result.get("tree_hash", "cloud_resolved")
                clusters = parsed_result.get("clusters", {})
                f2c = {}
                skel_cand = set(parsed_result.get("skeleton_candidates", []))
                for slug, info in clusters.items():
                    grav = info.get("gravity", 5)
                    title = info.get("title", slug)
                    for f in info.get("files", []):
                        f2c[f] = (grav, slug.lower(), title)
                tax = ProjectTaxonomy(
                    tree_hash=tree_hash,
                    provider="cloud_agent",
                    clusters=clusters,
                    file_to_cluster=f2c,
                    skeleton_candidates=skel_cand,
                )
                save_taxonomy_cache(WORKSPACE_DIR, tax)
                print(f"[SUCCESS] Injected cloud-resolved taxonomy ({len(clusters)} clusters) into cache.")
            except Exception as pe:
                print(f"[WARN] Failed to save taxonomy cache: {pe}")

        elif matched_type == "SECURITY_TRIAGE":
            sec_cache_file = os.path.join(ORION_DIR, "working", "security_llm_cache.json")
            try:
                os.makedirs(os.path.dirname(sec_cache_file), exist_ok=True)
                s_data = {}
                if os.path.exists(sec_cache_file):
                    with open(sec_cache_file, "r", encoding="utf-8") as sf:
                        s_data = json.load(sf)
                if isinstance(parsed_result, list):
                    for item in parsed_result:
                        ik = item.get("fingerprint") or item.get("cache_key") or str(len(s_data))
                        s_data[ik] = item
                elif isinstance(parsed_result, dict):
                    ik = parsed_result.get("fingerprint") or parsed_result.get("cache_key") or "latest"
                    s_data[ik] = parsed_result
                atomic_write_text(sec_cache_file, json.dumps(s_data, indent=2))
                print(f"[SUCCESS] Injected security triage verdict into {sec_cache_file}.")
            except Exception as se:
                print(f"[WARN] Failed to save security triage cache: {se}")

        elif matched_type == "EXTRACT_GRAPH_TRIPLETS":
            try:
                inject_triplets(raw_json)
                clear_cloud_handoff("EXTRACT_GRAPH_TRIPLETS")
                print("[SUCCESS] Injected triplets and cleared EXTRACT_GRAPH_TRIPLETS handoff.")
                return 0
            except Exception as te:
                print(f"[ERROR] Failed to inject triplets: {te}")
                return 1

        if target_ref.startswith("handoff_"):
            cleared = clear_cloud_handoff(matched_type, match_fn=lambda t: t.get("id") == target_ref)
        else:
            cleared = clear_cloud_handoff(matched_type)
        print(f"[SUCCESS] Resolved and cleared {cleared} handoff task(s) for '{target_ref}'.")
        return 0

    elif action in ("clear", "clean", "purge"):
        target_type = sub_args[1] if len(sub_args) > 1 else "ALL"
        cleared = clear_cloud_handoff(target_type)
        print(f"[CLOUD HANDOFF] Cleared {cleared} pending handoff task(s) for '{target_type}'.")
        return 0

    else:
        print(f"Unknown handoff action: '{action}'. Available: list, show, resolve, clear.")
        return 1


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
        print("  handoff <action>          - Cloud Agent LLM handoff queue (list|show|resolve|clear)")
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
        return vault_main(["export"] + sub_args)
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
    elif cmd in ("handoff", "cloud_handoff", "cloud-handoff"):
        return handoff_main(sub_args)
    else:
        # Default fallback to sync
        return sync(" ".join(argv), delta=False)

if __name__ == "__main__":
    sys.exit(main() or 0)
