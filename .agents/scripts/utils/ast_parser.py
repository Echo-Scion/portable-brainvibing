import os
import ast
import re
import subprocess

def parse_python_ast(content: str) -> str:
    """Parses Python file content using the built-in ast module."""
    try:
        tree = ast.parse(content)
        result = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node)
                doc_str = f" - {doc.split(chr(10))[0]}" if doc else ""
                methods = []
                for child in node.body:
                    if isinstance(child, ast.FunctionDef) or isinstance(child, ast.AsyncFunctionDef):
                        methods.append(child.name)
                method_str = ", ".join(methods) if methods else "None"
                result.append(f"Class: {node.name}{doc_str}\n  Methods: {method_str}")
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                doc = ast.get_docstring(node)
                doc_str = f" - {doc.split(chr(10))[0]}" if doc else ""
                result.append(f"Function: {node.name}{doc_str}")
        
        if not result:
            return "No structural elements found (classes/functions)."
            
        return "\n".join(result)
    except SyntaxError:
        return "[AST PARSE ERROR: Invalid Python Syntax]"
    except Exception as e:
        return f"[AST PARSE ERROR: {str(e)}]"

def parse_regex_ast(content: str) -> str:
    """Fallback Regex heuristic parser for Dart, JS, TS, Java, etc."""
    result = []
    
    # Class matching: e.g., "class MyClass", "export class MyClass", "class MyClass extends Widget"
    class_pattern = re.compile(r'^\s*(?:export\s+)?(?:abstract\s+)?class\s+([A-Za-z0-9_]+)', re.MULTILINE)
    
    # Simple method/function matching: "void myFunc(", "Future<void> myFunc(", "const myFunc = ("
    # This is a very rough heuristic to catch function signatures
    func_pattern = re.compile(r'^\s*(?:export\s+)?(?:async\s+)?(?:[\w<>,\[\]]+\s+)?([A-Za-z0-9_]+)\s*\([^)]*\)\s*(?:{|=>)', re.MULTILINE)
    
    classes = class_pattern.findall(content)
    if classes:
        result.append("Classes found: " + ", ".join(classes))
        
    functions = func_pattern.findall(content)
    # Filter out common control structures that look like functions
    keywords = {"if", "switch", "for", "while", "catch", "return", "super", "this"}
    functions = [f for f in functions if f not in keywords]
    
    # De-duplicate while preserving order
    seen = set()
    funcs_dedup = []
    for f in functions:
        if f not in seen:
            seen.add(f)
            funcs_dedup.append(f)
            
    if funcs_dedup:
        result.append("Functions/Methods found: " + ", ".join(funcs_dedup[:30])) # Limit to 30 to avoid bloat
        if len(funcs_dedup) > 30:
            result.append(f"... and {len(funcs_dedup) - 30} more.")
            
    if not result:
        return "No structural elements found via Regex heuristics."
        
    return "\n".join(result)

def generate_ast_summary(filepath: str, content: str) -> str:
    """
    Attempts to parse the content into a lightweight AST summary.
    Uses 'rtk read --level aggressive' as the primary engine.
    Falls back to native Python ast or regex if RTK is unavailable.
    """
    header = f"--- AST Summary for {os.path.basename(filepath)} ---\n"
    
    # 1. Try RTK first (Primary Engine)
    try:
        # RTK returns the hollowed AST on stdout
        result = subprocess.run(
            ['rtk', 'read', filepath, '--level', 'aggressive'], 
            capture_output=True, 
            text=True, 
            check=True
        )
        if result.stdout.strip():
            # If rtk outputs its own hook warnings, we might want to filter them,
            # but usually they print to stderr.
            return header + result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass # Fallback to python/regex

    # 2. Graceful Fallback (Native Python ast or Regex)
    _, ext = os.path.splitext(filepath.lower())
    
    if ext == ".py":
        return header + parse_python_ast(content)
    elif ext in [".dart", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".go", ".rs"]:
        return header + parse_regex_ast(content)
    else:
        # Return None to indicate no AST mapping applies
        return None
