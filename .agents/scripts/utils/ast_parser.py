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

def parse_treesitter_ast(filepath: str, content: str) -> str:
    """Attempts to parse using tree-sitter, falls back to regex."""
    _, ext = os.path.splitext(filepath.lower())
    
    try:
        import tree_sitter
        
        # Determine language module based on extension
        lang_module = None
        if ext == '.js':
            import tree_sitter_javascript
            lang_module = tree_sitter_javascript.language()
        elif ext == '.ts':
            import tree_sitter_typescript
            lang_module = tree_sitter_typescript.language_typescript()
        elif ext == '.tsx':
            import tree_sitter_typescript
            lang_module = tree_sitter_typescript.language_tsx()
        elif ext == '.dart':
            try:
                import tree_sitter_dart
                lang_module = tree_sitter_dart.language()
            except ImportError:
                pass
                
        if not lang_module:
            return parse_regex_ast(content)
            
        parser = tree_sitter.Parser()
        # API differs between v0.21 and v0.22+ - handle gracefully
        try:
            parser.set_language(tree_sitter.Language(lang_module))
        except TypeError:
            parser.set_language(lang_module)
        
        tree = parser.parse(bytes(content, "utf8"))
        
        classes = []
        functions = []
        
        def traverse(node):
            if node.type in ['class_declaration', 'class']:
                for child in node.children:
                    if child.type == 'identifier':
                        classes.append(child.text.decode('utf8'))
                        break
            elif node.type in ['function_declaration', 'function', 'method_definition', 'arrow_function']:
                for child in node.children:
                    if child.type in ['identifier', 'property_identifier']:
                        functions.append(child.text.decode('utf8'))
                        break
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        
        result = []
        if classes:
            result.append("Classes found: " + ", ".join(classes))
        if functions:
            # Filter keywords
            keywords = {"if", "switch", "for", "while", "catch", "return", "super", "this"}
            funcs = [f for f in functions if f not in keywords]
            result.append("Functions/Methods found: " + ", ".join(funcs[:30]))
            if len(funcs) > 30:
                result.append(f"... and {len(funcs) - 30} more.")
                
        if not result:
            return "No structural elements found via Tree-sitter."
        return "
".join(result)
        
    except ImportError:
        # tree_sitter or language binding not installed
        return parse_regex_ast(content)
    except Exception as e:
        print(f"[AST WARNING] Tree-sitter failed: {e}. Falling back to Regex.")
        return parse_regex_ast(content)

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
    elif ext in [".dart", ".js", ".ts", ".tsx"]:
        return header + parse_treesitter_ast(filepath, content)
    elif ext in [".java", ".cpp", ".c", ".h", ".go", ".rs"]:
        return header + parse_regex_ast(content)
    else:
        # Return None to indicate no AST mapping applies
        return None
