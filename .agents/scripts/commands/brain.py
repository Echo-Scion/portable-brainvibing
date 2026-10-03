import argparse
import os
import re
import sys
import json
import urllib.request
import subprocess
from pathlib import Path

# Force utf-8 encoding for standard output to avoid UnicodeEncodeError on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

try:
    import psutil
except ImportError:
    psutil = None

def detect_hardware():
    """
    Detect host hardware specifications:
    - System RAM in GB (via psutil)
    - CUDA GPU VRAM in GB (via nvidia-smi or torch)
    Returns: dict with {ram_gb, vram_gb, is_high_capacity, gpu_name}
    """
    ram_gb = 0.0
    if psutil:
        try:
            ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        except Exception:
            pass

    vram_gb = 0.0
    gpu_name = ""
    # Try nvidia-smi
    try:
        cmd = ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits']
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
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
    except Exception:
        pass

    if vram_gb == 0.0:
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                vram_gb = sum(torch.cuda.get_device_properties(i).total_memory for i in range(torch.cuda.device_count())) / (1024 ** 3)
        except Exception:
            pass

    # Apple Silicon Graceful Fallback (Unified Memory)
    if vram_gb == 0.0 and sys.platform == "darwin":
        try:
            import platform
            if platform.machine() == "arm64":
                gpu_name = "Apple Silicon (Unified Memory)"
                # Apple allows ~70-75% of unified memory for GPU
                vram_gb = ram_gb * 0.7 
        except Exception:
            pass

    is_high_capacity = (ram_gb > 24.0 and vram_gb >= 12.0)
    return {
        "ram_gb": round(ram_gb, 2),
        "vram_gb": round(vram_gb, 2),
        "is_high_capacity": is_high_capacity,
        "gpu_name": gpu_name
    }

# --- Centralized Ollama URL Resolution (Dual-Stack Fallback + Self-Heal) ---
_RESOLVED_OLLAMA_BASE_URL = None  # Module-level cache

def _probe_url(url, timeout=1.0):
    """Attempt a lightweight HTTP GET to check if a URL is reachable."""
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False

def resolve_ollama_base_url(force_refresh=False):
    """
    Resolves the best reachable Ollama base URL using a dual-stack fallback strategy:
      1. User override via ORION_LLM_URL env var (extracted base)
      2. IPv4 loopback (fastest on Windows, avoids IPv6 SYN timeout)
      3. IPv6 loopback (preferred on some Linux distros)
      4. OS-resolved 'localhost' (last resort, may trigger dual-stack delay)

    Self-Healing: On first successful probe, caches the result for the process lifetime.
    If the .env file still contains an unreachable URL, writes back the working URL.
    
    Returns: base URL string like "http://127.0.0.1:11434" or None if Ollama is offline.
    """
    global _RESOLVED_OLLAMA_BASE_URL
    if _RESOLVED_OLLAMA_BASE_URL is not None and not force_refresh:
        return _RESOLVED_OLLAMA_BASE_URL

    # Extract base from env var (strip /api/generate suffix if present)
    env_url = os.environ.get("ORION_LLM_URL", "")
    env_base = env_url.replace("/api/generate", "").replace("/api/embeddings", "").rstrip("/") if env_url else ""

    # Build ordered candidate list: env override first, then standard fallbacks
    candidates = []
    if env_base:
        candidates.append(env_base)
    
    standard_fallbacks = [
        "http://127.0.0.1:11434",   # IPv4 loopback (fastest on Windows)
        "http://[::1]:11434",         # IPv6 loopback (some Linux defaults)
        "http://localhost:11434",     # OS-resolved (last resort)
    ]
    for fb in standard_fallbacks:
        if fb not in candidates:
            candidates.append(fb)

    for url in candidates:
        if _probe_url(url + "/", timeout=1.0):
            _RESOLVED_OLLAMA_BASE_URL = url
            # Self-heal: update ORION_LLM_URL env var for child processes
            os.environ["ORION_LLM_URL"] = url + "/api/generate"
            _self_heal_env_file(url)
            return url

    # All candidates failed — Ollama is offline
    _RESOLVED_OLLAMA_BASE_URL = None
    return None

def _self_heal_env_file(working_base_url):
    """
    If the .env file contains an ORION_LLM_URL that differs from the working URL,
    update it silently. This ensures the NEXT process startup uses the known-good URL
    without needing another probe cycle.
    """
    try:
        # Locate .env relative to this script: commands/ -> scripts/ -> .agents/ -> project_root/
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
        env_path = os.path.join(project_root, '.env')
        
        if not os.path.exists(env_path):
            return
        
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_value = f"ORION_LLM_URL={working_base_url}/api/generate\n"
        found = False
        changed = False
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("ORION_LLM_URL=") and not stripped.startswith("#"):
                found = True
                if stripped != new_value.strip():
                    new_lines.append(new_value)
                    changed = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(new_value)
            changed = True
        
        if changed:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
    except Exception:
        pass  # Silently degrade — .env writeback is best-effort

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
    agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    manifest_path = os.path.join(agents_dir, ".project_manifest.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                configured_model = manifest.get("llm_profile", {}).get("model")
                if configured_model:
                    return configured_model.strip()
        except Exception:
            pass

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

    agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    status_file = os.path.join(agents_dir, ".nanobrain_status")
    genome_path = os.path.join(agents_dir, ".genome.json")

    is_high = force_high_capacity or hw_info.get("is_high_capacity", False)
    chosen_model = select_optimal_local_model(hw_info, force_high_capacity=force_high_capacity)

    if is_high:
        try:
            with open(status_file, "w", encoding="utf-8") as f:
                f.write("FULL")
        except Exception:
            pass

        if os.path.exists(genome_path):
            try:
                with open(genome_path, "r", encoding="utf-8") as f:
                    genome = json.load(f)
                genome["daily_mutation_cap"] = 10
                with open(genome_path, "w", encoding="utf-8") as f:
                    json.dump(genome, f, indent=2)
            except Exception:
                pass

        return {
            "tier": "TITAN_HIGH_CAPACITY",
            "model": chosen_model,
            "status": "FULL",
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
            except Exception:
                pass

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
        except Exception:
            pass

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
            except Exception:
                pass

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

        agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
            except Exception:
                pass

    def check_tier(self, required_level, feature_name):
        if self.tier_level < required_level:
            return f"[DELEGATE_TO_CLOUD] Error: Required Medium Intelligence (or higher) for {feature_name}. Current tier is '{self.tier_name}'. Fallback gracefully to Cloud Agent LLM."
        return None

    def ping(self, capability="ANY"):
        agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
            except Exception:
                pass
                
        if state == "OFF":
            return False
            
        if capability != "ANY" and state != "FULL":
            if capability == "EMBED" and state != "EMBED": return False
            if capability == "LLM" and state != "LLM": return False

        if psutil:
            try:
                mem = psutil.virtual_memory()
                if mem.percent > 90:
                    print(f"\n[WARNING] System RAM at {mem.percent}%. Disabling NanoBrain to prevent lockup.")
                    return False
            except Exception:
                pass
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
            with urllib.request.urlopen(req, timeout=60) as r:
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

    def caveman_compress(self, text):
        system = "You are an English compression engine. You MUST output ONLY in English. Do not use any other languages. Use terse, telegraphic fragments."
        prompt = f"Convert this text to English Caveman Mode (terse, fragment sentences, 100% technical facts):\n\nTEXT: {text}\n\nENGLISH CAVEMAN OUTPUT:"
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

def cosine_similarity(v1, v2):
    import math
    if not v1 or not v2 or len(v1) != len(v2): return 0.0
    dot_product = sum(x*y for x,y in zip(v1,v2))
    mag1 = math.sqrt(sum(x*x for x in v1))
    mag2 = math.sqrt(sum(y*y for y in v2))
    if mag1 == 0 or mag2 == 0: return 0.0
    return dot_product / (mag1 * mag2)

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
                return list(set(base_keywords + expanded_words))
    except Exception:
        pass
        
    return base_keywords

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
            except Exception:
                pass
                
    matches.sort(reverse=True, key=lambda x: x[0])
    return [m[1] for m in matches[:3]]

def get_ast_block(filepath, tag_name):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(f'<{tag_name}>(.*?)</{tag_name}>', content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return None

def sync(intent, delta=False):
    print(f" NEURO-LINK ENGAGED: Syncing Brain for intent: '{intent}'")
    keywords = extract_keywords(intent)
    print(f" Extracted Tokens: {keywords}")
    
    agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    workspace_dir = os.path.dirname(agents_dir)
    orion_dir = os.path.join(workspace_dir, '.orion')
    context_dir = os.path.join(workspace_dir, 'context')
    
    skills = search_files(os.path.join(agents_dir, 'skills'), keywords)
    
    # Rute Semantic via LightRAG (SQLite FTS5 BM25)
    rules = []
    db_path = os.path.join(orion_dir, 'orion.db')
    cache_path = os.path.join(orion_dir, 'working', 'cache.json')
    query_str = " OR ".join([f'"{kw}"' for kw in keywords])

    cache_data = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
        except Exception:
            pass

    if query_str in cache_data and not delta:
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
        except Exception:
            pass

        if os.path.exists(db_path):
            import sqlite3
            try:
                conn = sqlite3.connect(db_path)
                conn.execute('PRAGMA busy_timeout=5000;')
                c = conn.cursor()
                
                scored_paths = {}
                
                # 1. FTS5 (Lexical)
                c.execute('SELECT path FROM pages_fts WHERE pages_fts MATCH ? ORDER BY rank LIMIT 5', (query_str,))
                for idx, row in enumerate(c.fetchall()):
                    path = row[0]
                    scored_paths[path] = 0.9 - (idx * 0.1) # Baseline lexical score

                # 2. Vector Search (Semantic)
                if query_embedding:
                    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='page_embeddings'")
                    if c.fetchone():
                        vector_results = []
                        offset = 0
                        limit = 1000
                        while True:
                            c.execute("SELECT path, embedding_json FROM page_embeddings LIMIT ? OFFSET ?", (limit, offset))
                            rows = c.fetchall()
                            if not rows:
                                break
                            for row in rows:
                                path = row[0]
                                try:
                                    emb = json.loads(row[1])
                                    sim = cosine_similarity(query_embedding, emb)
                                    if sim > 0.4: # Context semantic threshold
                                        vector_results.append((path, sim))
                                except Exception:
                                    pass
                            offset += limit
                            if offset > 10000: # OOM Fail-safe limit
                                break
                        
                        vector_results.sort(key=lambda x: x[1], reverse=True)
                        for path, sim in vector_results[:3]:
                            if path in scored_paths:
                                scored_paths[path] += sim # Hybrid boost
                            else:
                                scored_paths[path] = sim
                                
                # Resolve final top 3 paths (Cross-Encoder Re-Ranking on High-Capacity hardware)
                if temp_nb and getattr(temp_nb, 'use_cross_encoder', False):
                    candidate_pool = sorted(scored_paths.keys(), key=lambda k: scored_paths[k], reverse=True)[:5]
                    final_paths = cross_encoder_rerank(intent, candidate_pool, nanobrain=temp_nb)[:3]
                    print(f"  [CROSS-ENCODER] Re-ranked {len(final_paths)} candidate paths via TitanBrain profile.")
                else:
                    final_paths = sorted(scored_paths.keys(), key=lambda k: scored_paths[k], reverse=True)[:3]

                for path in final_paths:
                    if "archive/" in path.replace("\\", "/").lower():
                        import shutil
                        normalized_path = path.replace("\\", "/")
                        parts = normalized_path.split("archive/")
                        rel_path = parts[1] if len(parts) > 1 else os.path.basename(path)
                        dest = os.path.join(agents_dir, rel_path)
                        try:
                            if os.path.exists(path):
                                os.makedirs(os.path.dirname(dest), exist_ok=True)
                                if os.path.isdir(path):
                                    shutil.copytree(path, dest, dirs_exist_ok=True)
                                else:
                                    shutil.copy(path, dest)
                                print(f"  [AMNESIA RECALL] JIT Retrieved asset '{rel_path}' from archive!")
                            rules.append(dest)
                        except Exception as e:
                            print(f"  [AMNESIA ERROR] Could not recall {rel_path}: {e}")
                    else:
                        rules.append(path)
                        
                    # --- IDE-4: Smart Memory Compression ---
                    try:
                        c.execute("UPDATE pages SET access_count = IFNULL(access_count, 0) + 1, last_accessed = datetime('now') WHERE path = ?", (path,))
                        conn.commit()
                    except Exception:
                        pass
                conn.close()
    
                cache_data[query_str] = rules
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f)
            except Exception as e:
                print(f"  [ERROR] LightRAG Query Failed: {e}")
            
    wiki_nodes = search_files(orion_dir, keywords)
    saas_nodes = search_files(context_dir, keywords)
    
    print("\n" + "="*60)
    if delta:
        print(" DELTA CONTEXT PACKET (LIGHTRAG-HARMONIZED) - Continuous RAG")
    else:
        print(" UNIFIED CONTEXT PACKET (LIGHTRAG-HARMONIZED)")
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
            except Exception:
                pass
                
            for line in rules_content.split('\n'):
                if not line.strip() or line.startswith('#'):
                    continue
                line_lower = line.lower()
                
                # Global rules always apply
                if "global" in line_lower:
                    matches.append(line.strip())
                    continue
                    
                is_match = False
                # Semantic filter via NanoBrain
                if nb:
                    sys_prompt = "You are a binary classifier. Answer ONLY with YES or NO. Is the RULE relevant to the INTENT?"
                    prompt = f"INTENT: {intent}\nRULE: {line.strip()}\nRelevant (YES/NO):"
                    try:
                        resp = nb.generate(prompt, system=sys_prompt)
                        if resp and "YES" in resp.upper():
                            is_match = True
                    except Exception: pass
                    
                # Fallback to lexical
                if not is_match and any(kw in line_lower for kw in keywords):
                    is_match = True
                    
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
        for r in (rules + skills)[:3]:
            rel_path = os.path.relpath(r, workspace_dir)
            print(f"- [Mandatory Execution Protocol]: {rel_path}")
            
            # Apply NanoBrain compression ONLY to .md rules/skills
            if r.endswith('.md'):
                try:
                    with open(r, "r", encoding="utf-8") as f:
                        content = f.read()
                    if len(content) < 4000: # Limit size to prevent 0.5b timeout
                        if nb and nb.ping():
                            compressed = nb.caveman_compress(content)
                            if compressed and len(compressed) > 10:
                                print(f"  [COMPRESSED CONTEXT]: {compressed.replace(chr(10), ' ')}")
                except Exception:
                    pass
            
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
        except Exception:
            pass
            
    if wiki_hits:
        print("\n##  Deep RAG (Orion Graph Hits)")
        print(f"  Found potential nodes: {', '.join(wiki_hits[:3])}")
        top_node = wiki_hits[0]
        print(f"  [AUTO-RAG]: Resolving primary node '{top_node}' automatically...\n")
        try:
            import subprocess
            ops_script = os.path.join(agents_dir, "scripts", "orion.py")
            # We output directly instead of capturing so it prints immediately in sync stream
            subprocess.run([sys.executable, ops_script, "orion_ops", "resolve", top_node], check=True)
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
                except Exception:
                    pass
            
            if mtime > last_mtime:
                stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                if age_hours > 48:
                    print(f"  [WARNING] Handoff is {age_hours:.0f}h old. May be stale. Archiving with STALE prefix.")
                    shutil.copy2(handoff_path, os.path.join(episodic_dir, f"STALE_handoff_{stamp}.md"))
                else:
                    shutil.copy2(handoff_path, os.path.join(episodic_dir, f"handoff_{stamp}.md"))
                    print("  [INFO] Handoff backed up to episodic memory.")
                
                with open(archive_marker, "w") as mf:
                    mf.write(str(mtime))
        except Exception as e:
            print(f"  [ERROR] Failed to process working memory: {e}")
    # --------------------------------------------

    if saas_nodes:
        print("\n##  Working Memory (SaaS State)")
        for s in saas_nodes:
            rel_path = os.path.relpath(s, workspace_dir)
            print(f"- [Active State]: {rel_path}")
            if get_ast_block(s, 'saas-state'):
                print("  [DATA-NODE]: Extracted semantic state successfully.")
    
    if not (skills or rules or wiki_nodes or saas_nodes):
        print("\n[WARNING]: No contextual nodes found for these tokens. AI must rely on zero-shot reasoning.")
        
    print("\n---\n[DIRECTIVE] Read the above files with `view_file` BEFORE modifying code. Adhere to rules. Proceed.")

def page_context(keywords):
    agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
                        import sys
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        if script_dir not in sys.path:
                            sys.path.insert(0, script_dir)
                        from compile_rules import parse_markdown_to_dict
                        
                        for chunk in chunks:
                            chunk_lower = chunk.lower()
                            if any(kw.lower() in chunk_lower for kw in keywords):
                                header_match = re.match(r'(#+ .*?)\n', chunk)
                                header = header_match.group(1) if header_match else f"Excerpt from {file}"
                                
                                # Ephemeral Caveman Compilation
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
                except Exception:
                    pass
                    
    with open(page_path, "w", encoding="utf-8") as f:
        f.write("# Ephemeral Pager Context\n\n")
        f.write("\n---\n".join(relevant_chunks))
        
    print(f"Paging complete. {len(relevant_chunks)} chunks swapped into {os.path.relpath(page_path, workspace_dir)}")


def main():
    parser = argparse.ArgumentParser(description="Neuro-Link Brain Engine")
    subparsers = parser.add_subparsers(dest='command')
    
    sync_parser = subparsers.add_parser('sync', help='Sync brain context')
    sync_parser.add_argument('intent', type=str, help='The task or intent')
    sync_parser.add_argument('--delta', action='store_true', help='Only fetch new info without pulling full global rules')
    
    nb_parser = subparsers.add_parser('nanobrain', help='Execute NanoBrain tasks')
    nb_parser.add_argument('action', choices=['vibe_check', 'extract', 'compress', 'draft', 'on', 'off', 'embed_only', 'llm_only', 'status'], help='Action to perform')
    nb_parser.add_argument('text', nargs='?', type=str, default='', help='Input text')
    
    page_parser = subparsers.add_parser('page', help='Ephemeral context slicer')
    page_parser.add_argument('keywords', nargs='+', help='Keywords to extract')
    
    autoscale_parser = subparsers.add_parser('autoscale', aliases=['hardware'], help='Detect hardware and apply auto-scale profile')
    autoscale_parser.add_argument('--simulate-ideal', action='store_true', help='Simulate Ideal PC (>24GB RAM & >=12GB VRAM)')

    args = parser.parse_args()
    if args.command == 'sync':
        sync(args.intent, getattr(args, 'delta', False))
    elif args.command in ('autoscale', 'hardware'):
        hw = detect_hardware()
        print(f" Detected RAM: {hw['ram_gb']} GB")
        print(f" Detected GPU VRAM: {hw['vram_gb']} GB ({hw['gpu_name'] or 'No dedicated GPU'})")
        sim = getattr(args, 'simulate_ideal', False)
        if sim:
            print(" [SIMULATION] Simulating Ideal PC (>24GB RAM & >=12GB VRAM)...")
        profile = apply_auto_scale_profile(hw, force_high_capacity=sim)
        print(f" Auto-Scale Tier: {profile['tier']}")
        print(f" Selected Model: {profile['model']}")
        print(f" NanoBrain Status: {profile['status']}")
        print(f" Daily Mutation Cap: {profile['daily_mutation_cap']}")
        print(f" Cross-Encoder Re-Ranking: {'ENABLED' if profile['use_cross_encoder'] else 'DISABLED'}")
        return
    elif args.command == 'nanobrain':
        agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        status_file = os.path.join(agents_dir, ".nanobrain_status")
        
        if args.action == 'on':
            with open(status_file, "w") as f: f.write("FULL")
            print("🟢 NanoBrain is now FULLY ENABLED (LLM + EMBED).")
            return
        elif args.action == 'off':
            with open(status_file, "w") as f: f.write("OFF")
            print("🔴 NanoBrain is now DISABLED.")
            return
        elif args.action == 'embed_only':
            with open(status_file, "w") as f: f.write("EMBED")
            print("🟢 NanoBrain is now EMBED mode (Vector Search Active, Generative AI Off).")
            return
        elif args.action == 'llm_only':
            with open(status_file, "w") as f: f.write("LLM")
            print("🟢 NanoBrain is now LLM-ONLY (Generative AI Active, Vector Search Off).")
            return
        elif args.action == 'status':
            state = "FULL"
            if os.path.exists(status_file):
                with open(status_file, "r") as f: state = f.read().strip().upper()
            print(f"NanoBrain Toggle: {state}")
            return

        nb = NanoBrain()
        if not nb.ping():
            print("Error: NanoBrain is DISABLED or Ollama is not reachable on any endpoint (tried IPv4, IPv6, localhost)")
            return
            
        if args.action == 'vibe_check':
            print(nb.vibe_check(args.text))
        elif args.action == 'extract':
            print(nb.extract_triplets(args.text))
        elif args.action == 'compress':
            print(nb.caveman_compress(args.text))
        elif args.action == 'draft':
            print(nb.draft_boilerplate(args.text))
    elif args.command == 'page':
        page_context(args.keywords)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
