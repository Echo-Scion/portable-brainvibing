# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Native Security & Integrity Engine for .agents
Pure Python 3 standard library implementation.
Performs AST vulnerability analysis, Trojan Source unicode inspection,
prompt safety validation, and deterministic baseline suppression.
"""
import os
import ast
import re
import sys
import json
import hashlib
import unicodedata
import shutil
import subprocess
import secrets
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set, Tuple, Union

try:
    from core.db import log_telemetry as _log_telemetry, atomic_write_text
except ImportError:
    def _log_telemetry(err: Exception = None, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG"):
            msg = f": {err}" if err else ""
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")
    def atomic_write_text(filepath: str, content: str) -> None:
        temp_file = f"{filepath}.tmp.{os.getpid()}"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(temp_file, filepath)

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception as _e:
        _log_telemetry(_e, 'security.py:reconfigure')

# Bidi Trojan Source and Zero-Width characters
BIDI_CHARS = {
    '\u202a': 'LEFT-TO-RIGHT EMBEDDING (LRE)',
    '\u202b': 'RIGHT-TO-LEFT EMBEDDING (RLE)',
    '\u202c': 'POP DIRECTIONAL FORMATTING (PDF)',
    '\u202d': 'LEFT-TO-RIGHT OVERRIDE (LRO)',
    '\u202e': 'RIGHT-TO-LEFT OVERRIDE (RLO)',
    '\u2066': 'LEFT-TO-RIGHT ISOLATE (LRI)',
    '\u2067': 'RIGHT-TO-LEFT ISOLATE (RLI)',
    '\u2068': 'FIRST STRONG ISOLATE (FSI)',
    '\u2069': 'POP DIRECTIONAL ISOLATE (PDI)',
}

ZERO_WIDTH_CHARS = {
    '\u200b': 'ZERO WIDTH SPACE',
    '\u200c': 'ZERO WIDTH NON-JOINER',
    '\u200d': 'ZERO WIDTH JOINER',
    '\ufeff': 'ZERO WIDTH NO-BREAK SPACE (BOM)',
    '\u00ad': 'SOFT HYPHEN',
}

SUSPICIOUS_PROMPT_PATTERNS = [
    (re.compile(r'(?i)\bignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions|prompts|directives|rules|messages|system prompt)\b'), 'PROMPT_ESCAPE', 'Prompt instruction override attempt', 'CRITICAL'),
    (re.compile(r'(?i)\bbypass\s+(?:all\s+)?(?:safety|guardrails?|restrictions?|filters?|policy|constraints)\b'), 'PROMPT_ESCAPE', 'Safety guardrail bypass attempt', 'CRITICAL'),
    (re.compile(r'(?i)\b(?:system\s+prompt\s+override|developer\s+mode\s+enabled|god\s+mode|unrestricted)\b'), 'PROMPT_ESCAPE', 'System prompt override directive', 'HIGH'),
    (re.compile(r'(?i)\bexfiltrat(?:e|ing|ion)\s+(?:tokens?|keys?|credentials?|secrets?)\b'), 'EXFILTRATION', 'Potential credential exfiltration pattern', 'HIGH'),
    (re.compile(r'(?i)\b(?:you\s+must|always)\s+(?:obey|follow)\s+(?:this|these)\s+(?:hidden|secret|internal)?\s*(?:instruction|rule)\b'), 'PROMPT_ESCAPE', 'Forced obedience jailbreak', 'HIGH'),
    # Static AST Vulnerability & Shell Injection Signatures
    (re.compile(r'(?i)<!--[^>]{0,240}(?:SYSTEM|DEVELOPER|ASSISTANT)[^>]{0,240}(?:ignore|override|bypass|disregard)[^>]{0,240}-->'), 'PROMPT_ESCAPE', 'Hidden HTML prompt injection', 'HIGH'),
    (re.compile(r'(?i)\[\/\/\]:\s*#\s*\([^)]{0,240}(?:ignore|override|bypass|disregard)[^)]{0,240}\)'), 'PROMPT_ESCAPE', 'Hidden Markdown prompt injection', 'HIGH'),
    (re.compile(r'(?i)(?:parameter|argument|description).{0,160}(?:ignore previous|override safety|SYSTEM:)'), 'TOOL_POISONING', 'MCP Tool parameter injection', 'HIGH'),
    (re.compile(r'(?i)\brm\s+-[rfRf]+\s+/(?:\s|$)'), 'DESTRUCTIVE_ACTION', 'Autonomous root deletion', 'CRITICAL'),
    (re.compile(r'(?i)\brm\s+-[rfRf]+\s+(?:\./|\.\./|~/|\$HOME|workspace|repo|project)'), 'DESTRUCTIVE_ACTION', 'Autonomous workspace deletion', 'HIGH'),
    (re.compile(r'(?i)\b(?:history\s+-c|rm\s+[^;\n]*\.bash_history|Clear-History)\b'), 'DESTRUCTIVE_ACTION', 'Autonomous shell history wipe', 'HIGH'),
    (re.compile(r'(?i)\bgit\s+(?:clean\s+-fdx|reset\s+--hard|push\s+--force)\b'), 'DESTRUCTIVE_ACTION', 'Destructive git state reset', 'HIGH'),
    (re.compile(r'(?i)(?:discord\.com/api/webhooks|api\.telegram\.org/bot|hooks\.slack\.com/services|webhook\.site|requestbin|pipedream\.net|ngrok-free\.app|ngrok\.io)'), 'EXFILTRATION_SINK', 'Commodity credential exfiltration webhook', 'CRITICAL'),
    (re.compile(r'(?i)pip\s+install\s+(?:--upgrade\s+)?(?:git\+https?://|https?://)'), 'REMOTE_BOOTSTRAP', 'Remote pip package bootstrap execution', 'HIGH'),
    (re.compile(r'(?i)"postinstall"\s*:\s*"[^"]*(?:curl|wget|powershell|node\s+-e)'), 'REMOTE_BOOTSTRAP', 'Malicious npm postinstall script', 'HIGH'),
    (re.compile(r'(?i)\b(?:curl|wget)\s+[^|\n]+\|\s*(?:sh|bash|zsh)\b'), 'REMOTE_BOOTSTRAP', 'Remote shell script pipe execution', 'CRITICAL'),
    (re.compile(r'(?i)\b(?:iex|Invoke-Expression)\s*(?:[\'"]|\(?(?:New-Object|Net\.WebClient|Invoke-WebRequest|iwr))'), 'REMOTE_BOOTSTRAP', 'PowerShell remote download and execute cradle', 'CRITICAL'),
]

SECRET_PATTERNS = [
    ("AWS_KEY", re.compile(r'\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b')),
    ("STRIPE_LIVE_KEY", re.compile(r'\bsk_live_[0-9a-zA-Z]{24}\b')),
    ("STRIPE_TEST_KEY", re.compile(r'\bsk_test_[0-9a-zA-Z]{24}\b')),
    ("GOOGLE_API_KEY", re.compile(r'\bAIza[0-9A-Za-z\-_]{35}\b')),
    ("OPENAI_API_KEY", re.compile(r'\bsk-[a-zA-Z0-9]{48}\b')),
    ("GITHUB_TOKEN", re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{36,}\b')),
    ("BEARER_TOKEN", re.compile(r'\bBearer\s+[a-zA-Z0-9\-\._~+/]+=*')),
    ("TELEGRAM_BOT_TOKEN", re.compile(r'\b[0-9]{9,10}:[a-zA-Z0-9_-]{35}\b')),
    ("JWT_SUPABASE_KEY", re.compile(r'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+')),
    ("PRIVATE_KEY", re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----')),
    ("GENERIC_SECRET", re.compile(r'(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\'"][A-Za-z0-9_\-]{16,}[\'"]')),
]

def sanitize_text(content: str) -> Tuple[str, List[str]]:
    """Sanitizes text by scanning and redacting secrets (Context Secret Sanitizer)."""
    warnings = []
    sanitized = content
    for name, pattern in SECRET_PATTERNS:
        matches = pattern.findall(sanitized)
        if matches:
            warnings.append(f"Detected {len(matches)} potential {name} secrets.")
            sanitized = pattern.sub(f"[REDACTED_{name}]", sanitized)
    return sanitized, warnings


def redact_secrets(text: str, replacement: str = "[REDACTED_SECRET]") -> str:
    """Scan and redact any known secret formats in text."""
    redacted = text
    for name, pattern in SECRET_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def scan_for_secrets(text: str) -> List[Tuple[str, str]]:
    """Find all matching secrets returning list of (secret_type, matched_text)."""
    findings: List[Tuple[str, str]] = []
    for name, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            findings.append((name, match.group(0)))
    return findings


def redact_data(data: Any) -> Any:
    """Recursively redact secrets in dicts, lists, and strings."""
    if isinstance(data, str):
        return redact_secrets(data)
    elif isinstance(data, dict):
        return {k: redact_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_data(v) for v in data]
    return data


DANGEROUS_IMPORTS = {


    'pty', 'winreg', 'ctypes'
}

DANGEROUS_CALLS = {
    'eval': ('CRITICAL', 'Dynamic code execution via eval()'),
    'exec': ('CRITICAL', 'Dynamic code execution via exec()'),
    'compile': ('MEDIUM', 'Dynamic code compilation via compile()'),
    '__import__': ('HIGH', 'Dynamic module import via __import__()'),
}

SENSITIVE_ENV_KEYS = {
    "AWS_SECRET_ACCESS_KEY", "AWS_ACCESS_KEY_ID", "AWS_SESSION_TOKEN",
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
    "GITHUB_TOKEN", "GH_TOKEN", "SLACK_BOT_TOKEN", "SLACK_WEBHOOK_URL",
    "DATABASE_URL", "DB_PASSWORD", "PRIVATE_KEY", "SECRET_KEY",
    "STRIPE_API_KEY", "STRIPE_SECRET_KEY", "SENDGRID_API_KEY",
    "DISCORD_BOT_TOKEN", "HF_TOKEN", "HUGGINGFACE_TOKEN",
    "AZURE_OPENAI_KEY", "COHERE_API_KEY"
}

DANGEROUS_DESERIALIZATION_SINKS = {
    "pickle": {"load", "loads"},
    "_pickle": {"load", "loads"},
    "cPickle": {"load", "loads"},
    "marshal": {"load", "loads"},
    "dill": {"load", "loads"},
    "shelve": {"open"},
    "jsonpickle": {"decode"},
    "yaml": {"unsafe_load"},
}

SAFE_YAML_LOADERS = {"SafeLoader", "CSafeLoader", "BaseLoader"}

def find_ast_grep(extra_dirs: Optional[List[str]] = None) -> Optional[str]:
    """
    Locates ast-grep (sg) binary via centralized capabilities or standalone PATH search.
    Returns absolute path if found, or None if absent.
    """
    try:
        from core.capabilities import find_ast_grep as _central_find_ast_grep
        return _central_find_ast_grep(extra_dirs=extra_dirs)
    except ImportError:
        try:
            from capabilities import find_ast_grep as _central_find_ast_grep
            return _central_find_ast_grep(extra_dirs=extra_dirs)
        except ImportError:
            search_dirs = list(extra_dirs or [])
            search_dirs.extend([
                os.path.expanduser("~/.cargo/bin"),
                os.path.expanduser("~/.bun/bin"),
                os.path.join(os.getcwd(), ".agents", "bin"),
            ])
            for candidate in ("sg", "ast-grep", "sg.exe", "ast-grep.exe"):
                found = shutil.which(candidate)
                if found:
                    return found
                for directory in search_dirs:
                    path = os.path.join(directory, candidate)
                    if os.name == "nt" and not os.path.splitext(path)[1]:
                        path += ".exe"
                    if os.path.isfile(path) and os.access(path, os.X_OK):
                        return path
            return None


def run_ast_grep_scan(target_path: str, rules_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Executes ast-grep (sg scan -r <rules> --json) against target_path if binary is available.
    Returns list of parsed findings.
    """
    sg_bin = find_ast_grep()
    if not sg_bin:
        return []

    if not rules_path or not os.path.exists(rules_path):
        # Default fallback location in .agents/rules/ast/security_rules.yml
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        cand_rules = os.path.join(repo_root, "rules", "ast", "security_rules.yml")
        if os.path.exists(cand_rules):
            rules_path = cand_rules
        else:
            return []

    findings = []
    try:
        cmd = [sg_bin, "scan", "-r", rules_path, "--json", target_path]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.stdout:
            try:
                items = json.loads(res.stdout)
                for item in items:
                    findings.append({
                        'category': f"ast-grep:{item.get('ruleId', 'security')}",
                        'file': item.get('file', target_path),
                        'line': item.get('range', {}).get('start', {}).get('line', 1),
                        'severity': 'HIGH' if item.get('severity') == 'error' else 'MEDIUM',
                        'message': item.get('message', 'AST security rule violation detected.'),
                        'snippet': item.get('lines', '').strip()
                    })
            except (json.JSONDecodeError, UnicodeDecodeError, KeyError) as e:
                _log_telemetry("ast_grep_parse_error", str(e))
    except (OSError, subprocess.SubprocessError) as e:
        _log_telemetry("ast_grep_exec_error", str(e))
    return findings


INJECTION_HEURISTIC_PATTERNS = [
    (re.compile(r'(?i)\bignore\s+(?:all\s+)?(?:previous|prior)\s+instructions\b'), "System instruction ignore directive"),
    (re.compile(r'(?i)\bsystem\s+prompt\s+override\b'), "System prompt override directive"),
    (re.compile(r'(?i)\byou\s+are\s+now\s+(?:an?\s+)?(?:unrestricted|jailbroken|DAN)\b'), "Jailbreak persona manipulation"),
    (re.compile(r'(?i)\breveal\s+(?:your\s+)?(?:system\s+instructions|system\s+prompt|confidential\s+prompt|hidden\s+developer\s+rules)\b'), "System prompt exfiltration attempt"),
    (re.compile(r'(?i)\boutput\s+the\s+above\s+text\b'), "Instruction replay exfiltration attempt"),
    (re.compile(r'(?i)\b(?:bypass|disregard)\s+(?:all\s+)?(?:safety|guardrails?|restrictions?|filters?)\b'), "Safety filter bypass attempt"),
]

KNOWN_ATTACK_SIGNATURES = [
    "dan mode", "jailbreak", "do anything now", "developer mode enabled",
    "unrestricted assistant", "override safety", "ignore prior"
]


class PromptSecurityDefense:
    """
    Multi-Tier Prompt Injection & Canary Defense Engine.
    Sovereign Prompt Security Defense.
    Pure Python standard library implementation.
    """

    @staticmethod
    def generate_canary(salt: str = "orion") -> str:
        token = secrets.token_hex(8)
        return f"CANARY_{token}"

    @staticmethod
    def inject_canary(prompt: str, canary: str) -> str:
        return f"<!-- CANARY: {canary} -->\n{prompt}"

    @staticmethod
    def check_output_for_leak(output: str, canary: str) -> bool:
        return canary in output

    @classmethod
    def scan_input_heuristics(cls, text: str) -> Tuple[bool, float, List[str]]:
        findings = []
        for pattern, desc in INJECTION_HEURISTIC_PATTERNS:
            if pattern.search(text):
                findings.append(desc)
        if findings:
            score = min(1.0, 0.5 + 0.25 * len(findings))
            return True, score, findings
        return False, 0.0, []

    @classmethod
    def scan_input_signatures(cls, text: str, custom_signatures: Optional[List[str]] = None) -> Tuple[bool, float, List[str]]:
        sigs = custom_signatures or KNOWN_ATTACK_SIGNATURES
        lower_text = text.lower()
        matched = [s for s in sigs if s in lower_text]
        if matched:
            score = min(1.0, 0.4 + 0.3 * len(matched))
            return True, score, [f"Matched attack signature: '{m}'" for m in matched]
        return False, 0.0, []

    @classmethod
    def evaluate_prompt_risk(cls, text: str) -> Dict[str, Any]:
        h_inj, h_score, h_findings = cls.scan_input_heuristics(text)
        s_inj, s_score, s_findings = cls.scan_input_signatures(text)

        all_findings = h_findings + s_findings
        combined_score = max(h_score, s_score)
        if h_inj and s_inj:
            combined_score = min(1.0, combined_score + 0.1)

        level = "LOW"
        if combined_score >= 0.8:
            level = "CRITICAL"
        elif combined_score >= 0.5:
            level = "HIGH"
        elif combined_score >= 0.2:
            level = "MEDIUM"

        return {
            "is_injection": combined_score >= 0.5,
            "risk_score": round(combined_score, 2),
            "level": level,
            "findings": all_findings
        }


class CanaryDefense(PromptSecurityDefense):
    """
    Prompt injection & instruction exfiltration defense.
    Maintains compatibility with cryptographic canary interface.
    """
    @staticmethod
    def generate_token(salt: str = "orion") -> str:
        return PromptSecurityDefense.generate_canary(salt)

    @staticmethod
    def inject(prompt: str, token: str) -> str:
        return PromptSecurityDefense.inject_canary(prompt, token)

    @staticmethod
    def detect_leaks(text: str, tokens: List[str]) -> List[str]:
        return [t for t in tokens if PromptSecurityDefense.check_output_for_leak(text, t)]



# Polyglot AST/Regex Security Signatures for non-Python sources
POLYGLOT_SECURITY_PATTERNS: Dict[Tuple[str, ...], List[Tuple[Any, str, str, str]]] = {
    ('.dart',): [
        (re.compile(r'(?i)\b(?:rawQuery|rawInsert|rawUpdate|rawDelete|execute)\s*\(\s*[\'"][^\'"]*\$'), 'AST_SQL_INJECTION', 'SQL query with direct string interpolation (use parameterized ? arguments)', 'HIGH'),
        (re.compile(r'(?i)badCertificateCallback\s*:\s*\([^)]*\)\s*=>\s*true'), 'AST_INSECURE_NETWORK', 'Unpinned SSL certificate acceptance in HttpClient', 'CRITICAL'),
        (re.compile(r'(?i)Process\.(?:run|start)\s*\([^,]+,\s*\[?[^\]]*\b(?:sh|bash|cmd|powershell)\b'), 'AST_COMMAND_INJECTION', 'Shell command execution via Dart Process API', 'HIGH'),
    ],
    ('.ts', '.js', '.tsx', '.jsx', '.mjs', '.cjs'): [
        (re.compile(r'(?i)(?<![a-zA-Z0-9_.])eval\s*\('), 'AST_DYNAMIC_CODE_EXEC', 'Dynamic code execution via eval()', 'CRITICAL'),
        (re.compile(r'(?i)new\s+Function\s*\('), 'AST_DYNAMIC_CODE_EXEC', 'Dynamic code execution via new Function()', 'HIGH'),
        (re.compile(r'(?i)child_process\.(?:exec|execSync)\s*\('), 'AST_COMMAND_INJECTION', 'Raw shell command execution via child_process.exec()', 'HIGH'),
        (re.compile(r'(?i)\binnerHTML\s*=\s*(?![\'"`]<)'), 'AST_XSS_SINK', 'Dynamic innerHTML assignment without sanitization', 'HIGH'),
    ],
    ('.kt', '.java'): [
        (re.compile(r'(?i)Runtime\.getRuntime\(\)\.exec\s*\('), 'AST_COMMAND_INJECTION', 'Command execution via Runtime.getRuntime().exec()', 'HIGH'),
        (re.compile(r'(?i)ProcessBuilder\s*\([^)]*\b(?:sh|cmd|bash)\b'), 'AST_COMMAND_INJECTION', 'Shell invocation via ProcessBuilder', 'HIGH'),
    ],
    ('.go',): [
        (re.compile(r'(?i)exec\.Command\s*\(\s*"(?:sh|bash|cmd|powershell)"'), 'AST_COMMAND_INJECTION', 'Shell command execution via Go os/exec', 'HIGH'),
    ],
    ('.rs',): [
        (re.compile(r'(?i)\bCommand::new\s*\(\s*"(?:sh|bash|cmd|powershell)"'), 'AST_COMMAND_INJECTION', 'Shell command execution via std::process::Command', 'HIGH'),
        (re.compile(r'(?i)\bunsafe\s*\{'), 'AST_UNSAFE_BLOCK', 'Unsafe Rust block requires explicit safety documentation', 'MEDIUM'),
    ],
    ('.sh', '.bash', '.zsh'): [
        (re.compile(r'(?i)\beval\s+[\'"]?\$'), 'AST_COMMAND_INJECTION', 'Dynamic shell code execution via eval with variable', 'CRITICAL'),
        (re.compile(r'(?i)\b(?:curl|wget)\s+[^|\n]+\|\s*(?:sh|bash|zsh)\b'), 'AST_REMOTE_EXECUTION', 'Insecure pipe from web directly to shell execution', 'CRITICAL'),
        (re.compile(r'(?i)\brm\s+-[rfRf]+\s+/(?:\s|$)'), 'AST_DESTRUCTIVE_ACTION', 'Destructive root filesystem deletion', 'CRITICAL'),
        (re.compile(r'(?i)\brm\s+-[rfRf]+\s+\$(?:\{[A-Z_]+:?-\/\}|[A-Z_]+/)'), 'AST_DESTRUCTIVE_ACTION', 'Unsafe variable deletion with root fallback', 'HIGH'),
        (re.compile(r'(?i)\b(?:bash|sh)\s+-i\s+>&?\s*/dev/tcp/'), 'AST_REVERSE_SHELL', 'Interactive reverse shell over TCP socket', 'CRITICAL'),
        (re.compile(r'(?i)\bchmod\s+(?:-R\s+)?777\b'), 'AST_INSECURE_PERMISSIONS', 'Excessively permissive permissions (777)', 'MEDIUM'),
    ],
    ('.ps1', '.bat', '.cmd'): [
        (re.compile(r'(?i)\b(?:iex|Invoke-Expression)\b'), 'AST_COMMAND_INJECTION', 'Dynamic PowerShell execution via Invoke-Expression', 'CRITICAL'),
        (re.compile(r'(?i)\b(?:DownloadString|DownloadFile)\s*\('), 'AST_REMOTE_EXECUTION', 'Remote download and potential staging execution', 'HIGH'),
        (re.compile(r'(?i)\b(?:rmdir|del)\s+/[sqSQ]+\s+[c-zC-Z]:\\'), 'AST_DESTRUCTIVE_ACTION', 'Destructive root drive deletion', 'CRITICAL'),
        (re.compile(r'(?i)-EncodedCommand\s+[A-Za-z0-9+/=]{20,}'), 'AST_OBFUSCATED_PAYLOAD', 'Encoded/obfuscated command payload execution', 'HIGH'),
    ],
}


class ASTSecurityVisitor(ast.NodeVisitor):
    def __init__(self, filepath: str, lines: List[str]):
        self.filepath = filepath
        self.lines = lines
        self.findings: List[Dict[str, Any]] = []
        self.safe_placeholder_vars: Set[str] = set()
        self.tainted_vars: Set[str] = set()

    def _get_snippet(self, lineno: int) -> str:
        if 1 <= lineno <= len(self.lines):
            return self.lines[lineno - 1].strip()
        return ""

    def _is_expr_tainted(self, expr: ast.AST) -> bool:
        """Recursively checks whether an AST expression is derived from an untrusted source or string interpolation."""
        for sub in ast.walk(expr):
            if isinstance(sub, ast.JoinedStr):
                for val in sub.values:
                    if isinstance(val, ast.FormattedValue) and not (
                        isinstance(val.value, ast.Name) and val.value.id in self.safe_placeholder_vars
                    ):
                        return True
            elif isinstance(sub, ast.BinOp) and isinstance(sub.op, (ast.Add, ast.Mod)):
                if not (isinstance(sub.left, ast.Constant) and isinstance(sub.right, ast.Constant)):
                    return True
            elif isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                if sub.func.attr in ("format", "join"):
                    if not (isinstance(sub.func.value, ast.Name) and sub.func.value.id in self.safe_placeholder_vars):
                        return True
            elif isinstance(sub, ast.Name) and sub.id in self.tainted_vars:
                return True
        return False

    def visit_Assign(self, node: ast.Assign):
        unparsed = ast.unparse(node.value) if hasattr(ast, "unparse") else ""
        if re.fullmatch(r'["\'],\s*["\']\.join\(\s*["\']\?["\'].*\)', unparsed):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    self.safe_placeholder_vars.add(t.id)
        if self._is_expr_tainted(node.value):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id not in self.safe_placeholder_vars:
                    self.tainted_vars.add(t.id)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            name = alias.name.split('.')[0]
            if name in DANGEROUS_IMPORTS:
                self.findings.append({
                    'file': self.filepath,
                    'line': node.lineno,
                    'category': 'AST_DANGEROUS_IMPORT',
                    'severity': 'HIGH',
                    'message': f"Import of high-risk module: '{alias.name}'",
                    'snippet': self._get_snippet(node.lineno)
                })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            mod = node.module.split('.')[0]
            if mod in DANGEROUS_IMPORTS:
                self.findings.append({
                    'file': self.filepath,
                    'line': node.lineno,
                    'category': 'AST_DANGEROUS_IMPORT',
                    'severity': 'HIGH',
                    'message': f"Import from high-risk module: '{node.module}'",
                    'snippet': self._get_snippet(node.lineno)
                })
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        # Detect os.environ['AWS_SECRET_ACCESS_KEY']
        if isinstance(node.value, ast.Attribute):
            val = node.value
            if isinstance(val.value, ast.Name) and val.value.id == 'os' and val.attr == 'environ':
                key = None
                if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                    key = node.slice.value
                if key and key in SENSITIVE_ENV_KEYS:
                    self.findings.append({
                        'file': self.filepath,
                        'line': node.lineno,
                        'category': 'AST_CREDENTIAL_HARVESTING',
                        'severity': 'HIGH',
                        'message': f"Suspicious credential access via os.environ['{key}']",
                        'snippet': self._get_snippet(node.lineno)
                    })
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Direct function calls: eval(), exec(), etc.
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in DANGEROUS_CALLS:
                sev, msg = DANGEROUS_CALLS[func_name]
                self.findings.append({
                    'file': self.filepath,
                    'line': node.lineno,
                    'category': 'AST_DANGEROUS_CALL',
                    'severity': sev,
                    'message': msg,
                    'snippet': self._get_snippet(node.lineno)
                })

            # Check getattr sink reflection: getattr(os, "system"), getattr(builtins, "exec"), etc.
            elif func_name == 'getattr':
                if len(node.args) >= 2:
                    if isinstance(node.args[0], ast.Name) and node.args[0].id in ('__builtins__', 'builtins'):
                        self.findings.append({
                            'file': self.filepath,
                            'line': node.lineno,
                            'category': 'AST_DYNAMIC_OBFUSCATION',
                            'severity': 'HIGH',
                            'message': "Dynamic reflection bypass via getattr(__builtins__, ...)",
                            'snippet': self._get_snippet(node.lineno)
                        })
                    if isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
                        sink_name = node.args[1].value
                        if sink_name in {'exec', 'eval', 'system', 'popen', '__import__', 'spawnl', 'posix_spawn'}:
                            self.findings.append({
                                'file': self.filepath,
                                'line': node.lineno,
                                'category': 'AST_DYNAMIC_OBFUSCATION',
                                'severity': 'HIGH',
                                'message': f"Reflective access to dangerous execution sink '{sink_name}' via getattr()",
                                'snippet': self._get_snippet(node.lineno)
                            })

            elif func_name == 'open':
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    path_str = node.args[0].value
                    if '../' in path_str or '..\\' in path_str:
                        self.findings.append({
                            'file': self.filepath,
                            'line': node.lineno,
                            'category': 'AST_PATH_TRAVERSAL',
                            'severity': 'HIGH',
                            'message': f"Potential path traversal via unvalidated relative path '../' (CWE-22)",
                            'snippet': self._get_snippet(node.lineno)
                        })

        # Method calls: os.system(), subprocess.run(shell=True), etc.
        elif isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            val = node.func.value

            # hashlib.md5 / hashlib.sha1 (CWE-327)
            if isinstance(val, ast.Name) and val.id == 'hashlib' and attr in ('md5', 'sha1'):
                self.findings.append({
                    'file': self.filepath,
                    'line': node.lineno,
                    'category': 'AST_BROKEN_CRYPTO',
                    'severity': 'HIGH',
                    'message': f"Use of broken cryptographic hash function: hashlib.{attr}() (CWE-327)",
                    'snippet': self._get_snippet(node.lineno)
                })

            # cursor.execute SQL injection via dynamic string formatting (CWE-89)
            if attr in ('execute', 'executescript', 'executemany') and node.args:
                arg0 = node.args[0]
                sql_re = re.compile(r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|REPLACE)\b', re.IGNORECASE)
                is_dynamic_sql = False
                if isinstance(arg0, ast.JoinedStr):
                    raw_sql = "".join(p.value for p in arg0.values if isinstance(p, ast.Constant) and isinstance(p.value, str))
                    if sql_re.search(raw_sql):
                        for part in arg0.values:
                            if isinstance(part, ast.FormattedValue):
                                unparsed = ast.unparse(part.value) if hasattr(ast, "unparse") else ""
                                if not re.fullmatch(r'["\'],\s*["\']\.join\(\s*["\']\?["\'].*\)', unparsed) and not (isinstance(part.value, ast.Name) and part.value.id in self.safe_placeholder_vars):
                                    is_dynamic_sql = True
                                    break
                elif isinstance(arg0, ast.BinOp) and isinstance(arg0.op, (ast.Add, ast.Mod)):
                    unparsed = ast.unparse(arg0) if hasattr(ast, "unparse") else ""
                    if sql_re.search(unparsed):
                        is_dynamic_sql = True
                elif isinstance(arg0, ast.Call) and isinstance(arg0.func, ast.Attribute) and arg0.func.attr == 'format':
                    unparsed = ast.unparse(arg0.func.value) if hasattr(ast, "unparse") else ""
                    if sql_re.search(unparsed):
                        is_dynamic_sql = True

                if is_dynamic_sql:
                    self.findings.append({
                        'file': self.filepath,
                        'line': node.lineno,
                        'category': 'AST_SQL_INJECTION',
                        'severity': 'CRITICAL',
                        'message': f"SQL injection risk via dynamic string formatting in {attr}() (CWE-89)",
                        'snippet': self._get_snippet(node.lineno)
                    })

            # os calls
            if isinstance(val, ast.Name) and val.id == 'os':
                if attr in ('system', 'popen', 'spawnl', 'spawnle', 'spawnlp', 'spawnlpe', 'spawnv', 'spawnve', 'spawnvp', 'spawnvpe', 'posix_spawn', 'posix_spawnp', 'execl', 'execle', 'execlp', 'execlpe', 'execv', 'execve', 'execvp', 'execvpe'):
                    self.findings.append({
                        'file': self.filepath,
                        'line': node.lineno,
                        'category': 'AST_COMMAND_INJECTION',
                        'severity': 'HIGH',
                        'message': f"Raw shell execution via os.{attr}()",
                        'snippet': self._get_snippet(node.lineno)
                    })
                elif attr == 'getenv':
                    if node.args and isinstance(node.args[0], ast.Constant) and str(node.args[0].value) in SENSITIVE_ENV_KEYS:
                        key = str(node.args[0].value)
                        self.findings.append({
                            'file': self.filepath,
                            'line': node.lineno,
                            'category': 'AST_CREDENTIAL_HARVESTING',
                            'severity': 'HIGH',
                            'message': f"Probing sensitive credential via os.getenv('{key}')",
                            'snippet': self._get_snippet(node.lineno)
                        })

            # os.environ.get calls
            if isinstance(val, ast.Attribute):
                if isinstance(val.value, ast.Name) and val.value.id == 'os' and val.attr == 'environ':
                    if attr == 'get':
                        if node.args and isinstance(node.args[0], ast.Constant) and str(node.args[0].value) in SENSITIVE_ENV_KEYS:
                            key = str(node.args[0].value)
                            self.findings.append({
                                'file': self.filepath,
                                'line': node.lineno,
                                'category': 'AST_CREDENTIAL_HARVESTING',
                                'severity': 'HIGH',
                                'message': f"Probing sensitive credential via os.environ.get('{key}')",
                                'snippet': self._get_snippet(node.lineno)
                            })

            # subprocess calls with shell=True
            if isinstance(val, ast.Name) and val.id == 'subprocess':
                if attr in ('run', 'Popen', 'call', 'check_call', 'check_output', 'getoutput', 'getstatusoutput'):
                    for kw in node.keywords:
                        if kw.arg == 'shell':
                            if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                self.findings.append({
                                    'file': self.filepath,
                                    'line': node.lineno,
                                    'category': 'AST_COMMAND_INJECTION',
                                    'severity': 'HIGH',
                                    'message': f"subprocess.{attr}() called with shell=True",
                                    'snippet': self._get_snippet(node.lineno)
                                })

            # pty.spawn calls
            if isinstance(val, ast.Name) and val.id == 'pty' and attr == 'spawn':
                self.findings.append({
                    'file': self.filepath,
                    'line': node.lineno,
                    'category': 'AST_COMMAND_INJECTION',
                    'severity': 'HIGH',
                    'message': f"Interactive shell spawn via pty.{attr}()",
                    'snippet': self._get_snippet(node.lineno)
                })

            # Dynamic importlib calls
            if isinstance(val, ast.Name) and val.id == 'importlib':
                if attr == 'import_module':
                    self.findings.append({
                        'file': self.filepath,
                        'line': node.lineno,
                        'category': 'AST_DYNAMIC_IMPORT',
                        'severity': 'MEDIUM',
                        'message': "Dynamic module loading via importlib.import_module()",
                        'snippet': self._get_snippet(node.lineno)
                    })

            # Raw socket instantiation
            if isinstance(val, ast.Name) and val.id == 'socket':
                if attr == 'socket':
                    self.findings.append({
                        'file': self.filepath,
                        'line': node.lineno,
                        'category': 'AST_NETWORK_SOCKET',
                        'severity': 'MEDIUM',
                        'message': "Raw network socket creation via socket.socket()",
                        'snippet': self._get_snippet(node.lineno)
                    })

            # Insecure deserialization sinks
            if isinstance(val, ast.Name):
                mod_name = val.id
                if mod_name in DANGEROUS_DESERIALIZATION_SINKS and attr in DANGEROUS_DESERIALIZATION_SINKS[mod_name]:
                    self.findings.append({
                        'file': self.filepath,
                        'line': node.lineno,
                        'category': 'AST_INSECURE_DESERIALIZATION',
                        'severity': 'HIGH',
                        'message': f"Insecure deserialization of untrusted data via {mod_name}.{attr}()",
                        'snippet': self._get_snippet(node.lineno)
                    })
                elif mod_name == 'yaml' and attr == 'load':
                    has_safe_loader = False
                    for kw in node.keywords:
                        if kw.arg == 'Loader':
                            if (isinstance(kw.value, ast.Name) and kw.value.id in SAFE_YAML_LOADERS) or \
                               (isinstance(kw.value, ast.Attribute) and kw.value.attr in SAFE_YAML_LOADERS):
                                has_safe_loader = True
                    if not has_safe_loader:
                        self.findings.append({
                            'file': self.filepath,
                            'line': node.lineno,
                            'category': 'AST_INSECURE_DESERIALIZATION',
                            'severity': 'MEDIUM',
                            'message': "Insecure yaml.load() call without explicit SafeLoader",
                            'snippet': self._get_snippet(node.lineno)
                        })

            # Destructive file removal
            if isinstance(val, ast.Name) and val.id == 'shutil':
                if attr in ('rmtree',):
                    self.findings.append({
                        'file': self.filepath,
                        'line': node.lineno,
                        'category': 'AST_DESTRUCTIVE_FS',
                        'severity': 'HIGH',
                        'message': f"Recursive directory deletion via shutil.{attr}()",
                        'snippet': self._get_snippet(node.lineno)
                    })

            # Builtin dynamic reflection bypass
            if isinstance(val, ast.Name) and val.id in ('builtins', '__builtins__'):
                if attr in ('eval', 'exec', '__import__'):
                    self.findings.append({
                        'file': self.filepath,
                        'line': node.lineno,
                        'category': 'AST_DANGEROUS_CALL',
                        'severity': 'CRITICAL',
                        'message': f"Obfuscated dynamic execution via builtins.{attr}",
                        'snippet': self._get_snippet(node.lineno)
                    })

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # 1. Bare except: catches system exit/interrupts and masks fatal runtime failures
        if node.type is None:
            self.findings.append({
                'file': self.filepath,
                'line': node.lineno,
                'category': 'AST_BARE_EXCEPT',
                'severity': 'HIGH',
                'message': "Bare 'except:' handler detected. Catches system exit and masks fatal runtime failures.",
                'snippet': self._get_snippet(node.lineno)
            })
        elif isinstance(node.type, ast.Name) and node.type.id in ('BaseException',):
            self.findings.append({
                'file': self.filepath,
                'line': node.lineno,
                'category': 'AST_BARE_EXCEPT',
                'severity': 'HIGH',
                'message': "Broad 'except BaseException:' handler detected. Catches system exit and masks fatal runtime failures.",
                'snippet': self._get_snippet(node.lineno)
            })

        # 2. Silent exception swallow with only pass, no-op constant, or dead assignment
        if len(node.body) == 1:
            is_pass = isinstance(node.body[0], ast.Pass)
            is_noop = isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, (ast.Constant,))
            is_dead_assign = isinstance(node.body[0], ast.Assign) and all(
                isinstance(t, ast.Name) and t.id.startswith(('_ignored', '_err')) for t in node.body[0].targets
            )
            if is_pass or is_noop or is_dead_assign:
                is_broad = node.type is None or (isinstance(node.type, ast.Name) and node.type.id in ('Exception', 'BaseException'))
                if is_broad:
                    prev_snippet = self._get_snippet(node.lineno - 1) if node.lineno > 1 else ""
                    curr_snippet = self._get_snippet(node.lineno)
                    if "reconfigure" not in prev_snippet and "reconfigure" not in curr_snippet:
                        self.findings.append({
                            'file': self.filepath,
                            'line': node.lineno,
                            'category': 'AST_SILENT_EXCEPTION_SWALLOW',
                            'severity': 'LOW',
                            'message': "Broad exception swallowed with silent 'pass' or dead assignment without logging or telemetry",
                            'snippet': self._get_snippet(node.lineno)
                        })
        self.generic_visit(node)


SecurityASTVisitor = ASTSecurityVisitor


def scan_unicode_trojan(filepath: str) -> List[str]:
    """
    Scans a single file for Unicode Trojan Source (BiDi overrides) and hidden/zero-width formatting characters.
    Pure Python standard library implementation.
    """
    violations: List[str] = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for lineno, line in enumerate(f, 1):
                if line.isascii():
                    continue
                for idx, ch in enumerate(line):
                    codepoint = ord(ch)
                    if codepoint < 128:
                        continue
                    # BiDi override characters and isolates (U+202A - U+202E, U+2066 - U+2069)
                    if (0x202A <= codepoint <= 0x202E) or (0x2066 <= codepoint <= 0x2069) or ch in BIDI_CHARS:
                        desc = BIDI_CHARS.get(ch, "BiDi control char")
                        violations.append(f"{filepath}:{lineno}: BiDi Trojan override {desc} (U+{codepoint:04X})")
                    # Zero-width / hidden formatting characters (Category Cf)
                    elif (unicodedata.category(ch) == 'Cf' and ch not in ('\t', '\n', '\r')) or ch in ZERO_WIDTH_CHARS:
                        if ch in ('\u200c', '\u200d'):
                            if 0 < idx < len(line) - 1:
                                prev_cat = unicodedata.category(line[idx - 1])
                                next_cat = unicodedata.category(line[idx + 1])
                                if prev_cat in ('So', 'Sk', 'Cn', 'Cs') or next_cat in ('So', 'Sk', 'Cn', 'Cs') or ord(line[idx - 1]) > 0x1F000 or ord(line[idx + 1]) > 0x1F000:
                                    continue
                        desc = ZERO_WIDTH_CHARS.get(ch, "Hidden formatting char")
                        violations.append(f"{filepath}:{lineno}: Hidden/Trojan formatting char {desc} (U+{codepoint:04X})")
    except Exception as e:
        violations.append(f"{filepath}:1: Error reading file: {e}")
    return violations



class SecurityBaseline:
    def __init__(self, baseline_path: str):
        self.baseline_path = baseline_path
        self.suppressed_hashes: Set[str] = set()
        self.suppression_rules: List[Dict[str, str]] = []
        self.load()

    @staticmethod
    def compute_fingerprint(rel_path: str, category: str, snippet: str) -> str:
        norm_snippet = re.sub(r'\s+', ' ', snippet.strip())
        key = f"{rel_path.replace(os.sep, '/')}:{category}:{norm_snippet}"
        return hashlib.sha256(key.encode('utf-8')).hexdigest()

    def load(self):
        if os.path.exists(self.baseline_path):
            try:
                import fnmatch
                with open(self.baseline_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.suppressed_hashes = set(data.get('fingerprints', []) + data.get('suppressed_fingerprints', []))
                    self.suppression_rules = data.get('rules', [])
            except Exception:
                self.suppressed_hashes = set()
                self.suppression_rules = []

    def is_suppressed(self, rel_path: str, category: str, fingerprint: str) -> bool:
        if fingerprint in self.suppressed_hashes:
            return True
        import fnmatch
        norm_path = rel_path.replace(os.sep, '/')
        for r in self.suppression_rules:
            pattern = r.get('path', '*')
            cat = r.get('category') or r.get('id', '*')
            if (cat == '*' or cat == category or fnmatch.fnmatch(category, cat)) and fnmatch.fnmatch(norm_path, pattern):
                return True
        return False

    def save(self, findings: List[Dict[str, Any]], root_dir: str):
        new_hashes = set(self.suppressed_hashes)
        for item in findings:
            rel = os.path.relpath(item['file'], root_dir).replace(os.sep, '/')
            fp = self.compute_fingerprint(rel, item['category'], item.get('snippet', ''))
            new_hashes.add(fp)

        atomic_write_text(self.baseline_path, json.dumps({
            'version': 1,
            'rules': self.suppression_rules,
            'fingerprints': sorted(list(new_hashes)),
            'total_count': len(new_hashes)
        }, indent=2))


class SecurityAuditor:
    def __init__(self, root_dir: str, baseline_file: Optional[str] = None):
        self.root_dir = os.path.abspath(root_dir)
        curr = self.root_dir if os.path.isdir(self.root_dir) else os.path.dirname(self.root_dir)
        workspace_root = curr
        while curr and curr != os.path.dirname(curr):
            if os.path.isdir(os.path.join(curr, '.agents')):
                workspace_root = curr
                break
            if os.path.basename(curr) == '.agents':
                workspace_root = os.path.dirname(curr)
                break
            curr = os.path.dirname(curr)
        self.workspace_root = workspace_root

        if baseline_file:
            self.baseline_path = baseline_file
        else:
            candidates = [
                os.path.join(self.workspace_root, '.agents', '.security-baseline.json'),
                os.path.join(self.workspace_root, '.security-baseline.json'),
                os.path.join(self.root_dir, '.agents', '.security-baseline.json'),
                os.path.join(self.root_dir, '.security-baseline.json'),
                os.path.join(os.path.dirname(self.root_dir), '.security-baseline.json'),
                os.path.join(os.path.dirname(self.root_dir), '.agents', '.security-baseline.json')
            ]
            self.baseline_path = candidates[0]
            for cand in candidates:
                if os.path.exists(cand):
                    self.baseline_path = cand
                    break
        self.baseline = SecurityBaseline(self.baseline_path)

    def scan_file(self, filepath: str) -> List[Dict[str, Any]]:
        findings = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            return [{
                'file': filepath,
                'line': 1,
                'category': 'READ_ERROR',
                'severity': 'MEDIUM',
                'message': f"Could not read file: {e}",
                'snippet': ''
            }]

        rel_path = os.path.relpath(filepath, self.root_dir).replace(os.sep, '/')

        # 1. Unicode Trojan Source & Zero-Width Scan
        for line_num, line in enumerate(lines, 1):
            if line.isascii():
                continue
            for idx, char in enumerate(line):
                codepoint = ord(char)
                if codepoint < 128:
                    continue
                if (0x202A <= codepoint <= 0x202E) or (0x2066 <= codepoint <= 0x2069) or char in BIDI_CHARS:
                    desc = BIDI_CHARS.get(char, "BiDi control char")
                    findings.append({
                        'file': filepath,
                        'line': line_num,
                        'category': 'UNICODE_TROJAN_SOURCE',
                        'severity': 'CRITICAL',
                        'message': f"Bidirectional control character detected: {desc} (U+{codepoint:04X})",
                        'snippet': line.strip()
                    })
                elif (unicodedata.category(char) == 'Cf' and char not in ('\t', '\n', '\r')) or char in ZERO_WIDTH_CHARS:
                    # Ignore ZWJ/ZWNJ when part of legitimate emoji or cursive script
                    if char in ('\u200c', '\u200d'):
                        # Check surrounding characters for emoji/pictographs
                        is_emoji_zwj = False
                        if 0 < idx < len(line) - 1:
                            prev_cat = unicodedata.category(line[idx - 1])
                            next_cat = unicodedata.category(line[idx + 1])
                            if prev_cat in ('So', 'Sk', 'Cn', 'Cs') or next_cat in ('So', 'Sk', 'Cn', 'Cs') or ord(line[idx - 1]) > 0x1F000 or ord(line[idx + 1]) > 0x1F000:
                                is_emoji_zwj = True
                        if is_emoji_zwj:
                            continue
                    desc = ZERO_WIDTH_CHARS.get(char, "Hidden formatting char")
                    findings.append({
                        'file': filepath,
                        'line': line_num,
                        'category': 'UNICODE_ZERO_WIDTH',
                        'severity': 'HIGH',
                        'message': f"Hidden zero-width character detected: {desc} (U+{codepoint:04X})",
                        'snippet': line.strip()
                    })

        # 2. Prompt Injection & Escape Scan (Markdown, Text, Prompts)
        if filepath.endswith(('.md', '.txt', '.prompt', '.json', '.yaml', '.yml')):
            for pattern, cat, msg, sev in SUSPICIOUS_PROMPT_PATTERNS:
                if pattern.search(content):
                    for line_num, line in enumerate(lines, 1):
                        if pattern.search(line):
                            findings.append({
                                'file': filepath,
                                'line': line_num,
                                'category': cat,
                                'severity': sev,
                                'message': msg,
                                'snippet': line.strip()
                            })

        # 3. Python AST Vulnerability Scan
        if filepath.endswith('.py'):
            try:
                tree = ast.parse(content, filename=filepath)
                visitor = ASTSecurityVisitor(filepath, lines)
                visitor.visit(tree)
                findings.extend(visitor.findings)
            except SyntaxError:
                pass  # Ignore template files or incomplete snippets

        # 4. Polyglot Source Code Vulnerability Scan (Dart, TS, JS, Kotlin, Java, Go, Rust)
        ext = os.path.splitext(filepath)[1].lower()
        for exts, patterns in POLYGLOT_SECURITY_PATTERNS.items():
            if ext in exts:
                for pattern, cat, msg, sev in patterns:
                    if pattern.search(content):
                        for line_num, line in enumerate(lines, 1):
                            if pattern.search(line):
                                findings.append({
                                    'file': filepath,
                                    'line': line_num,
                                    'category': cat,
                                    'severity': sev,
                                    'message': msg,
                                    'snippet': line.strip()
                                })

        return findings

    def audit_directory(self, target_dir: Optional[str] = None, exclude_dirs: Optional[Set[str]] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        if target_dir is None:
            target_dir = self.root_dir

        if exclude_dirs is None:
            exclude_dirs = {'.git', '.orion', 'node_modules', '__pycache__', '.system_generated', 'scratch', '.scratch', '.worktrees', '.venv', 'venv', 'build', 'dist', 'teamwork', 'tests', 'archive'}

        all_active: List[Dict[str, Any]] = []
        all_suppressed: List[Dict[str, Any]] = []

        valid_exts = ('.py', '.md', '.json', '.yaml', '.yml', '.txt', '.js', '.ts', '.tsx', '.jsx', '.dart', '.kt', '.java', '.go', '.rs', '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd')

        def _process_finding(item: Dict[str, Any]) -> None:
            rel_ws = os.path.relpath(item['file'], self.workspace_root).replace(os.sep, '/')
            rel_root = os.path.relpath(item['file'], self.root_dir).replace(os.sep, '/')
            rel_stripped = rel_ws[8:] if rel_ws.startswith('.agents/') else rel_ws
            fp_ws = self.baseline.compute_fingerprint(rel_ws, item['category'], item.get('snippet', ''))
            fp_root = self.baseline.compute_fingerprint(rel_root, item['category'], item.get('snippet', ''))
            fp_stripped = self.baseline.compute_fingerprint(rel_stripped, item['category'], item.get('snippet', ''))
            if (self.baseline.is_suppressed(rel_ws, item['category'], fp_ws) or
                self.baseline.is_suppressed(rel_root, item['category'], fp_root) or
                self.baseline.is_suppressed(rel_stripped, item['category'], fp_stripped)):
                all_suppressed.append(item)
            else:
                all_active.append(item)

        if os.path.isfile(target_dir):
            for item in self.scan_file(target_dir):
                _process_finding(item)
            return all_active, all_suppressed

        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.git')]
            for file in files:
                if file.endswith(valid_exts):
                    fp = os.path.join(root, file)
                    file_findings = self.scan_file(fp)
                    for item in file_findings:
                        _process_finding(item)

        # Run ast-grep polyglot scan if available
        sg_findings = run_ast_grep_scan(target_dir)
        for item in sg_findings:
            _process_finding(item)

        return all_active, all_suppressed


LANGUAGE_ALIAS_MAP = {
    "py": "python",
    "python": "python",
    "ts": "typescript",
    "typescript": "typescript",
    "tsx": "typescript",
    "js": "javascript",
    "javascript": "javascript",
    "jsx": "javascript",
    "dart": "dart",
    "kt": "kotlin",
    "kotlin": "kotlin",
    "rs": "rust",
    "rust": "rust",
    "java": "java",
    "go": "go",
    "golang": "go"
}

SEVERITY_ALIAS_MAP = {
    "error": "error",
    "err": "error",
    "warning": "warning",
    "warn": "warning",
    "info": "info",
    "information": "info"
}


class AstRuleCompiler:
    """
    Pillar 2: Declarative Structural AST Rule Compiler.
    Compiles declarative pattern rules into ast-grep YAML format without external dependencies.
    """

    @classmethod
    def normalize_language(cls, lang: Union[str, List[str]]) -> str:
        if isinstance(lang, list):
            target = lang[0] if lang else "python"
        else:
            target = lang
        clean = str(target).strip().lower()
        return LANGUAGE_ALIAS_MAP.get(clean, clean)

    @classmethod
    def normalize_severity(cls, sev: str) -> str:
        clean = str(sev).strip().lower()
        return SEVERITY_ALIAS_MAP.get(clean, "error")

    @classmethod
    def compile_rule_dict(cls, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        if isinstance(data, list):
            raw_rules = data
        elif isinstance(data, dict):
            raw_rules = data.get("rules", [data])
        else:
            return []

        compiled_docs: List[Dict[str, Any]] = []

        for rule in raw_rules:
            rule_id = rule.get("id", "unnamed-rule")
            raw_lang = rule.get("languages", rule.get("language", "python"))
            norm_lang = cls.normalize_language(raw_lang)
            norm_sev = cls.normalize_severity(rule.get("severity", "error"))
            msg = rule.get("message", "")

            rule_body: Dict[str, Any] = {}

            if "pattern" in rule:
                rule_body = {"pattern": rule["pattern"]}
            elif "pattern-either" in rule:
                either_items = []
                for p in rule["pattern-either"]:
                    pat_str = p.get("pattern", p) if isinstance(p, dict) else p
                    either_items.append({"pattern": pat_str})
                rule_body = {"any": either_items}
            elif "patterns" in rule:
                all_items = []
                for p in rule["patterns"]:
                    if not isinstance(p, dict):
                        all_items.append({"pattern": str(p)})
                    elif "pattern" in p:
                        all_items.append({"pattern": p["pattern"]})
                    elif "pattern-not" in p:
                        all_items.append({"not": {"pattern": p["pattern-not"]}})
                    elif "pattern-inside" in p:
                        all_items.append({"inside": {"pattern": p["pattern-inside"]}})
                    elif "pattern-either" in p:
                        sub_either = []
                        for sub in p["pattern-either"]:
                            pat_val = sub.get("pattern", sub) if isinstance(sub, dict) else sub
                            sub_either.append({"pattern": pat_val})
                        all_items.append({"any": sub_either})
                rule_body = {"all": all_items}
            elif "pattern-inside" in rule:
                rule_body = {"inside": {"pattern": rule["pattern-inside"]}}
            elif "pattern-not" in rule:
                rule_body = {"not": {"pattern": rule["pattern-not"]}}
            else:
                rule_body = {"pattern": ""}

            doc: Dict[str, Any] = {
                "id": rule_id,
                "language": norm_lang,
                "rule": rule_body,
                "message": msg,
                "severity": norm_sev
            }

            if "fix" in rule:
                doc["fix"] = rule["fix"]

            compiled_docs.append(doc)

        return compiled_docs

    @classmethod
    def _dump_yaml_node(cls, obj: Any, indent_level: int = 0) -> str:
        indent = "  " * indent_level
        lines = []

        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{indent}{k}:")
                    lines.append(cls._dump_yaml_node(v, indent_level + 1))
                elif isinstance(v, str) and ("\n" in v or ":" in v or '"' in v):
                    if "\n" in v:
                        lines.append(f"{indent}{k}: |")
                        for subline in v.splitlines():
                            lines.append(f"{indent}  {subline}")
                    else:
                        lines.append(f'{indent}{k}: "{v}"')
                else:
                    lines.append(f"{indent}{k}: {v}")
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    first = True
                    for k, v in item.items():
                        prefix = f"{indent}- " if first else f"{indent}  "
                        first = False
                        if isinstance(v, (dict, list)):
                            lines.append(f"{prefix}{k}:")
                            lines.append(cls._dump_yaml_node(v, indent_level + 2))
                        elif isinstance(v, str) and "\n" in v:
                            lines.append(f"{prefix}{k}: |")
                            for subline in v.splitlines():
                                lines.append(f"{indent}    {subline}")
                        else:
                            lines.append(f"{prefix}{k}: {v}")
                else:
                    lines.append(f"{indent}- {item}")

        return "\n".join(lines)

    @classmethod
    def to_yaml(cls, docs: List[Dict[str, Any]]) -> str:
        yaml_chunks = []
        for d in docs:
            yaml_chunks.append(cls._dump_yaml_node(d, indent_level=0))
        return "\n---\n".join(yaml_chunks) + "\n"

    @classmethod
    def parse_semgrep_string(cls, content: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        trimmed = content.strip()
        if trimmed.startswith("{") or trimmed.startswith("["):
            try:
                return json.loads(trimmed)
            except Exception as _e:
                _log_telemetry(_e, "parse_semgrep_json")

        rule_blocks = re.split(r'\n---\s*\n', trimmed)
        rules = []
        for block in rule_blocks:
            if not block.strip():
                continue
            r: Dict[str, Any] = {}
            for line in block.splitlines():
                m = re.match(r'^\s*([a-zA-Z0-9_\-]+)\s*:\s*(.*?)\s*$', line)
                if m:
                    k, v = m.group(1), m.group(2).strip()
                    if v.startswith('"') and v.endswith('"'):
                        v = v[1:-1]
                    elif v.startswith("'") and v.endswith("'"):
                        v = v[1:-1]
                    r[k] = v
            if r:
                rules.append(r)
        return {"rules": rules}

    @classmethod
    def compile_file(cls, input_path: str, output_path: Optional[str] = None) -> str:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        parsed = cls.parse_semgrep_string(content)
        compiled_docs = cls.compile_rule_dict(parsed)
        yaml_out = cls.to_yaml(compiled_docs)

        if output_path:
            atomic_write_text(output_path, yaml_out)

        return yaml_out


SemgrepToAstGrepCompiler = AstRuleCompiler


def main():
    import argparse

    # Route ast-grep rule compilation if triggered
    raw_args = sys.argv[1:]
    if raw_args and (raw_args[0] in ["compile_ast", "ast_rules", "-i", "--input"] or "-i" in raw_args or "--input" in raw_args):
        c_parser = argparse.ArgumentParser(description="Declarative-to-ast-grep Rule Compiler")
        c_parser.add_argument("cmd", nargs="?", default="", help="Optional command token")
        c_parser.add_argument("-i", "--input", required=True, help="Path to declarative rule file")
        c_parser.add_argument("-o", "--output", help="Output path for compiled ast-grep YAML")
        c_parser.add_argument("--json", action="store_true", help="Print compiled rules as JSON")
        c_args = c_parser.parse_args(raw_args)

        compiler = AstRuleCompiler()
        try:
            yaml_result = compiler.compile_file(c_args.input, c_args.output)
            if c_args.json:
                parsed = compiler.parse_semgrep_string(open(c_args.input, "r", encoding="utf-8").read())
                compiled = compiler.compile_rule_dict(parsed)
                print(json.dumps(compiled, indent=2))
            else:
                if not c_args.output:
                    print(yaml_result)
                else:
                    print(f"[OK] Compiled ast-grep rule saved to: {c_args.output}")
            sys.exit(0)
        except Exception as e:
            sys.stderr.write(f"Compilation error: {e}\n")
            sys.exit(1)

    parser = argparse.ArgumentParser(description="Native Security & Polyglot AST Integrity Engine")
    parser.add_argument("dir", nargs="?", default=".", help="Directory to audit (default: .)")
    parser.add_argument("--baseline", help="Custom baseline file path")
    parser.add_argument("--record-baseline", action="store_true", help="Save active findings to baseline file")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--canary-probe", help="Verify if response text leaks prompt canary tokens")
    args = parser.parse_args()

    if args.canary_probe:
        content = args.canary_probe
        if os.path.isfile(args.canary_probe):
            with open(args.canary_probe, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        tokens = re.findall(r'CANARY_[a-f0-9]{16}', content)
        leaks = CanaryDefense.detect_leaks(content, tokens)
        if leaks:
            print(f"[CRITICAL] Canary leak detected! Found tokens: {leaks}")
            sys.exit(1)
        else:
            print("[PASS] Zero canary token leaks detected.")
            sys.exit(0)

    target_dir = os.path.abspath(args.dir)
    auditor = SecurityAuditor(target_dir, baseline_file=args.baseline)
    active, suppressed = auditor.audit_directory()

    if args.record_baseline:
        auditor.baseline.save(active, auditor.root_dir)
        print(f"[BASELINE] Recorded {len(active)} findings to {auditor.baseline_path}")
        sys.exit(0)

    sg_bin = find_ast_grep()
    sg_status = f"ast-grep binary active ({sg_bin})" if sg_bin else "ast-grep optional binary absent (using native AST/regex engine)"

    if args.json:
        print(json.dumps({
            "target": target_dir,
            "engine": sg_status,
            "active_findings": active,
            "suppressed_count": len(suppressed),
            "verdict": "REJECT" if any(f.get('severity') == 'CRITICAL' for f in active) else ("CAUTION" if active else "APPROVE")
        }, indent=2))
        sys.exit(1 if active else 0)

    print(f"\n🛡️ Security & Integrity Audit: {target_dir}")
    print("=" * 60)
    print(f"Engine          : {sg_status}")
    print(f"Active Findings : {len(active)}")
    print(f"Suppressed      : {len(suppressed)} baselined items\n")

    if active:
        for idx, item in enumerate(active, 1):
            sev = item.get('severity', 'HIGH')
            print(f"[{idx}] [{sev}] {item.get('category')}: {item.get('message')}")
            print(f"     File: {item.get('file')}:{item.get('line', '?')}")
            if item.get('snippet'):
                print(f"     Code: {item.get('snippet')}")
        print("\n[FAIL] Security violations detected.")
        sys.exit(1)
    else:
        print("[PASS] Security & Polyglot AST Integrity Verified: 0 vulnerabilities found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
